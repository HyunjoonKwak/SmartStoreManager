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

def status_change(originProductNo):
    access_token = get_access_token(clientId, clientSecret)
    headers = {
        'Authorization': 'Bearer ' + str(access_token),
        'content-type': "application/json"
        }
    # payload = "{\"statusType\":\"OUTOFSTOCK\"}"
    # payload = "{\"statusType\":\"SUSPENSION\",\"stockQuantity\":0}"

    # payload = "{\"statusType\":\"SALE\",\"stockQuantity\":0}"
    payload = "{\"statusType\":\"WAIT\",\"stockQuantity\":0}"

    conn = http.client.HTTPSConnection("api.commerce.naver.com")
    conn.request("PUT", "/external/v1/products/origin-products/%7BoriginProductNo%7D/change-status", payload, headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))

status_change(8093783622)