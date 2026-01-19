import os
import hmac
import math
import hashlib
import datetime
import requests

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, date


def serialize_float(obj):
    return float(obj)


def check_hmac(payload, request_hmac, hmac_key):
    correct_hmac = hmac.digest(hmac_key.encode(
    ), payload.encode(), digest=hashlib.sha256).hex()
    if not hmac.compare_digest(request_hmac, correct_hmac):
        raise Exception("invalid credentials")


def search(dicts, key, value):
    try:
        return next(n for n in dicts if n[key] == value)
    except:
        return None


def get_dispatch(items, client):
    lat, long = client["coords"]["latitude"], client["coords"]["longitude"]

    distance_lookup = requests.get("https://api.radar.io/v1/route/distance?origin=%s&destination=%s,%s&modes=car&units=metric" % (
        os.environ.get("STORE_COORDS"), lat, long), headers={"Authorization": os.environ.get("TOKEN_KEY")})

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
