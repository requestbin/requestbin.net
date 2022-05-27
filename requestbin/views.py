import urllib
from flask import session, redirect, url_for, escape, request, render_template, make_response
import re, time
from urllib.parse import urlparse
from requestbin import app, db

@app.route("/")
def home():
    lstPosts = db.getListPosts(7)
    return render_template('home.html', posts = lstPosts)

@app.route("/dns")
@app.route("/bins")
def bins():
    return render_template('bins.html')

@app.route("/about")
def about():
    return render_template('about.html')

# view details of bin
@app.route('/', defaults={'path': ''}, subdomain="<binID>.b", methods=['GET', 'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'PATCH', 'TRACE'])
@app.route('/<path:path>', subdomain="<binID>.b", methods=['GET', 'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'PATCH', 'TRACE'])
def bintrigger(path, binID):
    # via binID
    binID = binID.split(".")[-1]
    bin = db.get_via_binid(binID)
    if bin == None:
        return "BIN NOT FOUND!\n", 404
    db.create_request(bin, request)
    ts = time.time()
    resp = make_response(str(ts).replace(".","") + "\n")
    resp.headers['Sponsored-By'] = "https://requestbin.net"
    return resp

# view details of bin
@app.route('/bins/view/<path:binKey>', methods=['GET'])
def bin(binKey):
    try:
        bin = db.lookup_bin(binKey)
    except KeyError:
        return "Not found\n", 404
    remote_ip = ""
    if 'Cf-Connecting-Ip' in request.headers:
        remote_ip = request.headers['Cf-Connecting-Ip']
    else:
        remote_ip = request.remote_addr
    return render_template('bin.html',
        bin=bin,
        base_url=request.host,
        remote_ip = remote_ip)

@app.route("/uip")
def myip():
    remote_ip = ""
    if 'Cf-Connecting-Ip' in request.headers:
        remote_ip = request.headers['Cf-Connecting-Ip']
    else:
        remote_ip = request.remote_addr
    return render_template('ip.html', recent=False, remote_ip = remote_ip, base_url=request.scheme+'://'+request.host)

@app.route("/ip")
def ip():
    if 'Cf-Connecting-Ip' in request.headers:
        resp = make_response(request.headers['Cf-Connecting-Ip'] + "\n")
    else:
        resp = make_response(request.remote_addr + "\n")
    resp.headers['Sponsored-By'] = "http://requestbin.net"
    return resp

@app.route("/ads.txt")
def ads():
    return make_response("google.com, pub-7093275067786161, DIRECT, f08c47fec0942fa0")

@app.route("/blog")
def blog():
    lstPosts = db.getListPosts()
    return render_template('blog.html', posts=lstPosts)

@app.route('/post/<string:postid>', methods=['GET'])
def post(postid):
    # nosql injection prevention
    postid = re.sub('[{}%$\'\"]', '', postid)
    post = db.getPost(postid)
    if post == None:
        return "NOT FOUND!\n", 404
    return render_template('post.html', post = post)