import os
import json
import boto3
import requests
from jose import jwt
from decimal import Decimal


def serialize_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)


def check_token(token):
    jwt.decode(token, key=os.environ.get("TOKEN_KEY"), audience="/auth/client")


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

                response["headers"]["Access-Control-Allow-Origin"] = event["headers"]["origin"]
                response["headers"]["Access-Control-Allow-Credentials"] = "true"
                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"orders": ddb_response["Items"]}, default=serialize_float)

            case "PUT /purchase-orders/client":
                if "Authorization" not in event["headers"]:
                    raise Exception("no authoriziation")

                response["body"] = json.dumps({"message": "hell"})
                check_token(event["headers"]["Authorization"])
                body = None

                if event["body"] != None:
                    body = json.loads(event["body"], parse_float=Decimal)

                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(os.environ.get("PO_TABLE"))

                ddb_response = table.put_item(Item=body)

                if ddb_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                    raise Exception(
                        "there was an error creating that purchase order")

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"message": "purchase order %s received" % body["purchase_order_id"]})
            case _:
                raise Exception("no matching resource")

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(error.__str__())
        error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
