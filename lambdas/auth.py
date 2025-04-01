import os
import boto3
import json

response = {}
response['headers'] = {"Access-Control-Allow-Origin": "*",
                       "Access-Control-Allow-Methods": "*"}


def handler(event, context):
    try:
        if event["body"] != None:
            body = json.loads(event["body"])
            cognito = boto3.client("cognito-idp")
            route_key = "%s %s" % (event["httpMethod"], event['resource'])
        else:
            raise Exception("there was no body in request")

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
                params = {
                    "ClientId": os.environ.get('USER_POOL_ID'),
                    "Username": body["username"],
                    "ConfirmationCode": body["verification"]
                }
                cognito_response = cognito.confirm_sign_up(**params)
                print(cognito_response)

                response['statusCode'] = 200
                response["body"] = json.dumps({"message": "testing 123"})

            case _:
                raise Exception("no matching resource")

    except Exception as error:
        print(error)
        error_message = "an error occurred."

        match error.__class__.__name__:
            case "UsernameExistsException":
                error_message = error.__dict__["response"]["message"]
            case "Exception":
                error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
