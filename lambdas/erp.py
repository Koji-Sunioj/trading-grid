import os
import hmac
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
clients = dynamodb.Table(os.environ.get("ROUTING_TABLE")).scan()["Items"]


def serialize_float(obj):
    return float(obj)


def check_hmac(payload, client_hmac, client_id):
    client = search(clients, "client_id", client_id)
    correct_hmac = hmac.digest(client["hmac"].encode(
    ), payload.encode(), digest=hashlib.sha256).hex()
    if not hmac.compare_digest(client_hmac, correct_hmac):
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
    estimated_delivery = dispatch_slot + timedelta(minutes=minutes)

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

        return function(*args, route_key, response, clients)
    return lambda_request


@validate
def handler(event, context, route_key, response, clients):
    try:
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

                routing_table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
                routing_table.put_item(Item=payload)

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "client created successfully"})

            case "DELETE /merchant/routing-table/{client_id}":
                routing_table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
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

                po_table = dynamodb.Table(os.environ.get("PO_TABLE"))
                purchase_orders = po_table.scan(
                    FilterExpression=Attr("client_id").contains(client_id))

                if sort_by == "line_count":
                    purchase_orders["Items"].sort(
                        key=lambda x: len(x["data"]), reverse=desc)
                else:
                    purchase_orders["Items"].sort(
                        key=lambda x: x[sort_by], reverse=desc)

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"orders": purchase_orders["Items"]}, default=serialize_float)

            case "GET /merchant/purchase-orders/{client_id}/{purchase_order_id}":

                po_key = {"purchase_order_id":  int(
                    event["pathParameters"]["purchase_order_id"]), "client_id":  event["pathParameters"]["client_id"]}

                po_table = dynamodb.Table(os.environ.get("PO_TABLE"))
                ammendments_table = dynamodb.Table(
                    os.environ.get("PO_AMMENDMENT_TABLE"))

                purchase_order = po_table.get_item(Key=po_key)
                purchase_order_lines = ammendments_table.get_item(Key=po_key)

                if "Item" in purchase_order_lines:
                    for line_index, line in enumerate(purchase_order["Item"]["data"]):
                        confirmed_line = search(
                            purchase_order_lines["Item"]["lines"], "line", line["line"])
                        if confirmed_line != None:
                            purchase_order["Item"]["data"][line_index]["confirmed"] = confirmed_line["confirmed"]

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"purchase_order": purchase_order["Item"]}, default=serialize_float)

            case "GET /client/dispatch-cost":
                check_hmac(str(event["queryStringParameters"]), event["headers"]
                           ["Authorization"], event["queryStringParameters"]["client_id"])
                client = search(clients, "client_id",
                                event["queryStringParameters"]["client_id"])

                freight = get_dispatch(
                    event["queryStringParameters"]["items"], client)

                response["statusCode"] = 200
                response["body"] = json.dumps(freight)

            case "PUT /client/purchase-orders":
                payload = json.loads(event["body"], parse_float=Decimal)
                check_hmac(event["body"], event["headers"]
                           ["Authorization"], payload["client_id"])
                client = search(clients, "client_id",
                                payload["client_id"])
                items = 0

                for line in payload["data"]:
                    items += line["quantity"]

                freight = get_dispatch(items, client)

                if freight["estimated_delivery"] != payload["estimated_delivery"] or round(freight["freight_cost"], 2) != round(float(payload["dispatch_cost"]), 2):
                    raise Exception("cost provided by customer not matching")

                po_key = {
                    "purchase_order_id": payload["purchase_order_id"], "client_id": payload["client_id"]}

                po_table = dynamodb.Table(os.environ.get("PO_TABLE"))
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

                ammendments_table = dynamodb.Table(
                    os.environ.get("PO_AMMENDMENT_TABLE"))
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

                po_table = dynamodb.Table(os.environ.get("PO_TABLE"))
                purchase_order = po_table.get_item(
                    Key={"purchase_order_id": purchase_order_id, "client_id": client_id})

                if purchase_order["Item"]["status"] == "confirmed":
                    raise Exception("this purchase order is completed")

                body = json.loads(event["body"])
                ammendments_table = dynamodb.Table(
                    os.environ.get("PO_AMMENDMENT_TABLE"))
                ammendments_table.put_item(Item=body)

                confirmed_lines = []
                for ammendment, po_line in zip(body["lines"], purchase_order["Item"]["data"]):
                    confirmed_lines.append(ammendment["line"] == int(
                        po_line["line"]) and ammendment["confirmed"] == int(po_line["quantity"]))

                status = "confirmed" if all(
                    confirmed_lines) else "pending-buyer"
                new_modified = datetime.now(
                    timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

                purchase_order["Item"]["status"] = status
                purchase_order["Item"]["modified"] = new_modified
                body["status"] = status
                body["modified"] = new_modified
                po_table.put_item(Item=purchase_order["Item"])

                routing_table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
                routing = routing_table.get_item(Key={"client_id": client_id})

                return_payload = json.dumps(body)
                hmac_hex = hmac.digest(routing["Item"]["hmac"].encode(), str(
                    return_payload).encode(), digest=hashlib.sha256).hex()
                headers = {"Authorization": hmac_hex}

                client_response = requests.post(
                    routing["Item"]["callback"]+"/api/purchase-orders/merchant-response", data=return_payload, headers=headers)

                if client_response.status_code != 200:
                    response["statusCode"] = 400
                    response["body"] = json.dumps(
                        {"message": "error on client's server"})
                else:
                    response["statusCode"] = 200
                    message = "purchase order %s received at client with order status %s" % (
                        purchase_order_id, status)
                    response["body"] = json.dumps({"message": message})
            case _:
                raise Exception("no matching resource")

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())
        error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
