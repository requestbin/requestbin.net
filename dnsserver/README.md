# dnsbin
The request.bin of DNS request

DNSBin is a simple tool to test data exfiltration through DNS and help test vulnerability like RCE or XXE when the environment has significant constraint. The project is in two parts, the first one is the web server and it's component. It offers a basic web UI, for most cases you won't need more than this. The client part offers a python script which allows data to be transfered in both direction through DNS using the web service. 

This project is based on https://github.com/HoLyVieR/dnsbin

## Demo

http://requestbin.net/dns

## Setup and installation

### DNS

The current DNS setup that I have for the demo server is the following one. Do note that I did this with trial and error, so the setup may be overcomplicated or may have issues. If you are more knowledgeable feel free to open an issue. 

 - Add a "A" record for the domain "ns1.requestbin.net" that points to "<an IP>".
 - Add a "A" record for the domain "ns2.requestbin.net" that points to "<an IP>".
 - Add a "NS" record for the domain "d.requestbin.net" with the value "ns1.requestbin.net".
 - Add a "NS" record for the domain "d.requestbin.net" with the value "ns2.requestbin.net". 

### Web Hosting

It's highly recommended to start the DNS receiver and WebSocket endpoint with the Node.JS module ["forever"](https://www.npmjs.com/package/forever).

> forever start index.js

After that, node open port 53 and 8080, please open firewall with udp:53, tcp:53 and tcp:8080
