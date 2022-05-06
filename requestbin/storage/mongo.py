from __future__ import absolute_import
from telnetlib import SE

import time
#import cPickle as pickle
import pickle

import os
from flask_pymongo import PyMongo

from ..models import Bin, NewBin, Request

from requestbin import config
from requestbin import app

class MongoStorage():
    prefix = config.REDIS_PREFIX

    def __init__(self, bin_ttl):
        self.bin_ttl = bin_ttl
        app.config["MONGO_URI"] = os.environ.get("MONGODB_URI")
        self.mongodb = PyMongo(app)

    def _key(self, name):
        return name

    def _request_count_key(self):
        return '{}-requests'.format(self.prefix)

    def create_bin(self, ownerIP = None):
        bin = NewBin(ownerIP)
        newbin = bin.to_dict()
        self.mongodb.db.bins.insert_one(newbin)
        return bin

    def create_request(self, bin, request):
        if not bin.check_add():
            raise KeyError("Denied")
        self.mongodb.db.requests.insert_one({"binID": bin.binID, "type": "http", "request": Request(request).to_dict()})
        bin.add(request)
        self.mongodb.db.bins.update_one({"binID": bin.binID},{"$set": bin.to_dict()})

    def count_bins(self):
        return self.mongodb.db.bins.count()

    def count_requests(self):
        return self.mongodb.db.bins.count()

    def avg_req_size(self):
        return self.mongodb.db.bins.totalSize() / self.mongodb.db.bins.count() / 1024

    # get bin via key
    def lookup_bin(self, binKey):
        binDict = self.mongodb.db.bins.find_one({"binKey": binKey})
        if binDict:
            try:
                requests = list(self.mongodb.db.requests.find({"binID": binDict["binID"]}))
                bin = NewBin()
                bin.load_request(binDict, requests)
                return bin
            except TypeError:
                self.mongodb.db.bins.delete_one({"binKey": binKey})
                #raise KeyError("Bin not found")
                return None
        else:
            #raise KeyError("Bin not found")
            return None

    # get bin via ID (for add new request)
    def get_via_binid(self, binID):
        binDict = self.mongodb.db.bins.find_one({"binID": binID})
        if binDict:
            bin = NewBin()
            bin.load_request(binDict, [])
            return bin
        else:
            #raise KeyError("Bin not found")
            return None

    def getListPosts(self, limit = None):
        lstPosts = list(reversed(list(self.mongodb.db.postsmeta.find({"type": "post", "title": {"$ne" : ""}}))))
        if limit != None:
            lstPosts = lstPosts[0:int(limit)]
        return lstPosts

    def getPost(self, postid):
        retPost = {}
        postMeta = self.mongodb.db.postsmeta.find_one({"id": str(postid)})
        if not postMeta:
            return None
        retPost['id'] = postid
        retPost['title'] = postMeta['title']
        retPost['date'] = postMeta['date']
        post = self.mongodb.db.posts.find_one({"id": str(postid)})
        if not post:
            return None
        retPost['content'] = post['content']
        return retPost
