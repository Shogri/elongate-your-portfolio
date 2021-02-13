import twint
import time
import requests
import json
import string
import nltk
import nlp

# Constants
TICK_TIME = 1.0
USERNAME = "StonkRat"

def get_ticker():
    # Test HTTP Request
    # r = requests.get('http://d.yimg.com/autoc.finance.yahoo.com/autoc?query=tesla&region=1&lang=en&callback=YAHOO.Finance.SymbolSuggest.ssCallback')
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc"
    params = {
        'query':'tesla',
        'region':'1',
        'lang':'en',
        'callback':'YAHOO.Finance.SymbolSuggest.ssCallback'
    }
    r = requests.get(url=url, params=params)
    content = r.content
    content = content.decode()
    content = str(content[39:-2])

    print(str(json.loads(content)))

def main():
    # Configure
    c = twint.Config()
    c.Username = USERNAME
    c.Limit = 1
    c.Hide_output = True
    c.Store_object = True

    # Run
    twint.run.Search(c)
    print("DONE INITIAL SEARCH")

    # Store output
    tweets = twint.output.tweets_list
    latest_tweet_date = " ".join(tweets[0].datetime.split(" ")[:2])
    print("Latest tweet: " + tweets[0].tweet)

    print("Waiting for New Tweets...")
    starttime = time.time()
    while True:

        # Prepare new list and new latest tweet date
        twint.output.tweets_list = []
        latest_tweet_date = " ".join(tweets[0].datetime.split(" ")[:2])

        c.Since = latest_tweet_date
        twint.run.Search(c)
        tweets = twint.output.tweets_list
        # print("Latest tweet: " + tweets[0].tweet)
        # print("Number of tweets since {}: {}".format(latest_tweet_date, len(tweets)))

        # Check if a new tweet is detected
        if len(tweets) > 1:
            print("New Tweet: \"{}\"".format(tweets[0].tweet))

        time.sleep(TICK_TIME - ((time.time() - starttime) % TICK_TIME))

if __name__ == '__main__':
    main()
    