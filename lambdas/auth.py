import os
import boto3
import json

response = {}
response['headers'] = {"Access-Control-Allow-Methods": "*"}


def get_module(cognito, access_token):

    cognito_response = cognito.get_user(AccessToken=access_token)
    module = [attribute for attribute in cognito_response["UserAttributes"]
              if attribute["Name"] == "custom:erp_module"][0]["Value"]
    return module


def handler(event, context):
    try:
        response["headers"]["Access-Control-Allow-Origin"] = event["headers"]["origin"]
        response["headers"]["Access-Control-Allow-Credentials"] = "true"
        cognito = boto3.client("cognito-idp")
        route_key = "%s %s" % (event["httpMethod"], event['resource'])

        match route_key:
            case "GET /auth/{module}":
                module = event["pathParameters"]["module"]

                if "cookie" not in event["headers"]:
                    raise Exception("please log in again")

                token = event["headers"]["cookie"].split("=")[1]
                user_module = get_module(cognito, token)

                if user_module != module:
                    raise Exception("unauthorized access")

                response["statusCode"] = 200
                response["body"] = json.dumps({"module": user_module})

            case "POST /sign-in":
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
                    user_module = get_module(cognito, token)
                    response["headers"]["Set-Cookie"] = token_string
                    response["statusCode"] = 200
                    response["body"] = json.dumps(
                        {"message": "welcome", "module": user_module})
                else:
                    raise Exception("there was an error signing in.")
            case _:
                raise Exception("no matching resource")

    except Exception as error:

        print(error.__class__.__name__, error)
        error_message = "an error occurred."

        match error.__class__.__name__:
            case "NotAuthorizedException":
                error_message = "invalid username or password"
            case "UsernameExistsException":
                error_message = error.__dict__["response"]["message"]
            case "Exception":
                error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
