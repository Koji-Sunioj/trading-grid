import os
import json
import boto3
import datetime
import traceback

from utils import check_hmac, search, HMACException

dynamodb = boto3.resource('dynamodb')
sockets_table = dynamodb.Table(os.environ.get("SOCKETS_TABLE"))
routing_table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))

def handler(event, context):
    route_key = event["requestContext"]["routeKey"]
    connection_id = event["requestContext"]["connectionId"]

    print(route_key)
    print(connection_id)
    print(event["headers"])

    try:
        match route_key:
            case "$connect":
                if "queryStringParameters" in event and event["queryStringParameters"]["user"] == "merchant":
                    cognito = boto3.client("cognito-idp")
                    token = event["headers"]["Cookie"].split("=")[1]
                    cognito.get_user(AccessToken=token)
                elif "queryStringParameters" in event and event["queryStringParameters"]["user"] == "client" and "client_id" in event["queryStringParameters"]:
                    clients = routing_table.scan()["Items"]
                    client = search(clients, "client_id",event["queryStringParameters"]["client_id"])
                    check_hmac(str(event["queryStringParameters"]),event["headers"]["Authorization"], client["hmac"])
                else:
                    raise Exception("unauthorized user")

                sockets_table.put_item(Item={"connection_id": connection_id, "user": event["queryStringParameters"]["user"], "at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})  
            
            case "$disconnect":
                sockets_table.delete_item(Key={"connection_id": connection_id})
    
            case _:
                raise Exception("no matching resources")

        return {"statusCode": 200} 
            
    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())

        return {"statusCode": 400} 


    
