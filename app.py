# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask import Flask, request
import json


from binance.client import Client
import math


app = Flask(__name__)



api_key = 'your key here'
api_secret = 'your secret here'

client = Client(api_key, api_secret)


minqtydata = {
    'C98USDT' : 11,
    'BTCUSDT' : 0.001
    }

def get_symbol_data(currency_symbol):    
    info1 = client.futures_exchange_info() 
    info1 = info1['symbols']
    mark = client.futures_symbol_ticker(symbol=currency_symbol)['price']
    for x in range(len(info1)):
        if info1[x]['symbol'] == currency_symbol:
            step=info1[x]['filters'][2]['stepSize']
            maxqty = info1[x]['filters'][2]['maxQty']
    return step, maxqty, mark


def get_usdt():    
    info = client.futures_account_balance() 
    for x in range(len(info)):
        if info[x]['asset'] == 'USDT':
            return info[x]['balance']
    return None

def getsize(a, MinClip,price, lev = 1, sf = 0.95 ):
    v = math.floor(a*lev*sf/float(price)/float(MinClip))
    w=  float(MinClip)
    return v/(1/w)


def trade_qty(symbol,data):

    bal = float(get_usdt())
    (precision, maxqty, price) = get_symbol_data(symbol)
    lev = 1
    sf = 0.95
    maxlev = 10
    size = getsize(bal,precision,price,lev,sf)
    client.futures_change_leverage(symbol=symbol,leverage=lev)
    x=0
    try:
        minqty = data[symbol]
    except:
        minqty = 30
    while size< float(minqty):
        if lev<maxlev:
            lev = lev+1
            client.futures_change_leverage(symbol=symbol,leverage=lev)
        size = getsize(bal,precision,price,lev,sf)
        x+=1
        if x>10:
            break    
        
    if size>float(maxqty):
        size = maxqty
    
    return size

def close_positions():
    x=client.futures_account()['positions']
    for z in range(len(x)):
        if float(x[z]['positionAmt'])!=0:
            if x[z]['positionSide']=='LONG':
                client.futures_create_order(symbol=x[z]['symbol'], side='SELL', type='MARKET', quantity=float(x[z]['positionAmt']), positionSide="Long")
            if x[z]['positionSide']=='SHORT':
                client.futures_create_order(symbol=x[z]['symbol'], side='BUY', type='MARKET', quantity=-float(x[z]['positionAmt']), positionSide="Short")



def order(action, symbol, data):
        
    print('closing orders')   
    close_positions()
    client.futures_cancel_all_open_orders(symbol=symbol)
    
    print('sending order')   
    qty = trade_qty(symbol, data)
   
    if action=='buy':
        client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty, positionSide="Long")
        tp=round(float(client.futures_position_information(symbol=symbol)[0]['markPrice'])*1.02,4)
        client.futures_create_order(symbol=symbol, type="TRAILING_STOP_MARKET", callbackRate=0.3, side='SELL', quantity=qty, activationPrice=tp, positionSide="Long")
        #sl = round(float(client.futures_position_information(symbol=symbol)[0]['markPrice'])*0.997,4)
        #client.futures_create_order(symbol=symbol, type="STOP_MARKET", side='SELL', quantity=qty, positionSide="Long", stopPrice = sl)
    if action=='sell':
        client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty, positionSide="Short")
        tp=round(float(client.futures_position_information(symbol=symbol)[0]['markPrice'])*0.98,4)
        client.futures_create_order(symbol=symbol, type="TRAILING_STOP_MARKET", callbackRate=0.3, side='BUY', quantity=qty, activationPrice=tp, positionSide="Short")
        #sl = round(float(client.futures_position_information(symbol=symbol)[0]['markPrice'])*1.003,4)
        #client.futures_create_order(symbol=symbol, type="STOP_MARKET", side='BUY', quantity=qty, positionSide="Short", stopPrice = sl)
        
    print(symbol,'_',qty,'_',action)

@app.route('/')
def hello():
    return 'Hello'

@app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)
    action = data['action']
    ticker = data['ticker'].split('PERP')[0]
    try:
        order(action,ticker,minqtydata)
    except:
        pass
    
    return 'success'
