import json
import boto3
import datetime


def handler(event, context):
    # dynamodb = boto3.resource('dynamodb')
    # table = dynamodb.Table("")

    route_key = event["requestContext"]["routeKey"]
    connection_id = event["requestContext"]["connectionId"]

    match route_key:
        case "$connect":
            if "queryStringParameters" in event and "user" in event["queryStringParameters"]:
                print("hello")
                # table.put_item(Item={"connection_id": connection_id, "user": event["queryStringParameters"]["user"], "at": datetime.datetime.now(
                # ).strftime("%Y-%m-%d %H:%M:%S")})
            else:
                raise Exception("i need a name")

        case "update":
            print("hello")
            #payload = json.loads(event["body"])
            #if "message" in payload:
            #    user = table.get_item(Key={"connection_id": connection_id})[
            #        "Item"]["user"]
            #
            #    message = payload["message"]
            #    api_client = boto3.client("apigatewaymanagementapi", endpoint_url="https://%s/%s" % (
            #        event["requestContext"]["domainName"], event["requestContext"]["stage"]))
            #    connections = table.scan()
            #    connection_ids = [item["connection_id"]
            #                      for item in connections["Items"]]
            #
            #    for connection in connection_ids:
            #        api_client.post_to_connection(
            #            Data=json.dumps({"message": message, "user": user}), ConnectionId=connection)
            #else:
            #    raise Exception("i need a message")

        case "$disconnect":
            print("hello")
            #table.delete_item(Key={"connection_id": connection_id})

    return {"statusCode": 200}
