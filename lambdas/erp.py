import os
import hmac
import uuid
import math
import json
import boto3
import hashlib
import datetime
import requests
import traceback

from functools import wraps
from zoneinfo import ZoneInfo
from decimal import Decimal, Context
from datetime import datetime, timezone, timedelta, date
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
po_table = dynamodb.Table(os.environ.get("PO_TABLE"))
routing_table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
dispatch_table = dynamodb.Table(os.environ.get("DISPATCH_TABLE"))
ammendments_table = dynamodb.Table(
    os.environ.get("PO_AMMENDMENT_TABLE"))


def serialize_float(obj):
    return float(obj)


def check_hmac(payload, request_hmac, hmac_key):
    correct_hmac = hmac.digest(hmac_key.encode(
    ), payload.encode(), digest=hashlib.sha256).hex()
    if not hmac.compare_digest(request_hmac, correct_hmac):
        raise Exception("invalid credentials")


def search(dicts, key, value):
    try:
        return next(n for n in dicts if n[key] == value)
    except:
        return None


def get_dispatch(items, client):
    lat, long = client["coords"]["latitude"], client["coords"]["longitude"]

    distance_lookup = requests.get("https://api.radar.io/v1/route/distance?origin=%s&destination=%s,%s&modes=car&units=metric" % (
        os.environ.get("STORE_COORDS"), lat, long), headers={"Authorization": os.environ.get("TOKEN_KEY")})

    freight = distance_lookup.json()["routes"]["car"]
    kilometers, minutes = int(
        freight["distance"]["value"] / 1000), int(round(freight["duration"]["value"]))
    weight_grams = 100 * \
        int(items)
    volume = (14.2 * 12.5 * 1.0) / 5000 * \
        float(items)
    cost = round(kilometers * volume * 1.25, 2)

    today = date.today()
    current_slot = datetime(year=today.year, month=today.month, day=today.day,
                            hour=12, minute=0, tzinfo=ZoneInfo("Europe/Helsinki"))
    n_days = 7 if current_slot.weekday() >= 2 else 2

    dispatch_slot = current_slot + \
        timedelta(days=n_days - current_slot.weekday())
    estimated_delivery = dispatch_slot + \
        timedelta(minutes=math.ceil(minutes / 10) * 10)

    return {"freight_cost": cost, "estimated_delivery": estimated_delivery.strftime("%Y-%m-%d %H:%M"), "weight_grams": weight_grams}


def validate(function):
    @wraps(function)
    def lambda_request(*args):
        event = args[0]

        route_key = "%s %s" % (event["httpMethod"], event['resource'])
        response = {}
        response['headers'] = {"Access-Control-Allow-Methods": "*"}

        if "/merchant" in event['resource']:
            cognito = boto3.client("cognito-idp")
            token = event["headers"]["cookie"].split("=")[1]
            cognito.get_user(AccessToken=token)
            response["headers"]["Access-Control-Allow-Origin"] = event["headers"]["origin"]
            response["headers"]["Access-Control-Allow-Credentials"] = "true"

        if event["httpMethod"] in ["POST", "PUT"] and event["body"] == None:
            response["statusCode"] = 400
            response["body"] = json.dumps({"message": "no body in request"})
            return response

        invalid_client = "/client" in event['resource'] and "Authorization" not in event["headers"]
        invalid_merchant = "/merchant" in event['resource'] and "cookie" not in event["headers"]

        if invalid_client or invalid_merchant:
            response["statusCode"] = 401
            response["body"] = json.dumps({"message": "invalid credentials"})
            return response

        return function(*args, route_key, response)
    return lambda_request


@validate
def handler(event, context, route_key, response):
    try:
        clients = routing_table.scan()["Items"]

        match route_key:
            case "GET /merchant/routing-table":
                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"clients": clients}, default=serialize_float)

            case "POST /merchant/routing-table":
                payload = json.loads(event["body"])

                address_lookup = requests.get(
                    "https://api.radar.io/v1/geocode/forward?query=%s" % payload["address"], headers={"Authorization": os.environ.get("TOKEN_KEY")})

                if address_lookup.status_code != 200:
                    raise Exception("address is not valid")

                address_response = address_lookup.json()
                lat, long = address_response["addresses"][0]["latitude"], address_response["addresses"][0]["longitude"]
                decimal_prec = Context(prec=6)
                payload["coords"] = {"latitude": decimal_prec.create_decimal_from_float(
                    lat), "longitude": decimal_prec.create_decimal_from_float(long)}

                routing_table.put_item(Item=payload)

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "client created successfully"})

            case "DELETE /merchant/routing-table/{client_id}":
                routing_table.delete_item(
                    Key={"client_id": event["pathParameters"]["client_id"]})

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "item successfully deleted"})

            case "GET /merchant/purchase-orders":
                sort_by = event["queryStringParameters"]["sort"] if "sort" in event["queryStringParameters"] else "modified"
                order_by = event["queryStringParameters"]["order"] if "order" in event["queryStringParameters"] else "asc"
                client_id = event["queryStringParameters"]["client_id"] if "client_id" in event["queryStringParameters"] else ""
                desc = order_by == "desc"

                purchase_orders = po_table.scan(
                    FilterExpression=Attr("client_id").contains(client_id))["Items"]

                if sort_by == "line_count":
                    purchase_orders.sort(
                        key=lambda x: len(x["data"]), reverse=desc)
                else:
                    purchase_orders.sort(
                        key=lambda x: x[sort_by], reverse=desc)

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"orders": purchase_orders}, default=serialize_float)

            case "GET /merchant/purchase-orders/{client_id}/{purchase_order_id}":
                po_key = {"purchase_order_id":  int(
                    event["pathParameters"]["purchase_order_id"]), "client_id":  event["pathParameters"]["client_id"]}

                purchase_order = po_table.get_item(Key=po_key)["Item"]
                purchase_order_lines = ammendments_table.get_item(Key=po_key)

                if "Item" in purchase_order_lines:
                    for line_index, line in enumerate(purchase_order["data"]):
                        confirmed_line = search(
                            purchase_order_lines["Item"]["lines"], "line", line["line"])
                        if confirmed_line != None:
                            purchase_order["data"][line_index]["confirmed"] = confirmed_line["confirmed"]

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"purchase_order": purchase_order}, default=serialize_float)

            case "PUT /client/purchase-orders":
                payload = json.loads(event["body"], parse_float=Decimal)
                client = search(clients, "client_id", payload["client_id"])
                check_hmac(event["body"], event["headers"]
                           ["Authorization"], client["hmac"])

                items = 0

                for line in payload["data"]:
                    items += line["quantity"]

                freight = get_dispatch(items, client)

                if freight["estimated_delivery"] != payload["estimated_delivery"] or round(freight["freight_cost"], 2) != round(float(payload["dispatch_cost"]), 2):
                    raise Exception("cost provided by customer not matching")

                po_key = {
                    "purchase_order_id": payload["purchase_order_id"], "client_id": payload["client_id"]}

                current_po = po_table.get_item(Key=po_key)

                if "Item" in current_po and current_po["Item"]["status"] != "pending-buyer":
                    raise Exception(
                        "please check the status of your purchase order before sending.")

                elif "Item" not in current_po:
                    other_client_pos = po_table.scan(
                        FilterExpression=Attr("status").eq(
                            "pending-supplier") & Attr("client_id").eq(payload["client_id"])
                    )
                    if other_client_pos["Count"] > 0:
                        raise Exception(
                            "a pending order already exists. please complete that first.")

                purchase_order_lines = ammendments_table.get_item(Key=po_key)
                keep_lines = None

                if "Item" in purchase_order_lines:
                    new_albums = [line["album_id"]
                                  for line in payload["data"]]
                    keep_lines = [line for line in purchase_order_lines["Item"]["lines"] if int(
                        line["album_id"]) in new_albums]

                    for n, line in enumerate(keep_lines):
                        album = search(
                            payload["data"], "album_id", int(line["album_id"]))
                        if album != None:
                            keep_lines[n]["line"] = Decimal(album["line"])

                if keep_lines != None and len(keep_lines) > 0:
                    purchase_order_lines["Item"]["lines"] = keep_lines
                    ammendments_table.put_item(
                        Item=purchase_order_lines["Item"])

                elif keep_lines != None and len(keep_lines) == 0:
                    ammendments_table.delete_item(
                        Key={"purchase_order_id": payload["purchase_order_id"], "client_id": payload["client_id"]})

                new_po = po_table.put_item(Item=payload)

                if new_po["ResponseMetadata"]["HTTPStatusCode"] != 200:
                    raise Exception(
                        "there was an error creating that purchase order")

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "purchase order %s received" % payload["purchase_order_id"]})

            case "POST /merchant/purchase-orders/{client_id}/{purchase_order_id}":
                purchase_order_id, client_id = int(
                    event["pathParameters"]["purchase_order_id"]), event["pathParameters"]["client_id"]

                purchase_order = po_table.get_item(
                    Key={"purchase_order_id": purchase_order_id, "client_id": client_id})["Item"]

                if purchase_order["status"] == "confirmed":
                    raise Exception("this purchase order is completed")

                payload = json.loads(event["body"])
                ammendments_table.put_item(Item=payload)

                confirmed_lines = []
                for ammendment, po_line in zip(payload["lines"], purchase_order["data"]):
                    confirmed_lines.append(ammendment["line"] == int(
                        po_line["line"]) and ammendment["confirmed"] == int(po_line["quantity"]))

                status = "confirmed" if all(
                    confirmed_lines) else "pending-buyer"
                new_modified = datetime.now(
                    timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

                purchase_order["status"] = status
                purchase_order["modified"] = new_modified
                payload["status"] = status
                payload["modified"] = new_modified
                po_table.put_item(Item=purchase_order)

                client = search(clients, "client_id", client_id)

                return_payload = json.dumps(payload)
                hmac_hex = hmac.digest(client["hmac"].encode(), str(
                    return_payload).encode(), digest=hashlib.sha256).hex()
                headers = {"Authorization": hmac_hex}

                client_response = requests.post(
                    client["callback"]+"/api/merchant/purchase-orders", data=return_payload, headers=headers)

                if client_response.status_code != 200:
                    raise Exception(
                        "there was an error returning an order response to the client")

                dispatch_uuid = str(uuid.uuid4())

                dispatch_item = {"dispatch_id": dispatch_uuid, "purchase_order": purchase_order_id,
                                 "status": "pending-supplier", "address": client["address"], "client_id": client_id, "estimated_delivery": purchase_order["estimated_delivery"]}
                dispatch_table.put_item(Item=dispatch_item)
                dispatch_payload = json.dumps(dispatch_item)

                hmac_hex = hmac.digest(client["hmac"].encode(), str(
                    dispatch_payload).encode(), digest=hashlib.sha256).hex()
                headers = {"Authorization": hmac_hex}

                dispatch_request = requests.post(
                    client["callback"] + "/api/merchant/shipment-orders", data=dispatch_payload, headers=headers)

                if dispatch_request.status_code != 200:
                    raise Exception(
                        "there was an error returning a dispatch order to the client")

                message = "purchase order %s received at client with order status %s" % (
                    purchase_order_id, status)
                response["statusCode"] = 200
                response["body"] = json.dumps({"message": message})

            case "GET /client/dispatch-cost":
                client = search(clients, "client_id",
                                event["queryStringParameters"]["client_id"])
                check_hmac(str(event["queryStringParameters"]),
                           event["headers"]["Authorization"], client["hmac"])

                freight = get_dispatch(
                    event["queryStringParameters"]["items"], client)

                response["statusCode"] = 200
                response["body"] = json.dumps(freight)

            case "PATCH /client/dispatches/{dispatch_id}":
                payload = json.loads(event["body"])
                dispatch_id = event["pathParameters"]["dispatch_id"]

                client = search(clients, "client_id", payload["client_id"])
                check_hmac(event["body"], event["headers"]
                           ["Authorization"], client["hmac"])

                dispatch_item = dispatch_table.get_item(
                    Key={"dispatch_id": dispatch_id})["Item"]

                if dispatch_item["status"] != "shipped":
                    raise Exception(
                        "dispatch item %s must be in shipped status to update" % dispatch_id)

                dispatch_item["status"] = payload["status"]
                dispatch_table.put_item(Item=dispatch_item)

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "dispatch item %s updated successfully" % dispatch_id})

            case "GET /merchant/dispatches":
                sort_by = event["queryStringParameters"]["sort"] if "sort" in event["queryStringParameters"] else "estimated_delivery"
                order_by = event["queryStringParameters"]["order"] if "order" in event["queryStringParameters"] else "asc"
                client_id = event["queryStringParameters"]["client_id"] if "client_id" in event["queryStringParameters"] else ""
                desc = order_by == "desc"

                dispatches = dispatch_table.scan(
                    FilterExpression=Attr("client_id").contains(client_id))["Items"]
                dispatches.sort(
                    key=lambda x: x[sort_by], reverse=desc)

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"dispatches": dispatches}, default=serialize_float)

            case "GET /merchant/dispatches/{dispatch_id}":
                dispatch_id = event["pathParameters"]["dispatch_id"]
                dispatch_item = dispatch_table.get_item(
                    Key={"dispatch_id": dispatch_id})["Item"]

                current_delivery_date = datetime.strptime(
                    dispatch_item["estimated_delivery"], "%Y-%m-%d %H:%M")
                now = datetime.now()
                dispatch_object = {"dispatch": dispatch_item}

                if now > current_delivery_date:
                    purchase_order = po_table.get_item(
                        Key={"client_id": dispatch_item["client_id"], "purchase_order_id": dispatch_item["purchase_order"]})
                    items = sum([line["quantity"]
                                for line in purchase_order["data"]])
                    client = search(clients, "client_id",
                                    dispatch_item["client_id"])
                    new_delivery_date = get_dispatch(items, client)[
                        "estimated_delivery"]
                    dispatch_object["dispatch"]["new_delivery_date"] = new_delivery_date

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    dispatch_object, default=serialize_float)

            case "POST /merchant/dispatches/{dispatch_id}":
                dispatch_id = event["pathParameters"]["dispatch_id"]
                payload = json.loads(event["body"])

                client = search(clients, "client_id", payload["client_id"])

                return_payload = json.dumps(
                    {"status": payload["status"], "estimated_delivery": payload["estimated_delivery"]})
                hmac_hex = hmac.digest(client["hmac"].encode(), str(
                    return_payload).encode(), digest=hashlib.sha256).hex()
                headers = {"Authorization": hmac_hex}

                dispatch_update = requests.patch(
                    client["callback"]+"/api/merchant/shipment-orders/%s" % dispatch_id, headers=headers, data=return_payload)

                if dispatch_update.status_code != 200:
                    raise Exception(
                        "there was an error returning a dispatch order to the client")

                dispatch_item = dispatch_table.get_item(
                    Key={"dispatch_id": dispatch_id})["Item"]

                if dispatch_item["estimated_delivery"] != payload["estimated_delivery"]:
                    dispatch_item["estimated_delivery"] = payload["estimated_delivery"]

                    purchase_order = po_table.get_item(
                        Key={"client_id": payload["client_id"], "purchase_order_id": dispatch_item["purchase_order"]})["Item"]
                    purchase_order["estimated_delivery"] = payload["estimated_delivery"]
                    purchase_order["modified"] = datetime.now(
                        timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

                    po_table.put_item(Item=purchase_order)

                dispatch_item["status"] = payload["status"] = payload["status"]
                dispatch_table.put_item(Item=dispatch_item)

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "dispatch %s updated at the clients server" % dispatch_id}, default=serialize_float)

            case _:
                raise Exception("no matching resource")

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())
        error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
