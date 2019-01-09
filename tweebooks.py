# Tweebooks- by Luna Winters
# This bot will generate markov style tweets from your twitter.
#
#The MIT License (MIT)
#
#Copyright (c) 2015 Luna Winters
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import sys
import tweepy
import os.path
import json
import re
import markovify
import random
from time import gmtime, strftime, sleep

# == OAuth Authentication ==
#
# This mode of authentication is the new preferred way
# of authenticating with Twitter.

# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")
consumer_key=""
consumer_secret=""

# The access tokens can be found on your applications's Details
# page located at https://dev.twitter.com/apps (located
# under "Your access token")
# These are the tokens for the source twitter account.
access_token=""
access_token_secret=""

#Tokens for tweeting out
publish_token = ""
publish_token_secret = ""

#Authenticate
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.secure = True
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

#Authenticate publisher
auth_publish = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.secure = True
auth_publish.set_access_token(publish_token, publish_token_secret)

publish_api = tweepy.API(auth_publish)

url_regex = r"https?:\/\/(www\.)?[A-Za-z0-9.\/]*"
un_regex = r"@[A-Za-z0-9_]*\s"

tweets = []

def save_file():
    with open('tweets.json', 'w') as outfile:
        json.dump(tweets, outfile, indent=4)

def get_tweets():
    count = 0
    #How far back to check, you might want to set this to a large number for the first run to 'seed' the file
    max = 100 
    for status in (tweepy.Cursor(api.user_timeline).items(max)):
        count +=1
        text = status.text
        if not re.search(r"^RT",text):
            if not status.text in tweets:
                text = re.sub(un_regex,"",text) #Removes usernames from the source
                text = re.sub(url_regex,"",text) #Removes URLs from the source
                tweets.append(text)

def load_tweets():
    global tweets
    json_data=open('tweets.json').read()
    tweets = json.loads(json_data)
    print("Tweets loaded")

def generate_markov():
    sentences = ""
    #This splits each tweet by periods, and by newlines, then processes each line as a sentence
    for tweet in tweets:
        split = tweet.split('.')
        for s in split:
            sentences += s+"\n"
    text_model = markovify.NewlineText(sentences)
    return text_model.make_short_sentence(140)


def run ():
    get_tweets()
    save_file()
    text = generate_markov()
    timef =  strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print(timef + " | "+text)
    publish_api.update_status(text)


if os.path.exists("tweets.json"):
    load_tweets()

while True:
    sleep(60*random.randint(15,66)) #Probably better to remove this and put it in a crontab
    run()
