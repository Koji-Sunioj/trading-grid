import os
import json
import boto3
import requests
from jose import jwt
from decimal import Decimal


response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}


def check_M2M_token(authoriziation_value):
    token = authoriziation_value
    signing_url = os.environ.get("SIGNING_URL")
    kids = requests.get(signing_url + "/.well-known/jwks.json").json()["keys"]
    token_header = jwt.get_unverified_header(token)
    rsa_key = [header for header in kids if header["kid"]
               == token_header["kid"]][0]
    jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        issuer=signing_url,
        subject=os.environ.get("M2M_POOL_ID")
    )


def handler(event, context):
    try:
        if "Authorization" not in event["headers"]:
            raise Exception("no authoriziation")

        check_M2M_token(event["headers"]["Authorization"])

        body = None

        if event["body"] != None:
            body = json.loads(event["body"], parse_float=Decimal)
            body["amendments"] = []

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get("TABLE_NAME"))

        ddb_response = table.get_item(
            Key={'purchase_order_id': int(body["purchase_order_id"])})

        if "Item" in ddb_response:
            raise Exception("that purchase order already exists")

        ddb_response = table.put_item(
            TableName=os.environ.get("TABLE_NAME"),
            Item=body,
        )

        if ddb_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception("there was an error creating that purchase order")

        response["statusCode"] = 200
        response["body"] = json.dumps(
            {"message": "purchase order %s received" % body["purchase_order_id"]})

    except Exception as error:
        print("error name %s" + error.__class__.__name__)
        print(error)
        print(error.__str__())
        error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
