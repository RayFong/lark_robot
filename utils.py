#!/usr/bin/env python3.8
import json
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")
WEATHER_ROBOT_URL = os.getenv("WEATHER_ROBOT_URL")
SWIM_ROBOT_URL = os.getenv("SWIM_ROBOT_URL")

class Obj(dict):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, Obj(b) if isinstance(b, dict) else b)


def dict_2_obj(d: dict):
    return Obj(d)


def save_data(filepath, data):
    with open(filepath, 'w') as fp:
        d = json.dumps(data, ensure_ascii=False, indent=2)
        fp.write(d)


def load_data(filepath, default={}):
    if not os.path.exists(filepath):
        return default
    with open(filepath) as fp:
        return json.load(fp)
