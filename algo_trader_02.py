import bybit
import time
import math
import pandas as pd


def autobit(macd_short, macd_long, macd_signal,orderqty):
  key = ""
  secret = ""
  client = bybit.bybit(test=False, api_key=key, api_secret=secret)

  data = client.Kline.Kline_indexPrice(symbol="BTCUSD", interval="5", **{'from':math.floor(time.time())-60*5*200*3}).result()[0]['result']
  for i in range(2):
    i = i+1
    data += client.Kline.Kline_indexPrice(symbol="BTCUSD", interval="5", **{'from':math.floor(time.time())-60*5*200*(3-i)}).result()[0]['result']
    #print(time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(basetime)))
  btcdata = pd.DataFrame(data)
  btcdata["MACD_short"]=btcdata["close"].ewm(span=macd_short).mean() 
  btcdata["MACD_long"]=btcdata["close"].ewm(span=macd_long).mean() 
  btcdata["MACD"]=btcdata.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1) 
  btcdata["MACD_signal"]=btcdata["MACD"].ewm(span=macd_signal).mean() 
  btcdata = btcdata[400:]
  btcdata.index=range(len(btcdata))
  nowposition = client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0]['result']['side']
  print(nowposition)

  if 'None'== nowposition:  #포지션 진입
    if btcdata["MACD"][198] > btcdata["MACD_signal"][198] and btcdata["MACD"][197] < btcdata["MACD_signal"][197]: #롱진입
      print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
    elif btcdata["MACD"][198] < btcdata["MACD_signal"][198] and btcdata["MACD"][197] > btcdata["MACD_signal"][197]: #숏진입
      print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
    

  else :  #포지션 청산
    if 'Buy'== nowposition and btcdata["MACD"][198] < btcdata["MACD_signal"][198]: #롱청산
      print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Market",qty=orderqty*2,time_in_force="GoodTillCancel").result())

    elif 'Sell'== nowposition and btcdata["MACD"][198] > btcdata["MACD_signal"][198]: #숏청산
      print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Market",qty=orderqty*2,time_in_force="GoodTillCancel").result())
  
  

def autousdt(macd_short, macd_long, macd_signal,orderqty):
  key = ""
  secret = ""
  client = bybit.bybit(test=False, api_key=key, api_secret=secret)

  
  dodata = client.LinearKline.LinearKline_indexPrice(symbol="DOGEUSDT", interval="5", **{'from':math.floor(time.time())-60*5*200*3}).result()[0]['result']
  for i in range(2):
    i = i+1
    dodata += client.LinearKline.LinearKline_indexPrice(symbol="DOGEUSDT", interval="5", **{'from':math.floor(time.time())-60*5*200*(3-i)}).result()[0]['result']
    #print(time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(basetime)))

  dogedata = pd.DataFrame(dodata)
  dogedata["MACD_short"]=dogedata["close"].ewm(span=macd_short).mean() 
  dogedata["MACD_long"]=dogedata["close"].ewm(span=macd_long).mean() 
  dogedata["MACD"]=dogedata.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1) 
  dogedata["MACD_signal"]=dogedata["MACD"].ewm(span=macd_signal).mean() 
  dogedata = dogedata[400:]
  dogedata.index=range(len(dogedata))

  xdata = client.LinearKline.LinearKline_indexPrice(symbol="XRPUSDT", interval="5", **{'from':math.floor(time.time())-60*5*200*3}).result()[0]['result']
  for i in range(2):
    i = i+1
    xdata += client.LinearKline.LinearKline_indexPrice(symbol="XRPUSDT", interval="5", **{'from':math.floor(time.time())-60*5*200*(3-i)}).result()[0]['result']
    #print(time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(basetime)))

  xrpdata = pd.DataFrame(xdata)
  xrpdata["MACD_short"]=xrpdata["close"].ewm(span=macd_short).mean() 
  xrpdata["MACD_long"]=xrpdata["close"].ewm(span=macd_long).mean() 
  xrpdata["MACD"]=xrpdata.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1) 
  xrpdata["MACD_signal"]=xrpdata["MACD"].ewm(span=macd_signal).mean() 
  xrpdata = xrpdata[400:]
  xrpdata.index=range(len(xrpdata))
  
  
  dogelong, dogeshort = client.LinearPositions.LinearPositions_myPosition(symbol="DOGEUSDT").result()[0]['result'][0]['size'],client.LinearPositions.LinearPositions_myPosition(symbol="DOGEUSDT").result()[0]['result'][1]['size']
  xrplong, xrpshort = client.LinearPositions.LinearPositions_myPosition(symbol="XRPUSDT").result()[0]['result'][0]['size'],client.LinearPositions.LinearPositions_myPosition(symbol="XRPUSDT").result()[0]['result'][1]['size']
  
  
  print(dogelong, dogeshort,xrplong, xrpshort)

  if 0 == dogelong and 0 == dogeshort:  #포지션 진입
    if dogedata["MACD"][198] > dogedata["MACD_signal"][198] and dogedata["MACD"][197] < dogedata["MACD_signal"][197]: #롱진입
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="DOGEUSDT",order_type="Market",qty=orderqty*3,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="DOGEUSDT",order_type="Limit",qty=orderqty*3,price=round(client.LinearPositions.LinearPositions_myPosition(symbol="DOGEUSDT").result()[0]['result'][0]['position_value']*(1+0.035),4),time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())

    elif dogedata["MACD"][198] < dogedata["MACD_signal"][198] and dogedata["MACD"][197] > dogedata["MACD_signal"][197]: #숏진입
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="DOGEUSDT",order_type="Market",qty=orderqty*3,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="DOGEUSDT",order_type="Limit",qty=orderqty*3,price=round(client.LinearPositions.LinearPositions_myPosition(symbol="DOGEUSDT").result()[0]['result'][1]['position_value']*(1+0.035),4),time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())


  else :  #포지션 청산
    if 0!= dogelong and dogedata["MACD"][198] < dogedata["MACD_signal"][198]: #롱청산
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="DOGEUSDT",order_type="Market",qty=orderqty*3,time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())

    elif 0!= dogeshort and dogedata["MACD"][198] > dogedata["MACD_signal"][198]: #숏청산
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="DOGEUSDT",order_type="Market",qty=orderqty*3,time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())
  

  if 0 == xrplong and 0 == xrpshort:  #포지션 진입
    if xrpdata["MACD"][198] > xrpdata["MACD_signal"][198] and xrpdata["MACD"][197] < xrpdata["MACD_signal"][197]: #롱진입
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="XRPUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="XRPUSDT",order_type="Limit",qty=orderqty,price=round(client.LinearPositions.LinearPositions_myPosition(symbol="XRPUSDT").result()[0]['result'][0]['position_value']*(1+0.035),4),time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())

    elif xrpdata["MACD"][198] < xrpdata["MACD_signal"][198] and xrpdata["MACD"][197] > xrpdata["MACD_signal"][197]: #숏진입
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="XRPUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="XRPUSDT",order_type="Limit",qty=orderqty,price=round(client.LinearPositions.LinearPositions_myPosition(symbol="XRPUSDT").result()[0]['result'][1]['position_value']*(1+0.035),4),time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())


  else :  #포지션 청산
    if 0!= xrplong and xrpdata["MACD"][198] < xrpdata["MACD_signal"][198]: #롱청산
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="XRPUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())

    elif 0!= xrpshort and xrpdata["MACD"][198] > xrpdata["MACD_signal"][198]: #숏청산
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="XRPUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())


while True:
  autobit(macd_short=20, macd_long=60, macd_signal=30,orderqty=200)
  autousdt(macd_short=5, macd_long=20, macd_signal=30,orderqty=20)
  time.sleep(300)
