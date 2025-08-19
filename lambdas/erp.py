import os
import hmac
import json
import boto3
import hashlib
import requests
import traceback
from decimal import Decimal
from functools import wraps
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
clients = table.scan()["Items"]


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
        match route_key:
            case "GET /merchant/purchase-orders":
                table = dynamodb.Table(os.environ.get("PO_TABLE"))
                ddb_response = table.scan()
                print(clients)
                sort_by = event["queryStringParameters"]["sort"] if "sort" in event["queryStringParameters"] else "modified"
                order_by = event["queryStringParameters"]["order"] if "order" in event["queryStringParameters"] else "asc"
                desc = order_by == "desc"

                if sort_by == "line_count":
                    ddb_response["Items"].sort(
                        key=lambda x: len(x["data"]), reverse=desc)
                else:
                    ddb_response["Items"].sort(
                        key=lambda x: x[sort_by], reverse=desc)

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"orders": ddb_response["Items"]}, default=serialize_float)

            case "POST /merchant/routing-table":
                table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
                table.put_item(Item=json.loads(event["body"]))

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "client created successfully"})

            case "GET /merchant/routing-table":
                table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
                ddb_response = table.scan()

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"clients": ddb_response["Items"]}, default=serialize_float)

            case "PUT /client/purchase-orders":
                ddb_body = json.loads(event["body"], parse_float=Decimal)
                check_hmac(event["body"], event["headers"]
                           ["Authorization"], ddb_body["client_id"])

                table = dynamodb.Table(os.environ.get("PO_TABLE"))
                ammendments_table = dynamodb.Table(
                    os.environ.get("PO_AMMENDMENT_TABLE"))

                purchase_order_lines = ammendments_table.get_item(
                    Key={"purchase_order_id": ddb_body["purchase_order_id"], "client_id": ddb_body["client_id"]})
                keep_lines = None

                if "Item" in purchase_order_lines:
                    new_albums = [line["album_id"]
                                  for line in ddb_body["data"]]
                    keep_lines = [line for line in purchase_order_lines["Item"]["lines"] if int(
                        line["album_id"]) in new_albums]

                    for n, line in enumerate(keep_lines):
                        album = search(
                            ddb_body["data"], "album_id", int(line["album_id"]))
                        if album != None:
                            keep_lines[n]["line"] = Decimal(album["line"])

                if keep_lines != None and len(keep_lines) > 0:
                    purchase_order_lines["Item"]["lines"] = keep_lines
                    ammendments_table.put_item(
                        Item=purchase_order_lines["Item"])

                elif keep_lines != None and len(keep_lines) == 0:
                    ammendments_table.delete_item(
                        Key={"purchase_order_id": ddb_body["purchase_order_id"], "client_id": ddb_body["client_id"]})

                ddb_response = table.put_item(Item=ddb_body)

                if ddb_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                    raise Exception(
                        "there was an error creating that purchase order")

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "purchase order %s received" % ddb_body["purchase_order_id"]})

            case "DELETE /merchant/routing-table/{client_id}":
                table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
                table.delete_item(
                    Key={"client_id": event["pathParameters"]["client_id"]})

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "item successfully deleted"})

            case "GET /merchant/purchase-orders/{client_id}/{purchase_order_id}":
                purchase_order_id, client_id = int(
                    event["pathParameters"]["purchase_order_id"]), event["pathParameters"]["client_id"]

                table = dynamodb.Table(os.environ.get("PO_TABLE"))
                ammendments_table = dynamodb.Table(
                    os.environ.get("PO_AMMENDMENT_TABLE"))

                purchase_order_lines = ammendments_table.get_item(
                    Key={"purchase_order_id": purchase_order_id, "client_id": client_id})

                purchase_order = table.get_item(
                    Key={"purchase_order_id": purchase_order_id, "client_id": client_id})

                if "Item" in purchase_order_lines:
                    for line_index, line in enumerate(purchase_order["Item"]["data"]):
                        confirmed_line = search(
                            purchase_order_lines["Item"]["lines"], "line", line["line"])
                        if confirmed_line != None:
                            purchase_order["Item"]["data"][line_index]["confirmed"] = confirmed_line["confirmed"]

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"purchase_order": purchase_order["Item"]}, default=serialize_float)

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
