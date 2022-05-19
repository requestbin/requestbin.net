# requestbin.net - The Next-Gen RequestBin

## Information
**Project:** requestbin.net

**Demo:** https://requestbin.net

**Author:** cuongmx@gmail.com

**Repository:** https://github.com/requestbin/requestbin.net

**Blog:** https://requestbin.net/post/whats-new-in-the-next-gen-requestbin

## Release notes
**Release date:** 05 May 2022

**Current verion:** 2.0

**Features:**
1. Support both DNS and HTTP on an unique ID
2. Support automatically storing the list of IDs
3. Blog

## Installation
### Pre-installation Requirements
To install an instance like requestbin.net, you need some bellow things:
1. A domain with full DNS control
2. A Heroku account
3. A VPS run linux server
4. A mongodb server

There are 3 parts in a requestbin.net system:
1. Main website run on Heroku
2. DNS server for DNSBin
3. Blog

### 1. Setup website on Heroku
First, clone this repo using git:

`$ git clone https://github.com/requestbin/requestbin.net.git`

From the project directory, create a Heroku application:

`$ heroku create`

Set an environment variable to indicate production:

`$ heroku config:set SERVER_NAME=requestbin.net`

`$ heroku config:set MONGODB_URI=mongodb://user:Passsword@exampleserver:port/db?retryWrites=true`

Now just deploy via git:

`$ git push heroku master`

It will push to Heroku and give you a URL that your own private RequestBin will be running.

**Important:** The RequestBin Next Gen run like "Multi-Tenant". So, the domain config step bellow is very important:
Set main domain as normal:

`$ heroku domains:add requestbin.net`

The CNAME got after this command like whispering-xxx.herokudns.com. is use for DNS config.

Next, add wildcard subdomain for "Multi-Tenant"

`$ heroku domains:add *.b.requestbin.net`

The CNAME got after this command like whispering-example.herokudns.com. must be memory for **next step.**

### 2. Setup DNS Server
This step must be done on the prepared server.
#### Clone this repo using git:

`$ git clone https://github.com/requestbin/requestbin.net.git`

#### Edit dnsbin.sh

`$ cd dnsbin/`

`$ mv dnsbin.sh.example dnsbin.sh`

Change MONGODB_URI and WORK_PATH as your system. Especially, change the **CNAME** as the CNAME which you got after config *.b.requestbin.net at last step.

#### Setup Iptables to forward port 53
Because you cannot open directly port 53, you must open another and forward port via Iptables via bellow rules:
```
-A PREROUTING -i eth0 -p tcp -m tcp --dport 53 -j REDIRECT --to-ports 8853
-A PREROUTING -i eth0 -p udp -m udp --dport 53 -j REDIRECT --to-ports 8853
-A INPUT -m state --state NEW -m tcp -p tcp --dport 53 -j ACCEPT
-A INPUT -m state --state NEW -m udp -p udp --dport 53 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 8853 -j ACCEPT
-A INPUT -m state --state NEW -m udp -p udp --dport 8853 -j ACCEPT
```

#### Setup supervisor
Read [here](https://www.codingforentrepreneurs.com/blog/hello-linux-setup-gunicorn-and-supervisor/) for the guide to install supervisor

After that, use the file at `dnsbin/supervisor.conf` for the dnsbin application.

#### DNS Config

On this step, you must use the DNS controller to add 2 records bellow:

 - Add a "A" record for the domain "ns1.requestbin.net" that points to "the server ip".
 - Add a "NS" record for the domain "b.requestbin.net" with the value "the server ip".

### 3. Setup Blog

The blog on requestbin.net/blog is automatically synchronized from our Github repo https://github.com/requestbin/blog

You can setup a repo like the requestbin/blog with bellow steps:

#### Edit the blogsync.sh

```
$ cd blogsync
$ mv blogsync.sh.example blogsync.sh
```
Change MONGODB_URI, BLOG_REPO as yours. The BLOG_REPO's format is `requestbin/blog`

#### Run synchronize

`$ bash blogsync.sh`

You can run it periodically by installing via crontab.

## References:
- https://github.com/Runscope/requestbin
- https://github.com/HoLyVieR/dnsbin
