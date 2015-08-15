import tweepy
import json
from pymongo import Connection
from bson import json_util
from tweepy.utils import import_simplejson


json = import_simplejson()
mongocon = Connection()

db = mongocon.test
col = db.tweets_tail

consumer_key = ''
consumer_secret = ''

access_token_key = ''
access_token_secret = ''

auth1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth1.set_access_token(access_token_key, access_token_secret)

class StreamListener(tweepy.StreamListener):
    mongocon = Connection()
    db = mongocon.test
    col = db.tweets_tail
    json = import_simplejson()

    
    def on_status(self, tweet):
        print 'Ran on_status'

    def on_error(self, status_code):
        return False

    def on_data(self, data):
        if data[0].isdigit():
            pass
        else:
            s = json.loads(data)
            try:
                if s["place"] is not None:
                    col.insert(s["place"])
                    print(s["place"])
	    except:
		pass		            


l = StreamListener()
streamer = tweepy.Stream(auth=auth1, listener=l)
setTerms = ['#JaiHind', '#IndependenceDay']
streamer.filter(track = setTerms)
