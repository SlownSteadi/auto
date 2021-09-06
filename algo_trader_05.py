import bybit
import time
import math
import pandas as pd
import copy

def autousdt(macd_short, macd_long, macd_signal,orderqty):
  key = "70YdgSVJtWaclVDUpg"
  secret = "h5lE8ajjrxSLjCrmdWnSHUHGKfFWGyDsluLS"
  client = bybit.bybit(test=False, api_key=key, api_secret=secret)

  
  dodata = client.LinearKline.LinearKline_indexPrice(symbol="BTCUSDT", interval="60", **{'from':math.floor(time.time())-60*60*200*3}).result()[0]['result']
  for i in range(2):
    i = i+1
    dodata += client.LinearKline.LinearKline_indexPrice(symbol="BTCUSDT", interval="60", **{'from':math.floor(time.time())-60*60*200*(3-i)}).result()[0]['result']
    #print(time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(basetime)))

  dogedata = pd.DataFrame(dodata)
  dogedata["MACD_short"]=dogedata["close"].ewm(span=macd_short).mean() 
  dogedata["MACD_long"]=dogedata["close"].ewm(span=macd_long).mean() 
  dogedata["MACD"]=dogedata.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1) 
  dogedata["MACD_signal"]=dogedata["MACD"].ewm(span=macd_signal).mean() 
  dogedata = dogedata[400:]
  dogedata.index=range(len(dogedata))
 
  
  dogelong, dogeshort = client.LinearPositions.LinearPositions_myPosition(symbol="BTCUSDT").result()[0]['result'][0]['size'],client.LinearPositions.LinearPositions_myPosition(symbol="BTCUSDT").result()[0]['result'][1]['size']
  
  if 0 == dogelong and 0 == dogeshort:  #포지션 진입
    if dogedata["MACD"][198] > dogedata["MACD_signal"][198] and dogedata["MACD"][197] < dogedata["MACD_signal"][197]: #롱진입
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())
      
    elif dogedata["MACD"][198] < dogedata["MACD_signal"][198] and dogedata["MACD"][197] > dogedata["MACD_signal"][197]: #숏진입
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())
     

  else :  #포지션 청산
    if 0!= dogelong and dogedata["MACD"][198] < dogedata["MACD_signal"][198]: #롱청산
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())
     
    elif 0!= dogeshort and dogedata["MACD"][198] > dogedata["MACD_signal"][198]: #숏청산
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())

while True:
  autousdt(macd_short=20, macd_long=50, macd_signal=25,orderqty=0.001)
  time.sleep(300)

 
