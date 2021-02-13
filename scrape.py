import twint
import time

# Constants
TICK_TIME = 5.0

# Configure
c = twint.Config()
c.Username = "StonkRat"
c.Limit = 1
c.Hide_output = True
c.Store_object = True

# Run
twint.run.Search(c)
print("DONE INITIAL SEARCH")

# Store output
tweets = twint.output.tweets_list
latest_tweet_date = " ".join(tweets[0].datetime.split(" ")[:2])

starttime = time.time()
while True:

    # Prepare new list and new latest tweet date
    twint.output.tweets_list = []
    latest_tweet_date = " ".join(tweets[0].datetime.split(" ")[:2])

    c.Since = latest_tweet_date
    twint.run.Search(c)
    tweets = twint.output.tweets_list
    print("Latest tweet: " + tweets[0].tweet)
    print("Number of tweets since {}: {}".format(latest_tweet_date, len(tweets)))

    # Check if a new tweet is detected
    if len(tweets) > 1:
        print("NEW TWEET DETECTED, DO ANALYSIS ON TWEET HERE")

    time.sleep(TICK_TIME - ((time.time() - starttime) % TICK_TIME))
    