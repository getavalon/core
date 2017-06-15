@echo off
set PYTHONPATH=%~dp0
call add python36
call add python3-mongo
call add python3-yaml
call add python-mindbender

set MINDBENDER_DEBUG=Yes
set MINDBENDER_ROOT=C:\Users\marcus\Dropbox\projects\mindbender\mindbender-example\projects
set MINDBENDER_LOCATION=http://192.168.99.100:8080
set MINDBENDER_MONGO=mongodb://localhost:27017
rem set MINDBENDER_MONGO=mongodb://mindbender:Napoleon2016@192.168.1.101:27017
rem set MINDBENDER_MONGO=mongodb://marcus:WhoRu2DaY@213.115.140.134:27017
rem set MINDBENDER_MONGO=mongodb://artist:Napoleon2016@213.115.140.134:27017
rem set MINDBENDER_MONGO=mongodb://colorbleed:ColorBleed@82.69.0.67:27017

python -u -m mindbender --loader
