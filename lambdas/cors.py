import json
import traceback


def handler(event, context):
    response = {}
    try:
        print(event)
        response["statusCode"] = 200
        response["body"] = json.dumps({"hello": "man"})

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())
        error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})

    return response
