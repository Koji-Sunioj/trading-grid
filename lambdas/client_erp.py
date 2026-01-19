import os
import json
import boto3
import traceback

from utils import check_hmac, get_dispatch, search

from functools import wraps
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
po_table = dynamodb.Table(os.environ.get("PO_TABLE"))
routing_table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
dispatch_table = dynamodb.Table(os.environ.get("DISPATCH_TABLE"))
ammendments_table = dynamodb.Table(
    os.environ.get("PO_AMMENDMENT_TABLE"))


def validate(function):
    @wraps(function)
    def lambda_request(*args):
        event = args[0]

        route_key = "%s %s" % (event["httpMethod"], event['resource'])
        response = {}
        response['headers'] = {"Access-Control-Allow-Methods": "*"}

        if event["httpMethod"] in ["POST", "PUT"] and event["body"] == None:
            response["statusCode"] = 400
            response["body"] = json.dumps({"message": "no body in request"})
            return response

        invalid_client = "/client" in event['resource'] and "Authorization" not in event["headers"]

        if invalid_client:
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

            case _:
                raise Exception("no matching resource")

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())
        error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
