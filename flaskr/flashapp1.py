import flask
from flask import request, jsonify

import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import statistics
import time

app = flask.Flask(__name__)
app.config["DEBUG"] = True


yf.pdr_override() # Activate yahoo finance workaround
now = dt.datetime.now() #Runs until todays date
start =dt.datetime(2019,1,1)

AvgGain=15 #Enter Your Average Gain %
AvgLoss=5 #Enter Your Average Loss %
smaUsed=[50,200]
emaUsed=[21]

@app.route('/', methods=['GET'])
def home():

    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"


@app.route('/api/getdata', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        stock =  request.args['id']
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []
    results.append("test test")
    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    df = pdr.get_data_yahoo(stock, start, now)
    # print(df)
    close = df["Adj Close"][-1]
    maxStop = close * ((100 - AvgLoss) / 100)
    Target1R = round(close * ((100 + AvgGain) / 100), 2)
    Target2R = round(close * (((100 + (2 * AvgGain)) / 100)), 2)
    Target3R = round(close * (((100 + (3 * AvgGain)) / 100)), 2)

    for x in smaUsed:
        sma = x
        df["SMA_" + str(sma)] = round(df.iloc[:, 4].rolling(window=sma).mean(), 2)
    for x in emaUsed:
        ema = x
        df['EMA_' + str(ema)] = round(df.iloc[:, 4].ewm(span=ema, adjust=False).mean(), 2)

    sma50 = round(df["SMA_50"][-1], 2)
    sma200 = round(df["SMA_200"][-1], 2)
    ema21 = round(df["EMA_21"][-1], 2)
    low5 = round(min(df["Low"].tail(5)), 2)

    pf50 = round(((close / sma50) - 1) * 100, 2)
    check50 = df["SMA_50"][-1] > maxStop
    pf200 = round(((close / sma200) - 1) * 100, 2)
    check200 = ((close / df["SMA_200"][-1]) - 1) * 100 > 100
    pf21 = round(((close / ema21) - 1) * 100, 2)
    check21 = df["EMA_21"][-1] > maxStop
    pfl = round(((close / low5) - 1) * 100, 2)
    checkl = pfl > maxStop


    results.append("Current Stock: " + stock + " Price: " + str(round(close, 2)))
    results.append("21 EMA: " + str(ema21) + " | 50 SMA: " + str(sma50) + " | 200 SMA: " + str(sma200) + " | 5 day Low: " + str(low5))
    results.append("-------------------------------------------------")
    results.append("Max Stop: " + str(round(maxStop, 2)))
    results.append("Price Targets:")
    results.append("1R: " + str(Target1R))
    results.append("2R: " + str(Target2R))
    results.append("3R: " + str(Target3R))
    results.append(str(low5) + "From 5 Day Low " + str(pfl) + "% -Within Max Stop: " + str(checkl))
    results.append("From 21 day EMA " + str(pf21) + "% -Within Max Stop: " + str(check21))
    results.append("From 50 day SMA " + str(pf50) + "% -Within Max Stop: " + str(check50))
    results.append("From 200 Day SMA " + str(pf200) + "% -In Danger Zone (Over 100% from 200 SMA): " + str(check200))


    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)

app.run(host='0.0.0.0', port=80)