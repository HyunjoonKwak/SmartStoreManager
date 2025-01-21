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

def store_check_product(channelProductNo):
    access_token = get_access_token(clientId, clientSecret)
    headers = {
        'Authorization': 'Bearer ' + str(access_token)
        }

    conn = http.client.HTTPSConnection("api.commerce.naver.com")
    conn.request("GET", "/external/v2/products/channel-products/"+str(channelProductNo), headers=headers)

    res = conn.getresponse()

    if res.status == 200:
        data = res.read()     
        select_data = data.decode("utf-8")
        data = json.loads(select_data)
        # print(data["originProduct"]["statusType"])
        # print(data["originProduct"]["name"])
        # print(data["originProduct"]["salePrice"])
    else:
        return False


    dynamic_stock_list = []
    max_retries = 3  # 최대 재시도 횟수

    data["originProduct"]["statusType"] = 'SALE'
    data["originProduct"]["salePrice"] = '30000'
    data["originProduct"]["stockQuantity"] = '9999'

    json_data = json.dumps(data, ensure_ascii=False)
    utf8_data = json_data.encode('utf-8')
    payload = utf8_data

    for retry in range(max_retries):
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'content-type': "application/json"
            }

        conn = http.client.HTTPSConnection("api.commerce.naver.com")
        conn.request("PUT", "/external/v2/products/channel-products/"+str(channelProductNo), payload, headers)
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            break
        elif res.status == 400:
            data = res.read()
            print(data)
            print(str(channelProductNo)+"---상품옵션문제/단일옵션 or 판매상태문제")
            break
        else:
            print("수정 API 요청 실패 ({}/{}): {} {} -status_code: {}".format(retry+1, max_retries, "PUT", "/external/v2/products/channel-products/"+str(channelProductNo), res.status))
            if retry == max_retries - 1:  # 최대 재시도 횟수 초과
                print("API 요청 실패. 최대 재시도 횟수를 초과했습니다.")
                return None
            time.sleep(retry_delay)  # 지정된 시간만큼 대기 후 재시도
            access_token = get_access_token(clientId, clientSecret)
            retry_delay *= 2    

# res = store_check_product(8093783622)

def status_change(originProductNo):
    access_token = get_access_token(clientId, clientSecret)
    headers = {
        'Authorization': 'Bearer ' + str(access_token),
        'content-type': "application/json"
        }
    # payload = "{\"statusType\":\"OUTOFSTOCK\"}"
    # payload = "{\"statusType\":\"SUSPENSION\",\"stockQuantity\":0}"

    payload = "{\"statusType\":\"SALE\",\"stockQuantity\":0}"

    conn = http.client.HTTPSConnection("api.commerce.naver.com")
    # conn.request("PUT", "/external/v1/products/origin-products/"+str(originProductNo)+"/change-status", payload, headers=headers)
    conn.request("PUT", "/external/v1/products/origin-products/%7BoriginProductNo%7D/change-status", payload, headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))

# status_change(8093783622)    

def order_check():
    access_token = get_access_token(clientId, clientSecret)

    conn = http.client.HTTPSConnection("api.commerce.naver.com")

    headers = { 
        'Authorization': 'Bearer ' + str(access_token),
        }

    # conn.request("GET", "/external/v1/pay-order/seller/orders/2021123115350911/product-order-ids", headers=headers)

    now = datetime.now()
    isoFormat = now.astimezone().isoformat()
    print(isoFormat)
    #unicode encoding isoFormat
    # isoFormat = isoFormat.encode('utf-8')
    isoFormat = parse.quote(isoFormat)
    conn.request("GET", "/external/v1/pay-order/seller/product-orders/last-changed-statuses?lastChangedFrom="+isoFormat, headers=headers)  

    string_original = "Mon%20Apr%2011%202022%2015%3A21%3A44%20GMT%2B0900%20(%ED%95%9C%EA%B5%AD%20%ED%91%9C%EC%A4%80%EC%8B%9C)"
    string_decoded = parse.unquote(string_original)
    print("기존 문자열 : ", string_original)
    print("Decoded 문자열 : ", string_decoded)

    string_original = "Mon Apr 11 2022 15:21:44 GMT+0900 (한국 표준시)"
    string_encoded = parse.quote(string_original)

    print("기존 문자열 : ", string_original)
    print("Encoded 문자열 : ", string_encoded)

    # conn.request("POST", "/external/v1/pay-order/seller/product-orders/query", payload, headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))

order_check()