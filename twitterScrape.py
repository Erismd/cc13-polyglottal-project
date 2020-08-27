import tweepy
import re
from tweepy import OAuthHandler
from textblob import TextBlob
import os
from os.path import join, dirname
from dotenv import load_dotenv
import pandas as pd
import time
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


class TwitterClient(object):
    
    # Set up tweepy authorization
    def __init__(self):
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        consumer_key = os.environ.get("CONSUMER_KEY")
        consumer_secret = os.environ.get("CONSUMER_SECRET")
        access_token = os.environ.get("ACCESS_TOKEN")
        access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

        try:
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        except:
            print("Error: Authentication Faild")


    # utility function to clean tweet text
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    # search by the username
    def search_user(self, user):

        username = user
        count = 10
        try:
            # Creation of query method using parameters
            tweets = tweepy.Cursor(
                self.api.user_timeline, id=username).items(count)

            # Pulling information from tweets iterable object
            tweets_list = [[tweet.text]
                           for tweet in tweets]
            # print(tweets_list)
            # Creation of dataframe from tweets list
            # Add or remove columns as you remove tweet information
            tweets_df = pd.DataFrame(tweets_list)
        except BaseException as e:
            print('failed on_status,', str(e))
            time.sleep(3)

    # search by word
    def search_text(self, text):

        text_query = text
        count = 20
        try:
            # Creation of query method using parameters
            tweets = tweepy.Cursor(self.api.search, q=text_query).items(count)

            # Pulling information from tweets iterable object
            tweets_list = [[self.clean_tweet(tweet.text)]
                           for tweet in tweets]
            print(tweets_list)
        # Creation of dataframe from tweets list
        # Add or remove columns as you remove tweet information
            tweets_df = pd.DataFrame(tweets_list)

        except BaseException as e:
            print('failed on_status,', str(e))
            time.sleep(3)


    # utility function to classify sentiment of passed tweet
    def get_tweet_sentiment(self, tweet):

        # create textBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
         # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'


    # main function to fetch tweets and parse them
    def get_tweets(self, query, count=10):

        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionaly to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet["text"] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            print("Error : " + str(e))

    # search by username
    def get_tweets_username(self, username, count=10):

        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch by username
            fetched_tweets = self.api.user_timeline(id=username, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionaly to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet["text"] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(
                    tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            print("Error : " + str(e))

st.title("Twitter Sentiment Analysis")


def main():

    #streamlit : widges
    #search type
    st.sidebar.header("Search Tool")
    searchtype = st.sidebar.radio('Choose the search type :', ("Username", "Keyword"))
    tweetamount = st.sidebar.slider("Amount of Tweet", min_value=10, max_value=200)
    title = st.sidebar.text_input('Search from Keyword :', 'Penguins')
    username = st.sidebar.text_input('Search from Username :')
    searchinput = st.sidebar.button("Search")

    # when the button get 
    if searchinput:

        # call function to get tweets
        api = TwitterClient()
        
        #search by keyword if keyword was chosen
        if searchtype == "Keyword" :
            # creat object of TwitterClient class
            tweets = api.get_tweets(query=title, count=tweetamount)

        #search by username if username was chosen
        if searchtype == "Username" : 
            tweets = api.get_tweets_username(username=username, count=tweetamount)

        # pick positive tweets from tweets
        posiTweets = [
            tweet for tweet in tweets if tweet['sentiment'] == 'positive']
        print("★★★★★★★★Positive tweets percentage: {} %".format(
            100*len(posiTweets)/len(tweets)))
        negaTweets = [
            tweet for tweet in tweets if tweet['sentiment'] == 'negative']
        print("☆☆☆☆☆☆☆☆Negative tweets percentage: {} %".format(
            100*len(negaTweets)/len(tweets)))
        print("Neutral tweets percentage: {} %".format(
            100*(len(tweets)-(len(negaTweets)))/len(tweets)))

        # print first 5 positive tweets
        print("\n\nPositive Tweets:")  
        for tweet in posiTweets[:10]:
            printpositive = tweet['text']
            print(tweet['text'])

        # print first 5 negative tweets
        print("\n\nNegative tweets:")
        for tweet in negaTweets[:10]:
            printnegative = tweet['text']
            print(tweet['text'])

        

        #streamlit header
        st.write('keyword : ', title)
        st.write('From ', tweetamount, ' tweets')
        st.write("Here's the result of your search:")
        #table that has percentages
        st.write(pd.DataFrame({
            'Positive': [format(100*len(posiTweets)/len(tweets))],
            'Negative': [format(100*len(negaTweets)/len(tweets))]
        }))
        # pie chart
        label = ['Positive', 'Negative']
        positive = format(100*len(posiTweets)/len(tweets))
        negative = format(100*len(negaTweets)/len(tweets))
        x = np.array([positive, negative])
        plt.pie(x, labels=label, counterclock=False,
                startangle=90, autopct="%1.1f%%", pctdistance=0.7)
        plt.axis('equal')
        st.pyplot()

        # table to show positive and negative tweets
        st.table(pd.DataFrame({
             "Positive" : [tweet["text"] for tweet in posiTweets]
        }))
        st.table(pd.DataFrame({
             "Negative" :  [tweet["text"] for tweet in negaTweets]
        }))



if __name__ == "__main__":
    main()
