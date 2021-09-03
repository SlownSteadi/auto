import bybit
import time
import math
import pandas as pd
import copy

def case(x):
    if x["ema5"] > x["ema20"] > x["ema60"] > x["ema200"] :
        return 1
    elif x["ema20"] > x["ema5"] > x["ema60"] > x["ema200"] :
        return 1
    elif x["ema5"] > x["ema60"] > x["ema20"] > x["ema200"] :
        return 7
    elif x["ema60"] > x["ema5"] > x["ema20"] > x["ema200"] :
        return 6
    elif x["ema20"] > x["ema60"] > x["ema5"] > x["ema200"] :
        return 3
    elif x["ema60"] > x["ema20"] > x["ema5"] > x["ema200"] :
        return 3
    elif x["ema200"] > x["ema20"] > x["ema60"] > x["ema5"] :
        return 10
    elif x["ema20"] > x["ema200"] > x["ema60"] > x["ema5"] :
        return 9
    elif x["ema200"] > x["ema60"] > x["ema20"] > x["ema5"] :
        return 1
    elif x["ema60"] > x["ema200"] > x["ema20"] > x["ema5"] :
        return 5
    elif x["ema20"] > x["ema60"] > x["ema200"] > x["ema5"] :
        return 7
    elif x["ema60"] > x["ema20"] > x["ema200"] > x["ema5"] :
        return 10
    elif x["ema5"] > x["ema200"] > x["ema60"] > x["ema20"] :
        return 8
    elif x["ema200"] > x["ema5"] > x["ema60"] > x["ema20"] :
        return 2
    elif x["ema5"] > x["ema60"] > x["ema200"] > x["ema20"] :
        return 6
    elif x["ema60"] > x["ema5"] > x["ema200"] > x["ema20"] :
        return 4
    elif x["ema200"] > x["ema60"] > x["ema5"] > x["ema20"] :
        return 1
    elif x["ema60"] > x["ema200"] > x["ema5"] > x["ema20"] :
        return 2
    elif x["ema5"] > x["ema20"] > x["ema200"] > x["ema60"] :
        return 1
    elif x["ema20"] > x["ema5"] > x["ema200"] > x["ema60"] :
        return 8
    elif x["ema5"] > x["ema200"] > x["ema20"] > x["ema60"] :
        return 4
    elif x["ema200"] > x["ema5"] > x["ema20"] > x["ema60"] :
        return 5
    elif x["ema20"] > x["ema200"] > x["ema5"] > x["ema60"] :
        return 5
    elif x["ema200"] > x["ema20"] > x["ema5"] > x["ema60"] :
        return 3
    
    
    
#check this!
macd_short=20, macd_long=60, macd_signal=30
key = "70YdgSVJtWaclVDUpg"
secret = "h5lE8ajjrxSLjCrmdWnSHUHGKfFWGyDsluLS"
client = bybit.bybit(test=False, api_key=key, api_secret=secret)

#copy.deepcopy(rowdata)

while True:
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
  btcdata["ema5"]=btcdata["close"].ewm(span=5).mean()
  btcdata["ema20"]=btcdata["close"].ewm(span=20).mean() 
  btcdata["ema60"]=btcdata["close"].ewm(span=60).mean()
  btcdata["ema200"]=btcdata["close"].ewm(span=200).mean()
  btcdata["case"]=btcdata.apply(lambda x: case(x), axis=1)

  btcdata = btcdata[400:]
  btcdata.index=range(len(btcdata))
  nowposition = client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0]['result']['side']

  if 'None'== nowposition:  #포지션 진입
    orderqty=int(btcdata["case"][198])*20
    if btcdata["MACD"][198] > btcdata["MACD_signal"][198] and btcdata["MACD"][197] < btcdata["MACD_signal"][197]: #롱진입
      print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
      
    elif btcdata["MACD"][198] < btcdata["MACD_signal"][198] and btcdata["MACD"][197] > btcdata["MACD_signal"][197]: #숏진입
      print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
      
  
  else :  #포지션 청산
    orderqty= orderqty + int(btcdata["case"][198])*20
    if 'Buy'== nowposition and btcdata["MACD"][198] < btcdata["MACD_signal"][198]: #롱청산
      print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())

    elif 'Sell'== nowposition and btcdata["MACD"][198] > btcdata["MACD_signal"][198]: #숏청산
      print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())



