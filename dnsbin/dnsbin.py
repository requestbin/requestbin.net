#!/usr/bin/env python
"""
LICENSE http://www.apache.org/licenses/LICENSE-2.0
https://gist.github.com/pklaus/b5a7876d4d2cf7271873
"""

import argparse
import datetime
import time
import sys
import time
import threading
import socketserver
import struct
import logging
import json
from dnsutil import insertDNSRequest, tinyid, insertSQLite
from flask_pymongo import PyMongo
from flask import Flask

try:
    from dnslib import *
except ImportError:
    print("Missing dependency dnslib: <https://pypi.python.org/pypi/dnslib>. Please install it with `pip`.")
    sys.exit(2)

class DomainName(str):
    def __getattr__(self, item):
        return DomainName(item + '.' + self)

env_loglevel = os.environ.get('LOG_LEVEL', "INFO")
if env_loglevel == "ERROR":
	loglevel = logging.ERROR
elif env_loglevel == "DEBUG":
	loglevel = logging.DEBUG
else:
	loglevel = logging.INFO

loghandler = [ logging.FileHandler("dnsdebug.log"), logging.StreamHandler()]
logging.basicConfig(
    level=loglevel,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=loghandler
)

dns_default_response = CNAME(os.environ.get('CNAME', "xxxxxxxxxxxxx.herokudns.com"))
dns_default_response_ip = A("127.0.0.1")
targetDomain = "requestbin.net."
dnsbinDomain = ".b.%s" % targetDomain
v1Domain = ".d.%s" % targetDomain

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGODB_URI', "mongodb://192.168.32.xx:xx/xx?retryWrites=true")
mongodb = PyMongo(app)

def dns_response(data, clientIP):
    try:
        request = DNSRecord.parse(data)
    except Exception as e:
        logging.error(e)
        return None

    logging.debug(request)

    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = request.q.qname
    qn = str(qname)
    logging.debug("Request %s" % qn)

    if qn.endswith(dnsbinDomain):
        dnsrequest = {}
        dnsrequest["id"] = tinyid(20)
        dnsrequest["time"] = time.time()
        dnsrequest["remote_addr"] = clientIP
        dnsrequest["base_dns"] = qn

        data = qn[0:-1*len(dnsbinDomain)]
        logging.debug("Sub data: %s" % data)
        if "." not in data:
            id = data
            dnsrequest["data"] = "None"    
        else:
            id = data[data.rindex(".")+1:]
            dnsrequest["data"] = data[0:-1*len(id)-1]
        logging.debug("DNS NG id %s" % id)
        logging.debug("data %s" % dnsrequest["data"])

        if insertDNSRequest(mongodb, id, dnsrequest):
            reply.add_answer(RR(rname=qname, rtype=getattr(QTYPE, dns_default_response.__class__.__name__), rclass=1, rdata=dns_default_response))
        else:
            logging.debug("Not found DNS BIN")
    elif qn.endswith(v1Domain):
        dnsrequest = {}
        dnsrequest["time"] = int(1000*time.time())
        dnsrequest["ip"] = clientIP
        data = qn[0:-1*len(v1Domain)]
        id = data[data.rindex(".")+1:]
        logging.debug("id %s" % id)
        dnsrequest["content"] = data[0:-1*len(id)-1]
        logging.debug("data %s" % dnsrequest["content"])
        if insertSQLite(id, json.dumps(dnsrequest)):
            reply.add_answer(RR(rname=qname, rdata=dns_default_response_ip))
    else:
        logging.info("DNS-No-match: %s from %s" % (qn, clientIP))
    logging.debug("Reply: %s" % reply)
    return reply.pack()

class BaseRequestHandler(socketserver.BaseRequestHandler):
    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        logging.debug("\n\n%s request %s (%s %s):" % (self.__class__.__name__[:3], now, self.client_address[0],
                                               self.client_address[1]))
        try:
            data = self.get_data()
            #logging.debug(len(data), data)  # repr(data).replace('\\x', '')[1:-1]
            self.send_data(dns_response(data, self.client_address[0]))
        except Exception as e:
            #traceback.print_exc(file=sys.stderr)
            logging.debug(e)

class TCPRequestHandler(BaseRequestHandler):
    def get_data(self):
        data = self.request.recv(8192).strip()
        sz = struct.unpack('>H', data[:2])[0]
        if sz < len(data) - 2:
            raise Exception("Wrong size of TCP packet")
        elif sz > len(data) - 2:
            raise Exception("Too big TCP packet")
        return data[2:]

    def send_data(self, data):
        sz = struct.pack('>H', len(data))
        return self.request.sendall(sz + data)

class UDPRequestHandler(BaseRequestHandler):
    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)

def main():
    parser = argparse.ArgumentParser(description='Start a DNS implemented in Python.')
    parser = argparse.ArgumentParser(description='Start a DNS implemented in Python. Usually DNSs use UDP on port 53.')
    parser.add_argument('--port', default=5053, type=int, help='The port to listen on.')
    parser.add_argument('--tcp', action='store_true', help='Listen to TCP connections.')
    parser.add_argument('--udp', action='store_true', help='Listen to UDP datagrams.')
    
    args = parser.parse_args()
    if not (args.udp or args.tcp): parser.error("Please select at least one of --udp or --tcp.")

    logging.info("Starting nameserver...")

    servers = []
    if args.udp: servers.append(socketserver.ThreadingUDPServer(('', args.port), UDPRequestHandler))
    if args.tcp: servers.append(socketserver.ThreadingTCPServer(('', args.port), TCPRequestHandler))

    for s in servers:
        thread = threading.Thread(target=s.serve_forever)  # that thread will start one more thread for each request
        thread.daemon = True  # exit the server thread when the main thread terminates
        thread.start()
        logging.info("%s server loop running in thread: %s" % (s.RequestHandlerClass.__name__[:3], thread.name))

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.shutdown()

if __name__ == '__main__':
    main()
