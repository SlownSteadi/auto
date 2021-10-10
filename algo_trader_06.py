import schedule
import bybit
import time
import math
import pandas as pd
import copy

def bit():
  key = "70YdgSVJtWaclVDUpg"
  secret = "h5lE8ajjrxSLjCrmdWnSHUHGKfFWGyDsluLS"
  client = bybit.bybit(test=False, api_key=key, api_secret=secret)
  mshort, mlong, msign, orderqty = 20, 50. 25, 0.001


  data = client.LinearKline.LinearKline_indexPrice(symbol="BTCUSDT", interval="60", **{'from':math.floor(time.time())-60*60*200*3}).result()[0]['result']
  for i in range(2):
    i = i+1
    data += client.LinearKline.LinearKline_indexPrice(symbol="BTCUSDT", interval="60", **{'from':math.floor(time.time())-60*60*200*(3-i)}).result()[0]['result']
    #print(time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(basetime)))

  btcdata = pd.DataFrame(data)
  btcdata["MACD_short"]=btcdata["close"].ewm(span=mshort).mean() 
  btcdata["MACD_long"]=btcdata["close"].ewm(span=mlong).mean() 
  btcdata["MACD"]=btcdata.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1) 
  btcdata["MACD_signal"]=btcdata["MACD"].ewm(span=msign).mean() 
  btcdata = btcdata[400:]
  btcdata.index=range(len(btcdata))
  
  #포지션 확인
  long, short = client.LinearPositions.LinearPositions_myPosition(symbol="BTCUSDT").result()[0]['result'][0]['size'],client.LinearPositions.LinearPositions_myPosition(symbol="BTCUSDT").result()[0]['result'][1]['size']
  
  if 0 == long :  #롱진입
    if btcdata["MACD"][198] > btcdata["MACD_signal"][198] and btcdata["MACD"][197] < btcdata["MACD_signal"][197]: #롱진입
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())

  elif 0!= long:
    if btcdata["MACD"][198] < btcdata["MACD_signal"][198]: #롱청산
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())

    
  if 0 == short :  #숏진입
    if btcdata["MACD"][198] < btcdata["MACD_signal"][198] and btcdata["MACD"][197] > btcdata["MACD_signal"][197]: #숏진입
      print(client.LinearOrder.LinearOrder_new(side="Sell",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())

  elif 0!= short:
    if btcdata["MACD"][198] > btcdata["MACD_signal"][198]: #숏청산
      print(client.LinearOrder.LinearOrder_new(side="Buy",symbol="BTCUSDT",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel",reduce_only=True, close_on_trigger=False).result())

schedule.every().hours.do(bit)

while True: 
  schedule.run_pending()
  time.sleep(10)
