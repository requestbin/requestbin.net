import time
import random
import string
import sqlite3
import json, os

def tinyid(size=6):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(size))

def insertSQLite(id, content):
    conn = None
    try:
        #logging.debug("Inserting %s" % content)
        env_sqllite = os.environ.get('SQLLITE', "dnsdb.lite")
        conn = sqlite3.connect(env_sqllite)
        cur = conn.cursor()

        cur.execute("SELECT master FROM identity WHERE subdomain = ?;", (id,))
        rows = cur.fetchall()

        if len(rows) > 0:
            sql = "INSERT INTO requests VALUES (?, ?, ?, ?);"
            cur.execute(sql, (rows[0][0], content, int(1000*time.time()), False))
            conn.commit()
            return True
        else:
            #logging.debug("Not foud %s" % id)
            return False
    except Exception as e:
        #logging.exception(e)
        print(e)

def insertDNSRequest(mongo, id, request):
    # check add
    binDict = mongo.db.bins.find_one({"binID": id})
    if binDict:
        # check
        MAX_REQUESTS = 50
        RATELIMIT_REQUEST = 15
        if (binDict["request_count"] + 1 >= MAX_REQUESTS and time.time() - binDict["lasttime"] < RATELIMIT_REQUEST) or (binDict["status"] != "active"):
            return False
        else:
            # add
            mongo.db.requests.insert_one({"binID": id, "type": "dns", "request": request})
            mongo.db.bins.update_one({"binID": id},{"$set": {"request_count": binDict["request_count"] + 1, "lasttime": time.time()}})
            return True
    else:
        #raise KeyError("Bin not found")
        return False
