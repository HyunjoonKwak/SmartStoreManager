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
orderID = []
#현재보다 10시간전의 시간을 구한다.
now = datetime.now()
now = now.replace(hour=now.hour-3)
isoFormat = now.astimezone().isoformat()
isoFormat = parse.quote(isoFormat)

date_time = isoFormat
# print("date and time:",date_time)

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
def order_check(date_time):
    access_token = get_access_token(clientId, clientSecret)

    conn = http.client.HTTPSConnection("api.commerce.naver.com")

    headers = { 
        'Authorization': 'Bearer ' + str(access_token),
        }

    conn.request("GET", "/external/v1/pay-order/seller/product-orders/last-changed-statuses?lastChangedFrom=" + date_time, headers=headers)  
    res = conn.getresponse()
    data = res.read()

    select_data = data.decode("utf-8")
    data = json.loads(select_data)
    if data['data']['count'] != 0:
        order_count = data['data']['count']
        print(f" {order_count} 주문이 있습니다.")
        for i in range(order_count):
            #prodecuOrderId 를 배열에 저장한다.
            orderID.append(data['data']['lastChangeStatuses'][i]['productOrderId'])            

    else:
        print("주문이 없습니다.")
        order_count = 0
    #order_count 와 orderID를 리턴한다.
    return order_count, orderID

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
    
    # print(res_data)
    if 'data' not in res_data:
        return False

    # print(res_data['data'][0]['order'])
    # print(res_data['data'][0]['productOrder'])
    print(f"주문번호 : {res_data['data'][0]['order']['ordererNo']}")
    print(f"주문일시 : {res_data['data'][0]['order']['orderDate']}")
    print(f"주문자명 : {res_data['data'][0]['order']['ordererName']}")
    print(f"주문자 연락처 : {res_data['data'][0]['order']['ordererTel']}")
    print(f"통관고유번호 : {res_data['data'][0]['productOrder']['individualCustomUniqueCode']}")
    print(f"상품이름 : {res_data['data'][0]['productOrder']['productName']}")
    print(f"셀러코드 : {res_data['data'][0]['productOrder']['sellerProductCode']}")
    #공백인쇄
    print()
    # for data in res_data['data']:
        # for d in data.keys():
            # print(f'{d} : {data[d]}')
            # for d2 in data[d].keys():
                # print(f'{d2} : {data[d][d2]}')

#############################################################################################################################################
#order 체크
count, orderID = order_check(date_time)

if(count != 0):
    for i in range(count):
        print(f" {i+1}번째 주문번호 : {orderID[i]}" )
        get_order_detail(orderID[i])
else:
    print("주문이 없습니다.")
