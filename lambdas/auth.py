import os
import boto3
import json

response = {}
response['headers'] = {"Content-Type": "application/json",
                       "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*"}


def handler(event, context):
    route_key = "%s %s" % (event["httpMethod"], event['resource'])
    if "body" in event:
        body = json.loads(event["body"])
        cognito = boto3.client("cognito-idp")
    else:
        raise Exception("there was no body in request")

    try:
        match route_key:
            case "POST /sign-up":

                params = {
                    "ClientId": os.environ.get('USER_POOL_ID'),
                    "Username": body["username"],
                    "Password": body["password"],
                    "UserAttributes": [{"Name": "email", "Value": body["email"]}, {"Name": "custom:erp_module", "Value": "purchase_orders"}]
                }
                cognito_response = cognito.sign_up(**params)

                if cognito_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    response['statusCode'] = 200
                    response["body"] = json.dumps({
                        "message": "user created. please check your email for verififcation code."})
                else:
                    raise Exception("there was an error creating your account")
            case "PATCH /sign-up":
                print("asdasd")

    except Exception as error:
        error_message = "an error occurred U+1F602"

        match error.__class__.__name__:
            case "UsernameExistsException":
                error_message = error.__dict__["response"]["message"]
            case "Exception":
                error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
