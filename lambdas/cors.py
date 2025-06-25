import os
import json
import traceback


def handler(event, context):
    response = {}
    response['headers'] = {}

    try:
        accepted_origins = os.environ.get("ACCEPTED_ORIGINS").split(",")
        if event["headers"]["origin"] in accepted_origins:
            response["statusCode"] = 200
            response["headers"]["Access-Control-Allow-Origin"] = event["headers"]["origin"]
            response["headers"]["Access-Control-Allow-Credentials"] = "true"
            response["headers"]["Access-Control-Allow-Headers"] = "Content-Type"
            response["headers"]["Access-Control-Allow-Methods"] = "DELETE"

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())
        error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})
    return response
