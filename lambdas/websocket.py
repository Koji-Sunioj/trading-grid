import os
import json
import boto3
import hashlib
import datetime
import traceback
from utils import check_hmac, search, NoCookieException

dynamodb = boto3.resource('dynamodb')
sockets_table = dynamodb.Table(os.environ.get("SOCKETS_TABLE"))
routing_table = dynamodb.Table(os.environ.get("ROUTING_TABLE"))
ws_token_table = dynamodb.Table(os.environ.get("WS_TOKEN_TABLE"))


def handler(event, context):
    route_key = event["requestContext"]["routeKey"]
    connection_id = event["requestContext"]["connectionId"]
    query = event["queryStringParameters"] if "queryStringParameters" in event else None

    try:
        match route_key:
            case "$connect":
                if query != None and query["user"] == "merchant" and list(query.keys()) == ['token', 'user', 'username']:
                    if "token" not in query:
                        raise NoCookieException("invalid user")
                    
                    ws_token = query["token"]
                    ws_token_hash = hashlib.sha256(
                        str(ws_token).encode("utf-8")).hexdigest()
                    token_entry = ws_token_table.get_item(
                        Key={"username": query["username"]})["Item"]

                    if token_entry["token_hash"] != ws_token_hash and token_entry["username"] != query["username"]:
                        raise Exception("unathorized user")

                elif query != None and query["user"] == "client" and list(query.keys()) == ['client_id', 'hmac', 'user']:
                    clients = routing_table.scan()["Items"]
                    client = search(clients, "client_id", query["client_id"])

                    check_hmac(str(
                        {"client_id": query["client_id"], "user": query["user"]}), query["hmac"], client["hmac"])
                else:
                    raise Exception("unauthorized user")

                sockets_table.put_item(Item={"connection_id": connection_id,
                                             "user": event["queryStringParameters"]["user"], "at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                             "endpoint_url": "https://%s/%s" % (event["requestContext"]["domainName"], event["requestContext"]["stage"])})

            case "$disconnect":
                sockets_table.delete_item(Key={"connection_id": connection_id})

            case "ping":
                api_client = boto3.client("apigatewaymanagementapi", endpoint_url="https://%s/%s" % (
                    event["requestContext"]["domainName"], event["requestContext"]["stage"]))
                api_client.post_to_connection(
                    Data=json.dumps({"message": "pong"}), ConnectionId=connection_id)

            case _:
                raise Exception("no matching resources")

        return {"statusCode": 200}

    except Exception as error:
        print("error name %s" % error.__class__.__name__)
        print(traceback.format_exc())

        match error.__class__.__name__:
            case "NotAuthorizedException" | "UserNotFoundException" | "HMACException" | "NoCookieException": 
                return {"statusCode": 401}
            case _:
                return {"statusCode": 400}
            
    
