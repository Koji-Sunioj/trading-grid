import os
import boto3
import json

dynamodb = boto3.resource('dynamodb')

response_object = {}
response_object['headers'] = {"Content-Type": "application/json",
                              "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*"}


def handler(event, context):
    route_key = "%s %s" % (event["httpMethod"], event['resource'])
    # table = dynamodb.Table(os.environ.get('TABLE_NAME'))
    # results = table.scan()
    # print(results)
    # Return response object

    match route_key:

        case "POST /sign-up":
            print(event)

    response_object['statusCode'] = 200
    response_object['body'] = json.dumps(
        {"resource": event['resource'], "method": event["httpMethod"]})

    return response_object
