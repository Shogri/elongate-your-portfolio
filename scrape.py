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
import buy
import tkinter as tk
from tkinter import ttk
from tkinter import * 

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

def getInputBoxValue():
    userInput = Amount.get()
    return userInput

# this is the function called when the button is clicked


def scrape(tickerQueue):
    # buy.buy_stock("GOOG", 3000)
    ticker = ""
    # Graph Process kickoff:
    q = Queue()
    q.put(ticker)
    p = Process(target=drawGraph, args=(q,))
    p.start()

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
            
            if ticker != "":
                q.put(ticker)
                buy.buy_stock(ticker, 3000)

        time.sleep(TICK_TIME - ((time.time() - starttime) % TICK_TIME))

if __name__ == '__main__':
    # Scraper Kickoff
    tickerQueue = Queue()
    scraperProcess = Process(target=scrape, args=(tickerQueue,))
    scraperProcess.start()
    print("Scraper Process Starting...")

    root = Tk()

    tweet_var = StringVar()
    tweet_var.set("No tweets to show")

    ticker_var = StringVar()
    ticker_var.set("No tickers to show")

    company_var = StringVar()
    company_var.set("No Company")

    buyamount_var = StringVar()
    buyamount_var.set('0')

    def btnClickFunction():
        print('clicked')
        value = getInputBoxValue()
        buyamount_var.set(value)
        root.update()
        print("Buyamount: {}".format(buyamount_var.get()))

    buyamount_wrapper = [buyamount_var]

    # This is the section of code which creates the main window
    root.geometry('666x442')
    root.configure(background='#F0F8FF')
    root.title('ElonBot')


    # This is the section of code which creates the a label
    Label(root, text='Tweet', bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=71, y=31)


    # This is the section of code which creates the a label
    Label(root, text='Detected Company/Ticker', bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=400, y=33)

    # This is the section of code which creates a text input box
    Amount=Entry(root)
    Amount.place(x=251, y=355)

    # This is the section of code which creates a button
    Button(root, text='Set Auto-purchase ($USD)', bg='#DBDBDB', font=('arial', 12, 'normal'), command=btnClickFunction).place(x=393, y=349)

    Label(root, textvariable=tweet_var, bg='#F0F8FF', font=('courier', 12, 'bold')).place(x=74, y=80)
    Label(root, textvariable=ticker_var, bg='#F0F8FF', font=('courier', 12, 'bold')).place(x=402, y=76)
    Label(root, text='Pre-Set Buy Amount:', bg='#F0F8FF', font=('arial', 12, 'bold')).place(x=125, y=392)
    Label(root, textvariable=buyamount_var, bg='#F0F8FF', font=('courier', 12, 'bold')).place(x=296, y=392)

    root.mainloop()

    