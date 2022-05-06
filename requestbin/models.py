import copy
import json
import time
import datetime
import os
import re
from aiohttp import request

import msgpack

from .util import random_color
from .util import tinyid
from .util import solid16x16gif_datauri
from .util import genKey
import base64

from requestbin import config

class Bin(object):
    max_requests = config.MAX_REQUESTS

    def __init__(self, private=False):
        self.created = time.time()
        self.private = private
        self.color = random_color()
        self.name = tinyid(8)
        self.favicon_uri = solid16x16gif_datauri(*self.color)
        self.requests = []
        self.secret_key = os.urandom(24) if self.private else None

    def json(self):
        return json.dumps(self.to_dict())
    
    def to_dict(self):
        return dict(
            private=self.private, 
            color=self.color, 
            name=self.name,
            request_count=self.request_count)

    def dump(self):
        o = copy.copy(self.__dict__)
        o['requests'] = [r.dump() for r in self.requests]
        return msgpack.dumps(o)

    def dumps(self):
        o = copy.copy(self.__dict__)
        o['requests'] = [r.dump() for r in self.requests]
        packbin = msgpack.dumps(o)
        return base64.b64encode(packbin).decode('ascii')

    @staticmethod
    def load(data):
        o = msgpack.loads(data)
        o['requests'] = [Request.load(r) for r in o['requests']]
        b = Bin()
        b.__dict__ = o
        return b

    @staticmethod
    def loads(data):
        databin = base64.b64decode(data.encode('ascii'))
        o = msgpack.loads(databin)
        o['requests'] = [Request.load(r) for r in o['requests']]
        b = Bin()
        b.__dict__ = o
        return b

    @property
    def request_count(self):
        return len(self.requests)

    def add(self, request):
        self.requests.insert(0, Request(request))
        if len(self.requests) > self.max_requests:
            for _ in range(self.max_requests, len(self.requests)):
                self.requests.pop(self.max_requests)

class NewBin(object):
    max_requests = config.MAX_REQUESTS
    ratelimit_request = config.RATELIMIT_REQUEST

    def __init__(self, ownerIP = None):
        self.created = time.time()
        self.binID = tinyid(16)
        self.binKey = genKey(self.binID, tinyid(24))
        self.ownerIP = ownerIP
        self.status = "active"
        self.request_count = 0
        self.lasttime = time.time()
        self.last_request = ""
        self.requests = []

    def load_request(self, binDict, requests):
        self.created = binDict['created']
        self.binID = binDict['binID']
        self.binKey = binDict['binKey']
        self.ownerIP = binDict['ownerIP']
        self.status = binDict['status']
        self.request_count = binDict['request_count']
        self.lasttime = binDict['lasttime']
        self.last_request = binDict['last_request']
        self.requests = []
        for req in reversed(requests):
            new_req = Request()
            if req['type'] == 'http':
                new_req.load_dict(req['request'], type="http")
            elif req['type'] == 'dns':
                new_req.load_dict(req['request'], type="dns")
            self.requests.append(new_req)

    def json(self):
        return json.dumps(self.to_dict())
    
    def to_dict(self):
        return dict(
            created=self.created, 
            binID=self.binID, 
            binKey=self.binKey,
            ownerIP=self.ownerIP,
            status=self.status,
            request_count=self.request_count,
            lasttime=self.lasttime,
            last_request=self.last_request
            )

    def dump(self):
        o = copy.copy(self.__dict__)
        o['requests'] = [r.dump() for r in self.requests]
        return msgpack.dumps(o)

    def dumps(self):
        o = copy.copy(self.__dict__)
        o['requests'] = [r.dump() for r in self.requests]
        packbin = msgpack.dumps(o)
        return base64.b64encode(packbin).decode('ascii')

    @staticmethod
    def load(data):
        o = msgpack.loads(data)
        o['requests'] = [Request.load(r) for r in o['requests']]
        b = Bin()
        b.__dict__ = o
        return b

    @staticmethod
    def loads(data):
        databin = base64.b64decode(data.encode('ascii'))
        o = msgpack.loads(databin)
        o['requests'] = [Request.load(r) for r in o['requests']]
        b = Bin()
        b.__dict__ = o
        return b

    # check rate limit for add request
    def check_add(self):
        if (self.request_count + 1 >= self.max_requests and time.time() - self.lasttime < self.ratelimit_request) or (self.status != "active"):
            return False
        else:
            return True

    # increase count, pop last request if 
    def add(self, request):
        self.request_count += 1
        self.lasttime = time.time()

class Request(object):
    ignore_headers = config.IGNORE_HEADERS
    max_raw_size = config.MAX_RAW_SIZE 

    def __init__(self, input=None):
        self.type = "http" # default is http, otherwise, dns
        if input:
            self.id = tinyid(20)
            self.time = time.time()
            self.remote_addr = input.headers.get('X-Forwarded-For', input.remote_addr)
            self.scheme = input.scheme
            self.method = input.method
            self.base_url = "%s://%s"%(input.scheme, input.host)
            self.headers = dict(input.headers)

            for header in self.ignore_headers:
                self.headers.pop(header, None)

            self.query_string = input.args.to_dict(flat=True)
            self.form_data = []

            for k in input.form:
                self.form_data.append([k, input.values[k]])

            self.body = input.data
            self.path = input.path
            self.content_type = self.headers.get("Content-Type", "")

            self.raw = input.environ.get('raw')
            self.content_length = len(self.raw)

            if self.raw and len(self.raw) > self.max_raw_size:
                self.raw = self.raw[0:self.max_raw_size]

    def to_dict(self):
        return dict(
            id=self.id,
            time=self.time,
            remote_addr=self.remote_addr,
            scheme=self.scheme,
            method=self.method,
            base_url=self.base_url,
            headers=self.headers,
            query_string=self.query_string,
            raw=self.raw,
            form_data=self.form_data,
            body=self.body,
            path=self.path,
            content_length=self.content_length,
            content_type=self.content_type,
        )
    
    def load_dict(self, data, type="http"):
        if type=="dns":
            self.type="dns"
            self.id=data['id']
            self.time=data['time']
            self.remote_addr=data['remote_addr']
            self.base_dns=data['base_dns']
            self.data=data['data']
        else:
            self.type="http"
            self.id=data['id']
            self.time=data['time']
            self.remote_addr=data['remote_addr']
            self.scheme=data['scheme']
            self.method=data['method']
            self.base_url=data['base_url']
            self.headers=data['headers']
            self.query_string=data['query_string']
            self.raw=data['raw']
            self.form_data=data['form_data']
            self.body=data['body']
            self.path=data['path']
            self.content_length=data['content_length']
            self.content_type=data['content_type']

    @property
    def created(self):
        return datetime.datetime.fromtimestamp(self.time)

    def dump(self):
        return msgpack.dumps(self.__dict__)

    @staticmethod
    def load(data):
        r = Request()
        try:
            r.__dict__ = msgpack.loads(data)
        except (UnicodeDecodeError):
            r.__dict__ = msgpack.loads(data)

        return r