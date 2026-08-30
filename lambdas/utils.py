import os
import hmac
import math
import uuid
import json
import boto3
import hashlib
import datetime
import requests

from decimal import Decimal
from zoneinfo import ZoneInfo
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timedelta, date


class HMACException(Exception):
    pass


class NoCookieException(Exception):
    pass


def broadcast(user: str, module: str, identifier: str) -> None:
    dynamodb = boto3.resource('dynamodb')
    sockets_table = dynamodb.Table(os.environ.get("SOCKETS_TABLE"))

    merchant_sockets = sockets_table.scan(
        FilterExpression=Attr("user").eq(user))["Items"]

    for connection in merchant_sockets:
        api_client = boto3.client(
            "apigatewaymanagementapi", endpoint_url=connection["endpoint_url"])
        try:
            api_client.post_to_connection(Data=json.dumps(
                {"module": module, "identifier": identifier}), ConnectionId=connection["connection_id"])
        except:
            sockets_table.delete_item(
                Key={"connection_id": connection["connection_id"]})


def serialize_float(obj: Decimal) -> float:
    return float(obj)


def webssocket_token() -> dict:
    ws_token = uuid.uuid4()
    ws_token_hash = hashlib.sha256(str(ws_token).encode("utf-8")).hexdigest()
    return {"ws_token": ws_token, "ws_token_hash": ws_token_hash}


def check_hmac(payload, request_hmac, hmac_key) -> None:
    correct_hmac = hmac.digest(hmac_key.encode(
    ), payload.encode(), digest=hashlib.sha256).hex()
    if not hmac.compare_digest(request_hmac, correct_hmac):
        raise HMACException("invalid credentials")


def search(dicts, key, value) -> dict:
    try:
        return next(n for n in dicts if n[key] == value)
    except:
        return None


def get_dispatch(items, client, coords, api_key) -> dict:
    lat, long = client["coords"]["latitude"], client["coords"]["longitude"]

    distance_lookup = requests.get("https://api.radar.io/v1/route/distance?origin=%s&destination=%s,%s&modes=car&units=metric" % (
        coords, lat, long), headers={"Authorization": api_key})

    freight = distance_lookup.json()["routes"]["car"]
    kilometers, minutes = int(
        freight["distance"]["value"] / 1000), int(round(freight["duration"]["value"]))
    weight_grams = 100 * \
        int(items)
    volume = (14.2 * 12.5 * 1.0) / 5000 * \
        float(items)
    cost = round(kilometers * volume * 1.25, 2)

    today = date.today()
    current_slot = datetime(year=today.year, month=today.month, day=today.day,
                            hour=12, minute=0, tzinfo=ZoneInfo("Europe/Helsinki"))
    n_days = 7 if current_slot.weekday() >= 2 else 2

    dispatch_slot = current_slot + \
        timedelta(days=n_days - current_slot.weekday())
    estimated_delivery = dispatch_slot + \
        timedelta(minutes=math.ceil(minutes / 10) * 10)

    return {"freight_cost": cost, "estimated_delivery": estimated_delivery.strftime("%Y-%m-%d %H:%M"), "weight_grams": weight_grams}
