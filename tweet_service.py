#!/bin/env python
# encoding: utf-8

"""
Webservice prototype for exposing cell data via
HTTP and JSON/JSONP
"""


DB = 'test'
CELLS_COLLECTION = 'tweets_tail'


import json
import time
import math
import redis
import threading
import signal
import sys
from flask import Flask
from flask import request
from flask import abort
from flask import url_for
from flask import make_response
from flask import Response
from pymongo import Connection
from bson import json_util
from threading import Thread
from geopy.geocoders import Nominatim


geolocator = Nominatim()

red = redis.StrictRedis()

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sys.exit(0)

def tail_mongo_thread():
    db = Connection().test
    coll = db.tweets_tail
    cursor = coll.find({}, {"name" : 1, "_id": 0 },timeout=False)
    ci=0
    while cursor.alive:
        try:
            doc = cursor.next()
            ci += 1
            try:
            	location = geolocator.geocode(doc["name"])
                coords = {}
                coords[0], coords[1] = location.latitude, location.longitude
                jsonified = json.dumps(coords)
                print jsonified
                red.publish('chat', u'%s' % json.dumps(jsonified,default=json_util.default))
            except:
                pass
        except StopIteration:
            pass

def event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe('chat')
    i=0
    for message in pubsub.listen():
        i+=1
        print i
        yield 'data: %s\n\n' % message['data']
    
app = Flask(__name__)
@app.route('/tweets')
def tweets():
   
    url_for('static', filename='map.html')
    url_for('static', filename='jquery-1.7.2.min.js')
    url_for('static', filename='jquery.eventsource.js')
    url_for('static', filename='jquery-1.7.2.js')
    return Response(event_stream(), headers={'Content-Type':'text/event-stream'})

def runThread():
    st = Thread( target = tail_mongo_thread )
    st.start()
    

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    app.before_first_request(runThread)
    app.run(debug=True, host='0.0.0.0')  
