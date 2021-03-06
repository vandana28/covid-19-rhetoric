import json
import os
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import re

######################################################################################################################
# Class TwitterAuthenticator
# - Handles Twitter authentication and the connection to Twitter Streaming API.
######################################################################################################################	
class TwitterAuthenticator():

  def __init__(self):
    #Get the dictionary of twitter OAth keys
    self.this_folder = os.path.dirname(os.path.abspath(__file__))
    self.keys_file = os.path.join(self.this_folder, "twitterKeys.json")

  def authenticate_twitter_app(self):
    try:
      twitterKeyFile = open(self.keys_file)
    except OSError:
      print("Error! Cannot open: ", self.keys_file)

    twitterKeys = json.load(twitterKeyFile)

    #API key & API secret key goes here...
    auth = OAuthHandler(twitterKeys.get("consumer_key"),
                        twitterKeys.get("consumer_secret"))

    #API Access token & secret token
    auth.set_access_token(twitterKeys.get("access_token_key"),
                          twitterKeys.get("access_token_secret"))
    return auth

######################################################################################################################
# Class TwitterStreamer
# - Class for streaming and processing live tweets.
######################################################################################################################	
class TwitterStreamer():

  def __init__(self):
    self.twitter_authenticator = TwitterAuthenticator()

  def stream_tweets(self, fetched_tweet_filename, hash_tag_list):
   
    listener = TwitterListener(fetched_tweet_filename)
    auth = self.twitter_authenticator.authenticate_twitter_app()

    stream = Stream(auth, listener)

    # This line filters Twitter Streams to capture data by the keywords: 
    stream.filter(track=hash_tag_list)

######################################################################################################################
# Class TwitterListener
######################################################################################################################
class TwitterListener(StreamListener):
  
  def __init__(self, fetched_tweet_filename):
    self.fetched_tweets_filename = fetched_tweet_filename

  def on_data(self, data):
    try:
      #Deserialize strin and create python object
      jsonTweets = json.loads(data)

      #Append to the file...
      with open(self.fetched_tweets_filename, "a") as f:
        json.dump(jsonTweets,f, indent=2)
    except BaseException as e:
      print("Error on_data: %s", str(e))
    return True

  def on_error(self, status):
    # Check if we're being rate limited for making too many requests to Twitter
    if status == 420:
      return False
    print(status)

######################################################################################################################
# Class TwitterClient
# - Client API functions
######################################################################################################################
class TwitterClient():
  def __init__(self, twitter_user=None):
    self.auth = TwitterAuthenticator().authenticate_twitter_app()
    self.twitter_client = API(self.auth)
    self.twitter_user = twitter_user

  def get_twitter_client_api(self):
    return self.twitter_client

  #########################################################
  # Function get_user_timeline_tweets
  # - Gets the specified user's timeline tweets 
  # - num_tweets is the # of tweets to get from timeline
  # - if no user, gets the API user's tweets
  #########################################################
  def get_user_timeline_tweets(self, screen_name, num_tweets):
    my_tweets = []
    for tweet in Cursor(self.twitter_client.user_timeline, tweet_mode="extended", screen_name=screen_name).items(num_tweets):
      my_tweets.append(tweet)
    return my_tweets

  #########################################################
  # Function get_friend_list
  # - Gets the specified user's twitter friends 
  # - num_friends is the # of tweets to get from timeline
  # - if no user, gets the API user's friends
  #########################################################
  def get_friend_list(self, num_friends):
    friend_list = []
    for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
      friend_list.append(friend)
    return friend_list

  #########################################################
  # Function search_for_tweet
  # - search query string of 500 characters maximum
  #########################################################
  def search_for_tweet(self, query_str, count):
    #Check character count... 
    if(len(query_str) >= 500):
      print("Exceeded Max character count in query!")
      return False
    else:
      found_tweets = []
      for tweet in Cursor(self.twitter_client.search, q=query_str, count=count).items(count):
        found_tweets.append(tweet)
      return found_tweets
