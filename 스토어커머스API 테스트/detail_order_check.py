import bcrypt
import pybase64
import time
import requests
import json
import http.client
from datetime import datetime
from urllib import parse

clientId = "213tGtVIri480GpHZ2K2tD"
clientSecret = "$2a$04$/6qDc21MqIwmIggCYNKqwO"

order_count = 0

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
    
    # print(res_data)
    if 'data' not in res_data:
        return False

    print(res_data['data'][0]['productOrder']['productName'])
    print(res_data['data'][0]['productOrder']['sellerProductCode'])

    for data in res_data['data']:
        for d in data.keys():
            # print(f'{d} : {data[d]}')
            for d2 in data[d].keys():
                print(f'{d2} : {data[d][d2]}')

ID = 2023042876622831
get_order_detail(ID)