import os
import json
import boto3
import datetime
import traceback

from models import User
from utils import webssocket_token, NoCookieException

response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}
dynamodb = boto3.resource('dynamodb')
ws_token_table = dynamodb.Table(os.environ.get("WS_TOKEN_TABLE"))

def handler(event, context):
    try:
        host = event["headers"]["Referer"]
        if "Origin" in event["headers"]:
            response["headers"]["Access-Control-Allow-Origin"] = event["headers"]["Origin"]
            host = event["headers"]["Origin"]

        response["headers"]["Access-Control-Allow-Credentials"] = "true"
        cognito = boto3.client("cognito-idp")
        route_key = "%s %s" % (event["httpMethod"], event['resource'])

        match route_key:
            case "GET /auth":
                if "Cookie" not in event["headers"]:
                    raise NoCookieException("please log in again")

                token = event["headers"]["Cookie"].split("=")[1]
                cognito_response = cognito.get_user(AccessToken=token)

                websocket = webssocket_token()
                ws_token_table.put_item(Item={"username": cognito_response["Username"],"token_hash": websocket["ws_token_hash"], "issued": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"from":host})

                response["statusCode"] = 200
                response["body"] = json.dumps(
                    {"user": cognito_response["Username"],"ws_token":str(websocket["ws_token"])})

            case "POST /auth":
                if event["body"] != None:
                    body = json.loads(event["body"])
                    User.model_validate(body)
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
                    websocket = webssocket_token()
                    ws_token_table.put_item(Item={"username": body["username"],"token_hash": websocket["ws_token_hash"], "issued": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"from":event["headers"]["Origin"]})

                    token = cognito_response["AuthenticationResult"]["AccessToken"]
                    token_string = "token=%s; SameSite=None; Secure; Path=/" % token

                    response["headers"]["Set-Cookie"] = token_string
                    response["statusCode"] = 200
                    response["body"] = json.dumps({"message": "welcome","ws_token":str(websocket["ws_token"])})

                else:
                    raise Exception("there was an error signing in.")
            case _:
                raise Exception("no matching resource")

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())
        error_message = "an error occurred."
        response['statusCode'] = 400

        match error.__class__.__name__:
            case "NotAuthorizedException" | "UserNotFoundException" | "NoCookieException":
                error_message = "invalid credentials"
                response['statusCode'] = 401
            case "Exception":
                error_message = error.__str__()
            case "ValidationError":
                error_message = "server payload did not match schema for the requested resource"    

        response["body"] = json.dumps({"message": error_message})

    return response
