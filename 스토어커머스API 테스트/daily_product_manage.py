import bcrypt
import pybase64
import time
import requests
import json
import http.client
from datetime import datetime
from urllib import parse
import time
import datetime
import pandas as pd
from bs4 import BeautifulSoup
import requests
import random
from requests.adapters import HTTPAdapter, Retry
from urllib3.exceptions import InsecureRequestWarning
from openpyxl import load_workbook

clientId = "213tGtVIri480GpHZ2K2tD"
clientSecret = "$2a$04$/6qDc21MqIwmIggCYNKqwO"

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

access_token = get_access_token(clientId, clientSecret)
conn = http.client.HTTPSConnection("api.commerce.naver.com")

def store_check_product(channelProductNo):
    headers = {
        'Authorization': 'Bearer ' + str(access_token)
        }

    originProductNo = channelProductNo
    conn.request("GET", "/external/v2/products/channel-products/"+str(channelProductNo), headers=headers)
    res = conn.getresponse()

    if res.status == 200:
        data = res.read()     
        select_data = data.decode("utf-8")
        data = json.loads(select_data)
        # print(data)
        print(data["originProduct"]["detailAttribute"]["sellerCodeInfo"]["sellerManagementCode"])
        print(data["originProduct"]["statusType"])
        print(data["originProduct"]["name"])
        print(data["originProduct"]["salePrice"])
        # print(data["originProduct"]["originProductNo"])
        # print(data["originProduct"]["channelProductNo"])
        print(data["originProduct"]["customerBenefit"]["immediateDiscountPolicy"]["discountMethod"]["value"])
        print(data["originProduct"]["customerBenefit"]["immediateDiscountPolicy"]["mobileDiscountMethod"]["value"])
    else:
        return False
#############################################################################################################################################

store_check_product(7575536540)