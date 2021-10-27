import schedule
import bybit
import time
import math
import pandas as pd
import copy
import smtplib
from email.mime.text import MIMEText

orderqty = 0

def bit(qtyy):
  key = "70YdgSVJtWaclVDUpg"
  secret = "h5lE8ajjrxSLjCrmdWnSHUHGKfFWGyDsluLS"
  client = bybit.bybit(test=False, api_key=key, api_secret=secret)
  mshort = 12
  mlong = 26
  msign = 9
  margin = 10
  betratio = 0.3
  global orderqty

  print(client.Wallet.Wallet_getBalance(coin="BTC").result()[0]["result"]["BTC"]["equity"])
  allqty = client.Wallet.Wallet_getBalance(coin="BTC").result()[0]["result"]["BTC"]["equity"]

  #데이터 수집 1
  data = client.Kline.Kline_indexPrice(symbol="BTCUSD", interval="60", **{'from':math.floor(time.time())-60*5*200*3}).result()[0]['result']
  for i in range(2):
    i = i+1
    data += client.Kline.Kline_indexPrice(symbol="BTCUSD", interval="60", **{'from':math.floor(time.time())-60*5*200*(3-i)}).result()[0]['result']
    #print(time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(basetime)))
  btcdata = pd.DataFrame(data)
  btcdata["MACD_short"]=btcdata["close"].ewm(span=macd_short).mean() 
  btcdata["MACD_long"]=btcdata["close"].ewm(span=macd_long).mean() 
  btcdata["MACD"]=btcdata.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1) 
  btcdata["MACD_signal"]=btcdata["MACD"].ewm(span=macd_signal).mean() 
  btcdata = btcdata[400:]
  btcdata.index=range(len(btcdata))

  #데이터 수집 2
  datalong = client.Kline.Kline_indexPrice(symbol="BTCUSD", interval="240", **{'from':math.floor(time.time())-60*5*200*3}).result()[0]['result']
  for i in range(2):
    i = i+1
    datalong += client.Kline.Kline_indexPrice(symbol="BTCUSD", interval="240", **{'from':math.floor(time.time())-60*5*200*(3-i)}).result()[0]['result']
    #print(time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(basetime)))
  btcdatalong = pd.DataFrame(datalong)
  btcdatalong["MACD_short"]=btcdatalong["close"].ewm(span=macd_short).mean() 
  btcdatalong["MACD_long"]=btcdatalong["close"].ewm(span=macd_long).mean() 
  btcdatalong["MACD"]=btcdatalong.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1) 
  btcdatalong["MACD_signal"]=btcdatalong["MACD"].ewm(span=macd_signal).mean() 
  btcdatalong = btcdatalong[400:]
  btcdatalong.index=range(len(btcdatalong))

  #포지션 확인
  #Buy, Sell, None

  pose = client.Positions.Positions_myPosition(symbol = "BTCUSD").result()[0]["result"]["side"]

  if pose == "None" :
    #진입수량 설정
    orderqty = math.floor(btcdata["close"][198]*allqty*betratio*margin)
    #롱진입
    if btcdatalong["MACD"][198] > btcdatalong["MACD_signal"][198] and btcdata["MACD"][198] >= btcdata["MACD_signal"][198]:
      print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
    #숏진입
    elif btcdatalong["MACD"][198] < btcdatalong["MACD_signal"][198] and btcdata["MACD"][198] <= btcdata["MACD_signal"][198]:
      print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())

  #롱청산
  elif pose == "Buy" :
    if btcdata["MACD"][198] <= btcdata["MACD_signal"][198]:
      print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
      orderqty = 0

  #숏청산
  elif pose == "Sell" :
    if btcdata["MACD"][198] >= btcdata["MACD_signal"][198]:
      print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Market",qty=orderqty,time_in_force="GoodTillCancel").result())
      orderqty = 0
  
  s = smtplib.SMTP('smtp.gmail.com', 587)
  s.starttls()
  s.login('rhqudrjs7@gmail.com', 'wfafqivenxkfgmrm')

  msg = MIMEText('내용 : stone, steel is working')
  msg['Subject'] = '제목 : stone, steel.'
  s.sendmail("rhqudrjs7@gmail.com", "rhqudrjs2@naver.com", msg.as_string())
  s.quit()

schedule.every().hours.do(bit)

while True: 
  schedule.run_pending()
  time.sleep(10)
