from jose import jwt
import requests
import os
import boto3
import json


response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}


def handler(event, context):
    if "Authorization" not in event["headers"]:
        response["statusCode"] = 401
        response["body"] = json.dumps({"message": "not authorized"})
        return response

    token = event["headers"]["Authorization"]
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

    response["statusCode"] = 200
    response["body"] = json.dumps({"message": "hey"})
    return response
