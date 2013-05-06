#!/usr/bin/env python

import webapp2
import tweepy
import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
CALLBACK = ""
if os.environ.get('SERVER_SOFTWARE','').startswith('Development'):
    CALLBACK = 'http://127.0.0.1:8080/oauth/callback'
else:
    CALLBACK = 'http://ninstweeter.appspot.com/oauth/callback'

print os.getcwd()
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

def render(template_name, template_values):
        path = os.path.join(os.path.dirname(__file__), 'templates/' + template_name)
        return template.render(path, template_values)

class AppAccount(db.Model):
        userid = db.StringProperty()
        # implicit property "accounts"

class TwitterAccount(db.Model):
        screenName = db.StringProperty()
        access_key = db.StringProperty()
        access_secret = db.StringProperty()
        appAccount = db.ReferenceProperty(AppAccount, collection_name="accounts")
                               
class Tweet(db.Model):
        text=db.StringProperty()
        statusid = db.IntegerProperty()
        twitterAccount = db.ReferenceProperty(TwitterAccount, collection_name="tweets")
               
class MainHandler(webapp2.RequestHandler):
    def get(self):        
        user = users.get_current_user()
        url = ""
        twitacc = []
        if user:
                url = users.create_logout_url("/")
                account = AppAccount.get_by_key_name(user.user_id())
                if account == None: # create the account
                        account = AppAccount(key_name = user.user_id())
                        account.put()
                        print "added user " + user.user_id()
                else:
                        for acc in account.accounts:
                            twitacc.append(acc.screenName)
        else:
                self.redirect(users.create_login_url("/"))
        self.response.out.write(render("index.html", {'url':url, 'accounts': twitacc}))
        #auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
        #self.redirect(auth.get_authorization_url())
    def post(self):
        self.response.out.write(self.request.get("screenName"))
        
class CallbackHandler(webapp2.RequestHandler):
        def get(self):
                user = users.get_current_user()
                if not user :
                    self.redirect("/") 
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
                        return 
                account = AppAccount.get_by_key_name(user.user_id())
                if account == None:
                    print "account does not exist!"
                    return
                api = tweepy.API(auth)
                me = api.me()
                found=False
                for twitteraccount in account.accounts:
                    if twitteraccount.screenName.lower() == me.screen_name.lower():
                        # update the tokens
                        twitteraccount.access_key = auth.access_token.key
                        twitteraccount.access_secret = auth.access_token.secret
                        twitteraccount.put()
                        self.response.out.write("token updated")
                        found=True
                        break
                if found==False:
                    self.response.out.write("account added")
                    # add account
                    twitacc = TwitterAccount(appAccount=account,
                                             screenName=me.screen_name,
                                             access_key=auth.access_token.key,
                                             access_secret=auth.access_token.secret)
                    twitacc.put()
        
                    
class AuthenticateHandler(webapp2.RequestHandler):
        def get(self):
                auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
                self.redirect(auth.get_authorization_url())
class StatusUpdateHandler(webapp2.RequestHandler):
        def get(self):
                auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
                auth.set_access_token("1010862853-BOjD3KZjBnW4fpPARVFQPbWgKtDZGom7JOgjerZ", "uFd3kpWyHdgjTXZAUEjmrizzd6MdjXbKI4tbFiHAtE")
                api=tweepy.API(auth)
                q=TweetList.all().run()
                for tweet in q:
                        print "tweeting ID!!"
                        print tweet.tweets[0]
                        try:
                                api.retweet(long(tweet.tweets[0]))
                        except:
                                print "oops"
                        del tweet.tweets[0]
                        tweet.put()
                        break

class UserCheck(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.response.out.write(user.nickname())
        else:
            self.response.out.write("uh oh")
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/usercheck', UserCheck),
    ('/auth', AuthenticateHandler),
    ('/oauth/callback', CallbackHandler),
    ('/statusupdate', StatusUpdateHandler)
], debug=True)
