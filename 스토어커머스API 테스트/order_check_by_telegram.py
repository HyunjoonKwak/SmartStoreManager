import bcrypt
import pybase64
import time
import requests
import json
import http.client
import datetime
from urllib import parse
import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request as req
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


clientId = "213tGtVIri480GpHZ2K2tD"
clientSecret = "$2a$04$/6qDc21MqIwmIggCYNKqwO"

######## 텔레그램 관련 코드 ########
token = "5968759585:AAH_Ra2RGzOeVbZEbnNNuBpiYwQFNSSIAiw"
id = "5705723422"

order_count = 0
orderID = []

# Get the current time
current_time = datetime.datetime.now()
time_before = current_time - datetime.timedelta(days=30)  # days, hours, minutes, seconds, microseconds, milliseconds, weeks
until_time = current_time - datetime.timedelta(seconds=5)
total_information = []

# 모든 주문정보를 저장하는 dictionary
total_order_information = {}

#############################################################################################################################################
def get_access_token(clientId, clientSecret):
    timestamp = int(time.time() * 1000)
    # 밑줄로 연결하여 password 생성
    password = clientId + "_" + str(timestamp)
    # bcrypt 해싱
    hashed = bcrypt.hashpw(password.encode('utf-8'), clientSecret.encode('utf-8'))
    # base64 인코딩
    client_secret_sign = pybase64.standard_b64encode(hashed).decode('utf-8')

    # 인증
    url = "https://api.commerce.naver.com/external/v1/oauth2/token"

    data = {
        "client_id": str(clientId),
        "timestamp": timestamp,
        "client_secret_sign":str(client_secret_sign),
        "grant_type":"client_credentials ",
        "type":"SELF"
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    res = requests.post(url, data=data, headers=headers)
    json_data = json.loads(res.text)
    access_token = json_data['access_token']
    return access_token
#############################################################################################################################################
def print_order_list(order_count, orderID):
    print(f"order_count : {order_count}")
    print(f"orderID : {orderID}")


#############################################################################################################################################
# order_partial_check 함수는 주문이 있는지 확인하고 주문이 있으면 주문번호를 배열에 저장한다.
#############################################################################################################################################
def order_partial_cehck(date_time, until_time):
    print(f"from : {date_time} to : {until_time}")
    date_time = date_time.astimezone().isoformat()
    date_time = parse.quote(date_time)

    until_time = until_time.astimezone().isoformat()
    until_time = parse.quote(until_time)
    
    access_token = get_access_token(clientId, clientSecret)

    conn = http.client.HTTPSConnection("api.commerce.naver.com")

    headers = { 
        'Authorization': 'Bearer ' + str(access_token),
        }

    # print(f"from : {date_time} to : {until_time}")
    conn.request("GET", "/external/v1/pay-order/seller/product-orders/last-changed-statuses?lastChangedFrom=" + date_time +"&lastChangedTo=" + until_time + "&lastChangedType=" + "PAYED", headers=headers)  

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    # data 의 message 가 있으면 False를 리턴한다.
    if 'message' in data:
        print(f"에러메시지 {data}")
        order_count = 0
        return order_count, False
    
    # data['data'] 가 없으면 False를 리턴한다.
    if 'data' not in data:
        order_count = 0
        return order_count, False
    
    if data['data']['count'] != 0:
        order_count = data['data']['count']
        print(f" {order_count} 주문이 있습니다.")
        for i in range(order_count):
            # productOrderId 를 배열에 저장한다.
            orderID.append(data['data']['lastChangeStatuses'][i]['productOrderId'])


    else:
        print("주문이 없습니다.")
        order_count = 0
    #order_count 와 orderID를 리턴한다.
    return order_count, orderID    

#############################################################################################################################################
# get_order_detail 함수는 주문번호를 이용하여 주문상세정보를 가져온다.
#############################################################################################################################################
def get_order_detail(orderID):
    access_token = get_access_token(clientId, clientSecret)
    headers = { 
        'Authorization': 'Bearer ' + str(access_token),
        }
    url = 'https://api.commerce.naver.com/external/v1/pay-order/seller/product-orders/query'
    
    params = {
        # 'productOrderIds' : ['']
        'productOrderIds' : [orderID]
    }

    res = requests.post(url=url, headers=headers, json=params)
    res_data = res.json()
    #order_id 배열 초기화
    orderID = []
    # print(res_data)
    if 'data' not in res_data:
        return False

    # print(res_data['data'][0]['order'])
    # print(res_data['data'][0]['productOrder'])
    print(f"주문번호 : {res_data['data'][0]['order']['ordererNo']}")
    order_number = res_data['data'][0]['order']['ordererNo']
    print(f"주문일시 : {res_data['data'][0]['order']['orderDate']}")
    order_date = res_data['data'][0]['order']['orderDate']
    print(f"주문자명 : {res_data['data'][0]['order']['ordererName']}")
    order_name = res_data['data'][0]['order']['ordererName']
    print(f"주문자 연락처 : {res_data['data'][0]['order']['ordererTel']}")
    order_tel = res_data['data'][0]['order']['ordererTel']
    print(f"통관고유번호 : {res_data['data'][0]['productOrder']['individualCustomUniqueCode']}")
    customcode = res_data['data'][0]['productOrder']['individualCustomUniqueCode']
    print(f"상품이름 : {res_data['data'][0]['productOrder']['productName']}")
    product_name = res_data['data'][0]['productOrder']['productName']
    print(f"셀러코드 : {res_data['data'][0]['productOrder']['sellerProductCode']}")
    seller_code = res_data['data'][0]['productOrder']['sellerProductCode']
    print(f"발주상태 : {res_data['data'][0]['productOrder']['placeOrderStatus']}")
    order_status = res_data['data'][0]['productOrder']['placeOrderStatus']
    print(f"발주일자 : {res_data['data'][0]['productOrder']['placeOrderDate']}")
    order_date = res_data['data'][0]['productOrder']['placeOrderDate']
    total_order_information[order_number] = {
        "order_date": order_date,
        "order_name": order_name,
        "order_tel": order_tel,
        "customcode": customcode,
        "product_name": product_name,
        "seller_code": seller_code,
        "order_status": order_status,
        "order_date": order_date
    }
    #공백인쇄
    print()
    return order_number

#############################################################################################################################################
# time_check 함수는 date_time 과 until_time 을 인자로 받아서 24시간 단위로 나누어서 order_partial_check 함수를 호출한다.
#############################################################################################################################################
def time_check(date_time, until_time):
# Calculate the time difference
    time_diff = until_time - time_before

    if time_diff >= datetime.timedelta(hours=24):
        num_days = time_diff.days
        remaining_time = time_diff - datetime.timedelta(days=num_days)

        for i in range(num_days + 1):
            current_start_time = date_time + datetime.timedelta(days=i)
            current_end_time = current_start_time + datetime.timedelta(days=1)

            count, orderID = order_partial_cehck(current_start_time, current_end_time)
            #0.5초 딜레이
            time.sleep(0.5)
            if(count != 0):
                #0.5초 딜레이
                time.sleep(0.5)
                for i in range(count):
                    print(f" {i+1}번째 주문번호 : {orderID[i]}" )
                    order_number = get_order_detail(orderID[i])
            else:
                print("주문이 없습니다.")
    else:
        #0.5초 딜레이
        time.sleep(0.5)
        count, orderID = order_partial_cehck(date_time, until_time)
        if(count != 0):
            for i in range(count):
                print(f" {i+1}번째 주문번호 : {orderID[i]}" )
                order_number = get_order_detail(orderID[i])
        else:
            print("주문이 없습니다.")

    return order_number

#############################################################################################################################################
# Code Start
#############################################################################################################################################
order_number = time_check(time_before , until_time)
# total_order_information 을 한줄씩 출력한다.
for i in total_order_information:
    print(f"{total_order_information[i]}")
#############################################################################################################################################

bot = telegram.Bot(token)
info_message = '''
Smart Store 주문정보를 알려드립니다.
1달 : gom 또는 ㅅㅅㄷ
1주일 : gow  또는 ㅅㅅㅈ
1일 : god 또는 ㅅㅅㅇ
'''
empty_message = '''
오늘은 경매결과가 없어요.
'''

bot.sendMessage(chat_id=id, text=info_message)
 
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
updater.start_polling()
 
### 챗봇 답장
def handler(update, context):
    user_text = update.message.text # 사용자가 보낸 메세지를 user_text 변수에 저장합니다.
    if (user_text == "gom") or (user_text == "ㅅㅅㄷ"):
        # 시작시간과 종료시간을 bot으로 전송한다.
        time_before = current_time - datetime.timedelta(days=30)  # days, hours, minutes, seconds, microseconds, milliseconds, weeks
        until_time = current_time - datetime.timedelta(seconds=5)
        bot.sendMessage(chat_id=id, text=f"From: {time_before} To: {until_time}")
        order_number = time_check(time_before , until_time)
        # total_order_information 을 한줄씩 출력한다.
        # for i in total_order_information:
            # print(f"{total_order_information[i]}")
        # total_order_information 을 bot으로 전송한다.
        for i in total_order_information:
            result = f"{total_order_information[i]}"
            bot.send_message(chat_id=id, text=result)
    
        bot.sendMessage(chat_id=id, text=info_message)

    elif (user_text == "gow") or (user_text == "ㅅㅅㅈ"):
        # 시작시간과 종료시간을 bot으로 전송한다.
        time_before = current_time - datetime.timedelta(weeks=1)  # days, hours, minutes, seconds, microseconds, milliseconds, weeks
        until_time = current_time - datetime.timedelta(seconds=5)
        bot.sendMessage(chat_id=id, text=f"From: {time_before} To: {until_time}")
        order_number = time_check(time_before , until_time)
        # total_order_information 을 한줄씩 출력한다.
        # for i in total_order_information:
            # print(f"{total_order_information[i]}")
        # total_order_information 을 bot으로 전송한다.
        for i in total_order_information:
            result = f"{total_order_information[i]}"
            bot.send_message(chat_id=id, text=result)
        bot.sendMessage(chat_id=id, text=info_message)
    elif (user_text == "god") or (user_text == "ㅅㅅㅇ"):
        # 시작시간과 종료시간을 bot으로 전송한다.
        time_before = current_time - datetime.timedelta(days=1)  # days, hours, minutes, seconds, microseconds, milliseconds, weeks
        until_time = current_time - datetime.timedelta(seconds=5)
        bot.sendMessage(chat_id=id, text=f"From: {time_before} To: {until_time}")
        order_number = time_check(time_before , until_time)
        # total_order_information 을 한줄씩 출력한다.
        # for i in total_order_information:
            # print(f"{total_order_information[i]}")
        # total_order_information 을 bot으로 전송한다.
        for i in total_order_information:
            result = f"{total_order_information[i]}"
            bot.send_message(chat_id=id, text=result)
        bot.sendMessage(chat_id=id, text=info_message)
    elif (user_text == "ㅋㄹㄴ"):
        bot.sendMessage(chat_id=id, text=info_message)

echo_handler = MessageHandler(Filters.text, handler)
dispatcher.add_handler(echo_handler)
####################################
 