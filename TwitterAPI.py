#!/home/jeffbar/venv/bin/python
# https://help.dreamhost.com/hc/en-us/articles/216128557-Guidelines-for-setting-up-a-Python-file-at-DreamHost
# http://www.learningaboutelectronics.com/Articles/How-to-run-Python-on-a-web-server.php
# specify the location of the Python interpreter on the web server.
# Allow HTML tags to be executed, since the file is an HTML file. Without this, none of the HTML commands will be executed.
import sys

print("Content-type: text/html\n\n")

print("<h1>Twitter API Script</h1>")

print("<br>" + (sys.version))

"""
Created on June 16, 2018
@author: 536693 Jeff Barrett
Python Version: 3.6
"""

print("<h1>Status1: Script Started</h1>")

# ===============================================================================
# In CMD: py -m pip install tweepy
# https://miningthedetails.com/blog/python/TwitterStreamsPythonMySQL/
# Twitter dev account: https://developer.twitter.com/en/apps/13512492 email: barrett_jeffrey@bah.com pw: 8H(%McNde"T6;r(
# Notes: Can use filter function to filter by location (see tweepy examples in documentation)
# Burundi Time Zone is GMT+2 (6 hours ahead of EST)
# ===============================================================================

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import mysql.connector
from mysql.connector import errorcode
import time
import json

print("<h1>Status2: Imports complete</h1>")

# replace mysql.server with "localhost" if you are running via your own server!
#                       server, MySQL user, MySQL pass, Database name:
db = mysql.connector.connect(user='jeff_b', password='HG2012sherin!', host='mysql.wwhgd.dreamhosters.com',
                             database='twitter_api', charset='utf8mb4')

dbc = db.cursor()

# consumer key, consumer secret, access token, access secret from EthnicityGEO twitter App
ckey = "tlC142SM1xHBHhcNNpp9cEJYv"
csecret = "13dCsVOmcVCprPO9kLNBFHrNj7xuwnEeLgi8Ic0eDT0ux3mI0r"
atoken = "839522400865746944-oGmFp4TCWf9TgSzjAU6O2CGSQMyJtdI"
asecret = "3MU63PQINN5u9NOOjzQGQ37plP9fkcMcpRGQaZfVFXKDV"

print("<h1>Status3: Establish DB Connection</h1>")


# id which tweet objects to pull
class Listener(StreamListener):

    def on_data(self, data):
        all_data = json.loads(data)

        # *** Tweet Data ***
        tweet = all_data["text"]  # Not Null

        id_str = all_data["id_str"]  # Not Null - The string representation of the unique identifier for this Tweet

        created_at = all_data["created_at"]  # Not Null - UTC time when this Tweet was created.

        in_reply_to_status_id_str = all_data["in_reply_to_status_id_str"]  # Nullable. If the represented Tweet is a
        # reply, this field will contain the string representation of the original Tweet’s ID.

        in_reply_to_user_id_str = all_data["in_reply_to_user_id_str"]  # Nullable. If the represented Tweet is a
        # reply, this field will contain the string representation of the original Tweet’s author ID. This will not
        # necessarily always be the user directly mentioned in the Tweet.

        in_reply_to_screen_name = all_data["in_reply_to_screen_name"]  # Nullable. If the represented Tweet is a
        # reply, this field will contain the screen name of the original Tweet’s author

        # retweeted_status = all_data["retweeted_status"]  # Users can amplify the broadcast of Tweets authored by other
        # users by retweeting . Retweets can be distinguished from typical Tweets by the existence of a retweeted_status
        # attribute. This attribute contains a representation of the original Tweet that was retweeted. Note that
        # retweets of retweets do not show representations of the intermediary retweet, but only the original Tweet.

        retweet_count = all_data["retweet_count"]  # Int - Number of times this Tweet has been retweeted.

        favorite_count = all_data["favorite_count"]  # Nullable. Indicates approximately how many times this Tweet
        # has been liked by Twitter users.

        # possibly_sensitive = all_data["possibly_sensitive"] # Nullable. This field only surfaces when a Tweet contains
        # a link. The meaning of the field doesn’t pertain to the Tweet content itself, but instead it is an indicator
        # that the URL contained in the Tweet may contain content or media identified as sensitive content. Boolean

        # *** User Data ***
        user_name = all_data["user"]["screen_name"]  # Not Null

        user_description = all_data["user"]["description"]  # Nullable

        user_profile_img_url = all_data["user"]["profile_image_url"]  # Not Null

        language = all_data["lang"]  # Not Null

        #user_followers = all_data["followers_count"]  # Not Null

        # *** Location Data ***
        place = all_data["place"]['full_name']  # Nullable - When present, indicates that the tweet is associated
        # (but not necessarily originating from) a Place.

        user_coordinates = all_data["coordinates"]  # Nullable - Represents the geographic location of this Tweet as
        # reported by the user or client application. The inner coordinates array is formatted as geoJSON
        # (longitude first, then latitude).

        user_location = all_data["user"]["location"]  # Nullable - Location associated with user profile

        user_geo_enabled = all_data["user"]["geo_enabled"]  # Not Null - true/false

        # tweet objects: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object.html
        # objects to add?: default_profile_image, verified

        # if coordinates are not present store blank value otherwise get the coordinates.coordinates value
        if user_coordinates is None:
            final_coordinates = user_coordinates
        else:
            final_coordinates = str(all_data["coordinates"]["coordinates"])

        # if places are not present store blank value otherwise get the place.full_name value
        if place is None:
            final_place = place
        else:
            final_place = str(all_data["place"]['full_name'])

        # insert object values into the db
        dbc.execute(
            "INSERT INTO twitterdata (tweetIDstr, created_at, username, description, usrImgURL, tweet, "
            "place, coordinates, userLocation, geoEnabled, language, rplyOrigTwtID, rplyOrigTwtUsrID, rplyOrigUsrName,"
            "retwtCount, favCount)"  # retwtdStatus, pssblySensitive, userFollowers,
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (id_str, created_at, user_name, user_description, user_profile_img_url, tweet, final_place,
             final_coordinates, user_location, user_geo_enabled, language, in_reply_to_status_id_str,
             in_reply_to_user_id_str, in_reply_to_screen_name, retweet_count, favorite_count))
        # retweeted_status, possibly_sensitive, user_followers,

        db.commit()

        print((created_at, user_name, tweet))

        # print("<h1>" + user_name, tweet + "</h1><br>")

        return True

    def on_error(self, status):
        print(status)
        print("<p>Error: " + status + "</p>")


auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

print("<h1>Status4: Listener Set</h1>")

twitterStream = Stream(auth, Listener())

print("<h1>Status5: Launch Script</h1>")

# https://boundingbox.klokantech.com/ in CSV raw
# bounding box limited to 25 miles in length for each side in granularity
# Burundi locations=[28.8205, -4.55148, 30.8857, -2.145] 29.0007, -4.4693, 30.8498, -2.3097
# Georgetown Conference Center: locations=[-77.0739900936, 38.9085468346, -77.0727798812, 38.9092881898]
# Portland, Oregon: locations=[-122.8377789383,45.4080111041,-122.4730551783,45.6284522464]
# Usage resembles the following: bounding_box:[west_long south_lat east_long north_lat] #check: https://www.latlong.net/
# Gdansk, Poland <bounding><westbc>18.2011234974</westbc><eastbc>19.1239750599</eastbc><northbc>54.5089262747</northbc><southbc>54.1260366458</southbc></bounding>
# Donetsk, Ukraine: 37.5886899177,47.8962066256,38.0633352177,48.1099076449
# long           lat             long            lat
twitterStream.filter(locations=[37.5886899177,47.8962066256,38.0633352177,48.1099076449])
print("<h1>Status6: Set Location</h1>")
# References:
# API from https://pythonprogramming.net/twitter-api-streaming-tweets-python-tutorial/
# https://gist.github.com/ctufts/e38e0588bf6d8f32e99d
# http://www.mikaelbrunila.fi/2017/03/27/scraping-extracting-mapping-geodata-twitter/

print("<h1>Status7: End of Script</h1>")
