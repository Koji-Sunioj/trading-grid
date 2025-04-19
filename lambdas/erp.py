import os
import boto3
import json

response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}


def handler(event, context):
    print(event)
    # response["headers"]["Access-Control-Allow-Origin"] = event["headers"]["origin"]
    response["statusCode"] = 200
    response["body"] = json.dumps({"message": "hey"})
    return response
