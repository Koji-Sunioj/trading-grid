import os
import boto3
import json

dynamodb = boto3.resource('dynamodb')


def handler(event, context):
    print(os.environ.get('TABLE_NAME'))
    print(event['resource'])
    print("/")
    print(context)
    table = dynamodb.Table(os.environ.get('TABLE_NAME'))
    results = table.scan()
    print(results)
    # Return response object
    response_object = {}
    response_object['statusCode'] = 200
    response_object['headers'] = {}
    response_object['headers']['Content-Type'] = 'application/json'
    response_object['headers']["Access-Control-Allow-Origin"] = "*"
    response_object['headers']["Access-Control-Allow-Methods"] = "*"
    response_object['body'] = json.dumps({"fuck": event['resource'],"shit":event["httpMethod"]})

    return response_object
