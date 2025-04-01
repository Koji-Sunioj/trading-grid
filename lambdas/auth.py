import os
import boto3
import json

response = {}
response['headers'] = {"Content-Type": "application/json",
                       "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*"}


def handler(event, context):
    route_key = "%s %s" % (event["httpMethod"], event['resource'])

    try:
        match route_key:

            case "POST /sign-up":
                body = json.loads(event["body"])
                cognito = boto3.client("cognito-idp")
                params = {
                    "ClientId": os.environ.get('USER_POOL_ID'),
                    "Username": body["username"],
                    "Password": body["password"],
                    "UserAttributes": [{"Name": "email", "Value": body["email"]}, {"Name": "custom:erp_module", "Value": "purchase_orders"}]
                }
                cognito_response = cognito.sign_up(**params)

                print(cognito_response)

                if cognito_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    response['statusCode'] = 200
                    response["body"] = {
                        "message": "user created. please check your email for verififcation code."}
                else:
                    raise Exception("there was an error creating your account")

    except Exception as error:
        print(error)
        response['statusCode'] = 400
        response["body"] = error

    return response
