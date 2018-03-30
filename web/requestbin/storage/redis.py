from __future__ import absolute_import

import time
import cPickle as pickle

import redis

from ..models import Bin

from requestbin import config

class RedisStorage():
    prefix = config.REDIS_PREFIX

    def __init__(self, bin_ttl):
        self.bin_ttl = bin_ttl
        self.redis = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)

    def _key(self, name):
        return '{}_{}'.format(self.prefix, name)

    def _request_count_key(self):
        return '{}-requests'.format(self.prefix)

    def create_bin(self, private=False):
        bin = Bin(private)
        key = self._key(bin.name)
        self.redis.set(key, bin.dump())
        self.redis.expireat(key, int(bin.created+self.bin_ttl))
        return bin

    def create_request(self, bin, request):
        bin.add(request)
        key = self._key(bin.name)
        self.redis.set(key, bin.dump())
        self.redis.expireat(key, int(bin.created+self.bin_ttl))

        self.redis.setnx(self._request_count_key(), 0)
        self.redis.incr(self._request_count_key())

    def count_bins(self):
        keys = self.redis.keys("{}_*".format(self.prefix))
        return len(keys)

    def count_requests(self):
        return int(self.redis.get(self._request_count_key()) or 0)

    def avg_req_size(self):
        info = self.redis.info()
        return info['used_memory'] / info['db0']['keys'] / 1024

    def lookup_bin(self, name):
        key = self._key(name)
        serialized_bin = self.redis.get(key)
        try:
            bin = Bin.load(serialized_bin)
            return bin
        except TypeError:
            self.redis.delete(key) # clear bad data
            raise KeyError("Bin not found")
