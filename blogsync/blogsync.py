#!/usr/bin/env python

import argparse
import datetime
import time
import sys
import os
import time
import requests
import logging
import json
from flask_pymongo import PyMongo
from flask import Flask
import re

env_loglevel = os.environ.get('LOG_LEVEL', "INFO")
if env_loglevel == "ERROR":
	loglevel = logging.ERROR
elif env_loglevel == "DEBUG":
	loglevel = logging.DEBUG
else:
	loglevel = logging.INFO

loghandler = [ logging.FileHandler("syncdebug.log"), logging.StreamHandler()]
logging.basicConfig(
    level=loglevel,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=loghandler
)

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGODB_URI', "mongodb://192.168.32.xx:xx/xx?retryWrites=true")
mongodb = PyMongo(app)
blogRepo = os.environ.get('BLOG_REPO', "requestbin/blog")

def getListResources(path):
    headers = {}
    headers["accept"] = "application/vnd.github.v3+json"
    url = "https://api.github.com/repos/%s/contents%s" % (blogRepo, path)
    resp = requests.get(url, headers= headers)
    if resp.status_code == 200:
        lstRes = json.loads(resp.content.decode('utf-8'))
        return lstRes
    else:
        raise Exception("Resource %s is not found" % (path))  

def getResourceSHA(path, resource):
    lstRes = getListResources(path)
    for res in lstRes:
        if res["name"] == resource:
            return res["sha"]
    raise Exception("Resource %s %s is not found" % (path, resource))

def getResource(resource, type = "raw"):
    headers = {}
    headers["accept"] = "application/vnd.github.v3.%s" % type
    url = "https://api.github.com/repos/%s/contents/%s" % (blogRepo, resource)
    resp = requests.get(url, headers= headers)
    if resp.status_code == 200:
        return resp.content.decode('utf-8')
    else:
        raise Exception("Resource %s is not found" % (resource))  

def getPost(path):
    lstRes = getListResources(path)
    retPost = {"title": "", "thumb": "", "content": "", "date": ""}
    for res in lstRes:
        if res["name"] == "meta.txt":
            retMeta = getResource(res["path"]).split("\n")
            retPost["title"] = retMeta[0] if len(retMeta) > 0 else ""
            retPost["date"] = retMeta[1] if len(retMeta) > 1 else ""
        elif "thumb." in res["name"]:
            retPost["thumb"] = "https://raw.githubusercontent.com/requestbin/blog/main/%s" % res["path"]
        elif res["name"] == "index.md":
            retPost["content"] = getResource(res["path"], "html")
    return retPost

if __name__ == '__main__':
    logging.info("Starting synchronize blog...")
    # get list category
    cats = mongodb.db.postsmeta.find({"type": "category"})
    for cat in cats:
        catName = cat["name"]
        catSHA = cat["sha"]
        logging.debug("Checking in category %s" % catName)
        nowSHA = getResourceSHA("/", catName)
        if catSHA != nowSHA:
            lstRes = getListResources("/%s" % catName)
            for res in lstRes:
                id = res["name"].lower().replace(" ", "-")
                id = re.sub('[{}%$\'\"]', '', id)
                logging.debug("Checking id %s" % id)
                meta = mongodb.db.postsmeta.find_one({"type": "post", "category": catName, "id": id})
                changed = True
                if meta:
                    if meta["sha"] == res["sha"]:
                        changed = False
                if changed:
                    newPost = {}
                    newPost["type"] = "post"
                    newPost["category"] = catName
                    newPost["id"] = id
                    newPost["sha"] = res["sha"]
                    newPost["path"] = res["path"]
                    retPost = getPost(res["path"])
                    newPost["thumb"] = retPost["thumb"]
                    newPost["title"] = retPost["title"]
                    newPost["date"] = retPost["date"]
                    mongodb.db.postsmeta.update_one({"id": id}, {'$set': newPost}, upsert=True)
                    mongodb.db.posts.update_one({"id": id}, {'$set': {"id": id, "content": retPost["content"]}}, upsert=True)
        cat["sha"] = nowSHA
        mongodb.db.postsmeta.update_one({"type": "category", "name": catName}, {'$set': cat}, upsert=True)
    logging.info("Synchronize blog DONE!")


