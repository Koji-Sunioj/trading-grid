import os
import json
import boto3
import requests
from jose import jwt
from decimal import Decimal


response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}


def check_token(token):
    jwt.decode(token, key=os.environ.get("TOKEN_KEY"), audience="/auth/client")


def handler(event, context):
    try:
        if "Authorization" not in event["headers"]:
            raise Exception("no authoriziation")

        route_key = "%s %s" % (event["httpMethod"], event['resource'])

        match route_key:
            case "PUT /purchase-orders":
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
