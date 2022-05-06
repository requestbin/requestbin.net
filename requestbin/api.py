import json
import operator

from flask import session, make_response, request, render_template
from requestbin import app, db

def _response(object, code=200):
    jsonp = request.args.get('jsonp')
    if jsonp:
        resp = make_response('%s(%s)' % (jsonp, json.dumps(object)), 200)
        resp.headers['Content-Type'] = 'text/javascript'
    else:
        resp = make_response(json.dumps(object), code)
        resp.headers['Content-Type'] = 'application/json'
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# create new bin
@app.route("/bins/new", methods=['POST'])
def newbin():
    if 'Cf-Connecting-Ip' in request.headers:
        ip = request.headers['Cf-Connecting-Ip']
    else:
        ip = request.remote_addr
    bin = db.create_bin(ip)
    # if bin.private:
    #     session[bin.name] = bin.secret_key
    return _response(bin.to_dict())