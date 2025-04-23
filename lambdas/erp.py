from jose import jwt
import requests
import os
import boto3
import json


response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}


def handler(event, context):
    try:
        if "Authorization" not in event["headers"]:
            raise Exception("no authoriziation")

        token = event["headers"]["Authorization"]
        signing_url = os.environ.get("SIGNING_URL")
        kids = requests.get(
            signing_url + "/.well-known/jwks.json").json()["keys"]
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

        body = json.loads(event["body"])
        print(body)

        response["statusCode"] = 200
        response["body"] = json.dumps({"message": "hey"})

    except Exception as error:
        print("error name %s" + error.__class__.__name__)
        print(error)
        print(error.__str__())
        error_message = "an error occurred."

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
