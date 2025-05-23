import os
import json
import boto3
import base64
from jose import jwt
from datetime import timedelta, datetime, timezone

response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}


def handler(event, context):
    try:
        if "origin" in event["headers"]:
            response["headers"]["Access-Control-Allow-Origin"] = event["headers"]["origin"]
        response["headers"]["Access-Control-Allow-Credentials"] = "true"
        cognito = boto3.client("cognito-idp")
        route_key = "%s %s" % (event["httpMethod"], event['resource'])

        match route_key:
            case "POST /auth/client":
                allowed_creds = json.loads(base64.b64decode(
                    os.environ.get("CLIENT_CREDS")).decode("utf-8"))
                creds = base64.b64decode(event["headers"]["Authorization"].split(" ")[
                                         1]).decode("utf-8").split(":")
                client_id, client_secret = creds[0], creds[1]

                if allowed_creds[client_id] == client_secret:
                    now = datetime.now(timezone.utc)
                    expires = now + timedelta(minutes=10)
                    jwt_payload = {"sub": "m2m-api", "client_id": client_id, "aud": event["resource"],
                                   "iat": now, "exp": expires}
                    token = jwt.encode(
                        jwt_payload, os.environ.get("TOKEN_KEY"))
                    response["statusCode"] = 200
                    response["body"] = json.dumps({"token": token})
                else:
                    raise Exception("invalid credentials")

            case "GET /auth/merchant":
                if "cookie" not in event["headers"]:
                    raise Exception("please log in again")

                token = event["headers"]["cookie"].split("=")[1]
                cognito_response = cognito.get_user(AccessToken=token)
                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"user": cognito_response["Username"]})

            case "POST /auth/sign-in":
                if event["body"] != None:
                    body = json.loads(event["body"])
                else:
                    raise Exception("there was no body in request")

                params = {
                    "AuthFlow": "USER_PASSWORD_AUTH",
                    "ClientId": os.environ.get('USER_POOL_ID'),
                    "AuthParameters": {
                        "USERNAME": body["username"],
                        "PASSWORD": body["password"]
                    }
                }
                cognito_response = cognito.initiate_auth(**params)

                if cognito_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    token = cognito_response["AuthenticationResult"]["AccessToken"]
                    token_string = "token=%s; SameSite=None; Secure; Path=/" % token
                    response["headers"]["Set-Cookie"] = token_string
                    response["statusCode"] = 200
                    response["body"] = json.dumps({"message": "welcome"})
                else:
                    raise Exception("there was an error signing in.")
            case _:
                raise Exception("no matching resource")

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(error)
        error_message = "an error occurred."

        match error.__class__.__name__:
            case "NotAuthorizedException":
                error_message = "invalid username or password"
            case "Exception":
                error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
