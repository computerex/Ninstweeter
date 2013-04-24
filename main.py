#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import tweepy

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
CALLBACK = 'http://127.0.0.1:8080/oauth/callback'

secrets=open('secrets','r')
CONSUMER_KEY=secrets.readline().strip()
CONSUMER_SECRET=secrets.readline().strip()
secrets.close()

print CONSUMER_KEY
print CONSUMER_SECRET

'''       
class OAuthToken(db.Model):
    token_key = db.StringProperty(required=True)
    token_secret = db.StringProperty(required=True)
'''    
class MainHandler(webapp2.RequestHandler):
    def get(self):        
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
        self.redirect(auth.get_authorization_url())
        
class CallbackHandler(webapp2.RequestHandler):
        def get(self):
                print "HY"
                request_key = self.request.get("oauth_token")
                request_secret = self.request.get("oauth_verifier")    
                if request_key is None or request_secret is None:
                        print "token_key or token_secret invalid"
                        return
                print "Request Key   : " + request_key
                print "Request Secret: " + request_secret
                auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
                auth.set_request_token(request_key, request_secret)
                try:
                        auth.get_access_token(request_secret)
                except tweepy.TweepError, e:
                        print e
                api = tweepy.API(auth)
                print api.me()
                api.update_status("muhahahaha")
                 
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/oauth/callback', CallbackHandler)
], debug=True)
