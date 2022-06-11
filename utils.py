#!/usr/bin/env python3.8
import json

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
