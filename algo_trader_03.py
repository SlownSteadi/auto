import bybit
import time
import math
import pandas as pd
import copy


#check this!
macd_short=12, macd_long=26, macd_signal=9,orderqty=200
key = "check"
secret = "check"
client = bybit.bybit(test=False, api_key=key, api_secret=secret)
posize = 0

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
  btcdata = btcdata[400:]
  btcdata.index=range(len(btcdata))
  nowposition = client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0]['result']['side']

  if 'None'== nowposition:  #포지션 진입
    if btcdata["MACD"][198] > btcdata["MACD_signal"][198] and btcdata["MACD"][197] < btcdata["MACD_signal"][197]: #롱진입
      print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
      posize = copy.deepcopy(orderqty)
    elif btcdata["MACD"][198] < btcdata["MACD_signal"][198] and btcdata["MACD"][197] > btcdata["MACD_signal"][197]: #숏진입
      print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
      posize = copy.deepcopy(-1*orderqty)
  
  else :  #포지션 청산
    if 'Buy'== nowposition and btcdata["MACD"][198] < btcdata["MACD_signal"][198]: #롱청산
      print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())

    elif orderqty == posize and btcdata["MACD"][198] - btcdata["MACD_signal"][198] < btcdata["MACD"][197] - btcdata["MACD_signal"][197] : #롱부분익절
      print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
      posize = 0

    elif 'Sell'== nowposition and btcdata["MACD"][198] > btcdata["MACD_signal"][198]: #숏청산
      print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
    
    elif orderqty == -1*posize and btcdata["MACD"][198] - btcdata["MACD_signal"][198] > btcdata["MACD"][197] - btcdata["MACD_signal"][197] : #숏부분익절
      print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
      posize = 0
