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

### 2. Setup DNS Server
### 3. Setup Blog

## References:
- https://github.com/Runscope/requestbin
- https://github.com/HoLyVieR/dnsbin
