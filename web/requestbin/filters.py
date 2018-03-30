import datetime
from dateutil.parser import parse
import hashlib
import os
import time
import urllib

def approximate_time(ts):
    if not isinstance(ts, (int, long, float, complex)):
        return ""

    now = time.time()
    diff = now - ts

    if diff < 0:
        return "now"
    elif diff < 60:
        return "{}s".format(int(diff))
    elif diff < 60 * 60:
        minutes = diff / 60.0
        return "{}m".format(int(minutes))
    elif diff < 60 * 60 * 24:
        hours = diff / (60.0 * 60.0)
        return "{}h".format(int(hours))
    else:
        days = diff / (60.0 * 60.0 * 24.0)
        return "{}d".format(int(days))


def friendly_size(bytes):
    if isinstance(bytes, str):
        return bytes

    unit = ""
    if bytes <= 1024:
        unit = "bytes"
    elif bytes <= 1024 * 1024:
        bytes = round(bytes / 1024.0, 2)
        unit = "kB"

    return "{} {}".format(bytes, unit)


def status_class(status_code):
    status_code = str(status_code or "0")
    lookup = {
        "0" : "",
        "2" : "ok",
        "3" : "info",
        "4" : "warning",
        "5" : "error"
    }

    return lookup.get(status_code[0], "")


def friendly_time(secs):
    if isinstance(secs, str):
        return secs

    ms = int(round(secs * 1000.0))
    unit = "ms"
    if ms > 60000:
        unit = "minutes"
        ms = round(ms / 60000.0, 2)
    elif ms > 3000:
        ms = round(ms / 1000.0, 2)
        unit = "sec" if (ms == 1) else "secs"

    return "{} {}".format(ms, unit)


def friendly_number(input):
    if not isinstance(input, (int, long, float, complex)):
        return ""
    return "{:,}".format(input)


def exact_time(ts):
    if not isinstance(ts, (int, long, float, complex)):
        return None

    return datetime.datetime.utcfromtimestamp(ts)


def time_class(secs):
    if not isinstance(secs, (int, long, float, complex)):
        return ""

    ms = secs * 1000.0
    if ms > 3000:
        return "error"

    if ms > 1000:
        return "warning" 

    return ""


def to_qs(params_dict):
    if not params_dict or not isinstance(params_dict, dict):
        return ""

    qs = u"?" if params_dict else u""

    for k, v in params_dict.items():
        if len(qs) > 1:  # more than just the ?
            qs = qs + u"&"
        if v is None:
            qs = qs + k
        else:
            qs = qs + u"{}={}".format(k, v)
    return qs

    
def short_date(input):
    dt = None
    if isinstance(input, (str, unicode)):
        dt = parse(input)
    elif isinstance(input, (int, long, float, complex)):
        dt = datetime.datetime.utcfromtimestamp(float(input))
    else:
        return ""

    return dt.strftime("%b %d, %Y")