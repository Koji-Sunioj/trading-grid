import os
import hmac
import json
import boto3
import hashlib
import requests
import traceback
from jose import jwt
from decimal import Decimal


def serialize_float(obj):
    return float(obj)


def check_hmac(payload, client_hmac):
    correct_hmac = hmac.digest(os.environ.get(
        "TOKEN_KEY").encode(), payload.encode(), digest=hashlib.sha256).hex()
    if not hmac.compare_digest(client_hmac, correct_hmac):
        raise Exception("invalid credentials")


response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}


def handler(event, context):
    try:
        route_key = "%s %s" % (event["httpMethod"], event['resource'])

        match route_key:
            case "GET /purchase-orders/merchant":
                if "cookie" not in event["headers"]:
                    raise Exception("please sign in")

                cognito = boto3.client("cognito-idp")
                token = event["headers"]["cookie"].split("=")[1]
                cognito.get_user(AccessToken=token)

                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(os.environ.get("PO_TABLE"))
                ddb_response = table.scan()

                sort_by = event["queryStringParameters"]["sort"] if "sort" in event["queryStringParameters"] else "modified"
                order_by = event["queryStringParameters"]["order"] if "order" in event["queryStringParameters"] else "asc"
                desc = order_by == "desc"

                if sort_by == "line_count":
                    ddb_response["Items"].sort(
                        key=lambda x: len(x["data"]), reverse=desc)
                else:
                    ddb_response["Items"].sort(
                        key=lambda x: x[sort_by], reverse=desc)

                response["headers"]["Access-Control-Allow-Origin"] = event["headers"]["origin"]
                response["headers"]["Access-Control-Allow-Credentials"] = "true"
                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"orders": ddb_response["Items"]}, default=serialize_float)

            case "GET /purchase-orders/merchant/{purchase_order_id}":
                if "cookie" not in event["headers"]:
                    raise Exception("please sign in")

                cognito = boto3.client("cognito-idp")
                token = event["headers"]["cookie"].split("=")[1]
                cognito.get_user(AccessToken=token)

                response["statusCode"] = 200
                response["body"] = json.dumps({"hello": "man"})

            case "PUT /purchase-orders/client":
                if "Authorization" not in event["headers"]:
                    raise Exception("no authoriziation")

                if event["body"] != None:
                    check_hmac(event["body"], event["headers"]
                               ["Authorization"])
                else:
                    raise Exception("no body in request")

                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(os.environ.get("PO_TABLE"))
                ddb_body = json.loads(event["body"], parse_float=Decimal)
                ddb_response = table.put_item(Item=ddb_body)

                if ddb_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                    raise Exception(
                        "there was an error creating that purchase order")

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "purchase order %s received" % ddb_body["purchase_order_id"]})

            case _:
                raise Exception("no matching resource")

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())
        error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
