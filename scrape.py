import twint
import time
import requests
import json
import string
import nlp
import datetime
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
import matplotlib.animation as animation
from yahoo_fin import stock_info as si
import gui

# Constants
TICK_TIME = 3.0
USERNAME = "StonkRat"

def get_ticker(company_name):
    if company_name == "Bitcoin":
        return "BTC-USD"

    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc"
    params = {
        'query':company_name,
        'region':'1',
        'lang':'en',
        'callback':'YAHOO.Finance.SymbolSuggest.ssCallback'
    }
    r = requests.get(url=url, params=params)
    content = r.content
    content = content.decode()
    content = str(content[39:-2])

    myjson = json.loads(content)
    result = myjson['ResultSet']['Result']

    if len(myjson['ResultSet']['Result']) == 0:
        return ""

    # Return the symbol
    return result[0]['symbol']

def drawGraph(tickerQueue):
    ticker = tickerQueue.get()
    xar = []
    yar = []
    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    ax.set_xlim([datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(minutes=5)])
    line, = plt.plot_date(xar, yar, '-')

    def animate(i):
        nonlocal ticker
        if not tickerQueue.empty():
            ticker = tickerQueue.get()
            print("Got new value in Graph Process: {}".format(ticker))

        if ticker != "":
            xar.append(datetime.datetime.now())
            yar.append(si.get_live_price(ticker))
        line.set_data(xar, yar)
        fig.gca().relim()
        fig.gca().autoscale_view()

        return line,

    ani = animation.FuncAnimation(fig, animate, interval=200)

    plt.tick_params(axis='x', which='major', labelsize=7)
    plt.tick_params(axis='y', which='major', labelsize=7)
    plt.xlabel('Timestamp')
    plt.ylabel('Price in $USD')
    plt.show()

if __name__ == '__main__':
    # Graph Process kickoff:
    q = Queue()
    q.put("")
    p = Process(target=drawGraph, args=(q,))
    p.start()

    # Gui Kickoff
    guiq = Queue()
    guiq.put({"",""})
    guip = Process(target=gui.startGui, args=(guiq,))
    guip.start()

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
    
    # Track the Ticker from the latest tweet
    result_list = nlp.nlp(tweets[0].tweet)

    for word in result_list:
        ticker = get_ticker(word)
        print("Found ticker: {}".format(ticker))
    
    q.put(ticker)

    print("Waiting for New Tweets...")
    starttime = time.time()
    while True:

        # Prepare new list and new latest tweet date
        twint.output.tweets_list = []
        latest_tweet_date = " ".join(tweets[0].datetime.split(" ")[:2])

        c.Since = latest_tweet_date
        twint.run.Search(c)
        tweets = twint.output.tweets_list

        # Check if a new tweet is detected
        if len(tweets) > 1:
            print("New Tweet: \"{}\"".format(tweets[0].tweet))

            result_list = nlp.nlp(tweets[0].tweet)

            for word in result_list:
                ticker = get_ticker(word)
                print("Found ticker: {}".format(ticker))
            
            q.put(ticker)

        time.sleep(TICK_TIME - ((time.time() - starttime) % TICK_TIME))


    