import os
import boto3
import json
import requests
from jose import jwt

response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}


def handler(event):
    print(os.environ.get("SIGNING_URL"))
    print(os.environ.get("USER_POOL_ID"))
    print(event)

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

    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        issuer=signing_url,
        # subject=os.environ.get("USER_POOL_ID")
    )

    print(payload)

    response["statusCode"] = 200
    response["body"] = json.dumps({"message": "hey"})
    return response
