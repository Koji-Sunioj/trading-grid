import os
import json
import boto3
import datetime
import traceback

dynamodb = boto3.resource('dynamodb')
sockets_table = dynamodb.Table(os.environ.get("SOCKETS_TABLE"))
routing_table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))

def handler(event, context):
    # dynamodb = boto3.resource('dynamodb')
    # table = dynamodb.Table("")

    route_key = event["requestContext"]["routeKey"]
    connection_id = event["requestContext"]["connectionId"]

    try:
        match route_key:
            case "$connect":
                #for client - use routing table and validate with hmac in utils
                #for merchant - use cognito
                #distinguist by url param
                if "queryStringParameters" in event and "user" in event["queryStringParameters"]:
                    print("hello")
                    # clients = routing_table.scan()["Items"]
                    # table.put_item(Item={"connection_id": connection_id, "user": event["queryStringParameters"]["user"], "at": datetime.datetime.now(
                    # ).strftime("%Y-%m-%d %H:%M:%S")})
                else:
                    raise Exception("i need a name")
                return {"statusCode": 200}
            
            case "$disconnect":
                print("hello")
                #table.delete_item(Key={"connection_id": connection_id})
                return {"statusCode": 200}
            
    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())
        # error_message = error.__str__()

        return {"statusCode": 400}


    
