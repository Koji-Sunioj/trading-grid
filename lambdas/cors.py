import os
import json
import boto3
import traceback

from utils import search


merchant_params = json.loads(os.environ.get("MERCHANT_PARAMS"))
react_cfn_outputs = boto3.client('cloudformation').describe_stacks(StackName='merchant-webapp')["Stacks"][0]["Outputs"]
cloudfront_react_url = "https://%s" % search(react_cfn_outputs,"OutputKey","CloudFrontURL")["OutputValue"]

def handler(event, context):
    response = {}
    response['headers'] = {}

    try:
        if event["headers"]["origin"] == merchant_params["dev-server"] or event["headers"]["origin"] == cloudfront_react_url:
            response["statusCode"] = 200
            response["headers"]["Access-Control-Allow-Origin"] = event["headers"]["origin"]
            response["headers"]["Access-Control-Allow-Credentials"] = "true"
            response["headers"]["Access-Control-Allow-Headers"] = "Content-Type"
            response["headers"]["Access-Control-Allow-Methods"] = "DELETE"
        else:
            raise Exception("client is not whitelisted")

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())
        error_message = error.__str__()

        response['statusCode'] = 400
        response["body"] = json.dumps({"message": error_message})
    return response
