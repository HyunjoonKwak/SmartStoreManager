###############################################################################################################
# 쿠팡 가격 읽어서 스토어에 직접 가격 과 품절상태를 업데이트 하는 프로그램
#   From 2023.04.28 ~ 
#   Request 사용
###############################################################################################################
import os
import sys
import time
import datetime
import pandas as pd
from bs4 import BeautifulSoup
import requests
import random
from requests.adapters import HTTPAdapter, Retry
from urllib3.exceptions import InsecureRequestWarning
from openpyxl import load_workbook
import shutil
import bcrypt
import pybase64
import time
import requests
import json
import http.client

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def requests_retry_session(
    retries=0,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

###############################################################################################################
#  get_proxy()
###############################################################################################################
def get_proxy():
    global p_idx
    p_idx = (p_idx + 1) % p_len
    return {
        "http":  proxy_list[p_idx],
        "https": proxy_list[p_idx]
    }

###############################################################################################################
#  스토어 커머스 api 
# ###############################################################################################################

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

#############################################################################################################################################

def store_check_product(channelProductNo):
    access_token = get_access_token(clientId, clientSecret)
    conn = http.client.HTTPSConnection("api.commerce.naver.com")
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
        sellerCode = data["originProduct"]["detailAttribute"]["sellerCodeInfo"]["sellerManagementCode"]
        statusType = data["originProduct"]["statusType"]
        ProdutName = data["originProduct"]["name"]
        StorePrice = data["originProduct"]["salePrice"]
        DiscountPrice = data["originProduct"]["customerBenefit"]["immediateDiscountPolicy"]["discountMethod"]["value"]
        MobileDiscountPrice = data["originProduct"]["customerBenefit"]["immediateDiscountPolicy"]["mobileDiscountMethod"]["value"]
        # print(f"sellerCode: {sellerCode}, statusType: {statusType}, ProdutName: {ProdutName}, StorePrice: {StorePrice}, DiscountPrice: {DiscountPrice}, MobileDiscountPrice: {MobileDiscountPrice}")
        # print(data["originProduct"]["originProductNo"])
        # print(data["originProduct"]["channelProductNo"])
        return sellerCode, statusType, ProdutName, StorePrice, DiscountPrice, MobileDiscountPrice
    else:
        return False

def store_update_product(channelProductNo, salePrice, statusType, sellerCode, discountPrice, mobileDiscountPrice):
    access_token = get_access_token(clientId, clientSecret)
    conn = http.client.HTTPSConnection("api.commerce.naver.com")
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
    else:
        return False

    # store 에 정보업데이트 
    data["originProduct"]["salePrice"] = str(salePrice)
    data["originProduct"]["customerBenefit"]["immediateDiscountPolicy"]["discountMethod"]["value"] = str(discountPrice)
    data["originProduct"]["customerBenefit"]["immediateDiscountPolicy"]["mobileDiscountMethod"]["value"] = str(mobileDiscountPrice)

    json_data = json.dumps(data, ensure_ascii=False)
    utf8_data = json_data.encode('utf-8')
    payload = utf8_data

    headers = {
        'Authorization': 'Bearer ' + str(access_token),
        'content-type': "application/json"
        }

    conn = http.client.HTTPSConnection("api.commerce.naver.com")
    conn.request("PUT", "/external/v2/products/channel-products/"+str(channelProductNo), payload, headers)
    res = conn.getresponse()
    if res.status == 200:
        data = res.read()
        print(f"{channelProductNo}---정보업데이트완료")
    elif res.status == 400:
        data = res.read()
        print(data)
        print(str(channelProductNo)+"---상품옵션문제/단일옵션 or 판매상태문제")
    else :
        return False


#############################################################################################################################################

    
###############################################################################################################
#   get_product()
###############################################################################################################

s=requests_retry_session()

def get_product(url, tries, max_retries):
    try:
        if url == "":
            print('URL is invalid')
            return {"title": "-", "price": 0, "soldout": "", "crawling": "", "coupon": ""}
        sleep_time = 0.5 + tries
        # print(f'Sleep start for {sleep_time}sec')
        time.sleep(sleep_time)
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Window-Size':'1920x1080',
            "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}

        html=s.get(url, headers = headers, proxies = get_proxy() , verify=False, timeout=1)
        html.raise_for_status()

        soup = BeautifulSoup(html.text, "html.parser")

        title=soup.select_one(".prod-buy-header__title").text
        price=soup.select_one(".prod-coupon-price .total-price > strong").text
        price=price.replace("원","").replace(",","")
        if price == "":
            price=soup.select_one(".total-price > strong").text
            price=price.replace("원","").replace(",","")
            coupon_price = ""
        else:
            coupon_price = True

        soldout=soup.select_one("div.oos-label")
        
        if soldout == None:
            soldout=""
        else:
            soldout="x"

        return {"title": title, "price": int(price), "soldout": soldout, "crawling": "", "coupon": coupon_price}

    except Exception as e:
        sleep = tries+0.5
        print(f'Exception occurs: {e.args}')
        if tries >= max_retries:
            print(f'Max reties exceeded. returns default value. \n url: {url}')
            return {"title": "-", "price": 0, "soldout": "", "crawling": False, "coupon": "-"}      
        return get_product(url, sleep, 4)


def read_option():
    df_option = pd.read_csv('./사전작업/option_daily.txt', header=None)
    df_option.columns = ['option']
    path = df_option['option'][0]
    fname = df_option['option'][1]
    start = int(df_option['option'][2])
    paging = int(df_option['option'][3])
    up_margin = int(df_option['option'][4])
    dn_margin = int(df_option['option'][5])
    return path, fname, start, paging, up_margin, dn_margin

###############################################################################################################
#   Main 실행코드
###############################################################################################################
dt_now = datetime.datetime.now()
print(f"start time : {dt_now}")

base_path = "."
path=base_path+"/proxylist.txt"

df_proxy=pd.read_csv(path, header=None)
df_proxy.columns= ["proxy"]
proxy_list=df_proxy["proxy"]

p_len=len(proxy_list)
p_idx = random.randrange(1,p_len)
print(f"Proxy 개수: {p_len}")

path, fname, start, paging, up_margin, dn_margin = read_option()
list_file = path+fname
print(f"file path : {list_file} , start = {start} , end = {paging}")    #files 리스트 값 출력
up = float(up_margin)
dn = float(dn_margin)
print(f"기준할인율 : up:{up} %, dn:{dn}%")


df= pd.read_excel(list_file, keep_default_na=False)    #   상품리스트 액셀 읽기
df=df.fillna('')
df=df.iloc[:,:7] ## 엑셀 수정할 것.

df_sub=df[start:paging].reset_index(drop=True)

passed=0
failed=0
skip = 0
products= []

for i, url in enumerate(df_sub["구매처링크"]):
    if(df_sub["구분"][i] == "C"):
        p = get_product(url, 0, 4)
        if p["price"] == 0:
            failed+=1
        else:
            passed+=1
    else :
        print("Get other price value")
        skip +=1
    # print(f"total/failed/passed / skip: ({failed+passed}/{failed}/{passed}) / {skip}")
    print("=====================================================================================================")
    products = products + [p]

    #price 와 soldout 을 스토어 가격과 비교하는 루틴 추가
    #df 의 상품번호를 이용해서 스토어 가격을 가져온다.
    if p["price"] != 0 :
        if(p["soldout"] != ""):
            print(f"품절상품입니다.")
            print(f"소싱가격을 업데이트 하면서 할인가격을 100원으로 바꾸자")
            print(f" productNo : {df_sub['상품번호'][i]} , price : {p['price']} , soldout : {p['soldout']} ")
            print("=====================================================================================================")        
            continue
        # print(f" productNo : {df_sub['상품번호'][i]} , price : {p['price']} , soldout : {p['soldout']} ")
        store_value = store_check_product(df_sub['상품번호'][i])
        # print(f"Seller Code: {store_value[0]} , Status Type : {store_value[1]} , Product Name : {store_value[2]} , Store Price : {store_value[3]} , Discount Price : {store_value[4]} , Mobile Discount Price : {store_value[5]}")

        #p["price"] 에 마진 25% 를 더한 값에 Discount Price 를 더한값과 Store Price 를 비교한다.
        margin = 1.25
        price_margin = int(p["price"] * margin) # price_margin : 소싱처 가격에 마진 25% 를 더한 값
        price_margin += int(store_value[4])     # price_margin 에 Discount Price 를 더한 값
        #테스트코드로 사용  
        if(False):
            if price_margin < int(store_value[3]):  # 소싱처가격 이 Store Price 보다 낮으면
                print("쿠팡가격이 스토어가격보다 낮습니다. 인하검토")
                print(f"price_margin : {price_margin} , store_value[3] : {store_value[3]}")
            else :                                  # 소싱처가격 이 Store Price 보다 높으면
                print("쿠팡가격이 스토어가격보다 높습니다. 인상검토")
                print(f"price_margin : {price_margin} , store_value[3] : {store_value[3]}")

        price_gap = price_margin - int(store_value[3])      # price_gap : 소싱처 가격과 Store Price 의 차이
        percent = float(price_gap) / float(store_value[3]) * 100
        percent = round(percent, 2)
        price_update = False
        if(price_gap != 0):
            if(price_gap > 0):              # 소싱처 가격이 Store Price 보다 높으면
                if(percent >= up):
                    price_update = True
                    # print(f"가격 인상 : {percent}%")
            elif(price_gap < 0):            # 소싱처 가격이 Store Price 보다 낮으면
                percent = percent * -1
                if(percent >= dn):
                    price_update = True           
                    # print(f"가격 인하 : {percent}%")     
        if(price_update == True):
            # print("Price Update")
            # 가격을 업데이트 할때 할인가격 은 원복시켜줘야 한다. (품절이었다가 풀리는 품목이 있을 수 있으므로)
            # price_margin 을 10 자라에서 반올림한다.
            price_margin = round(price_margin, -1)
            # print(f"percent : {percent} , price_gap : {price_gap} , price_margin : {price_margin} , store_value[3] : {store_value[3]}")
            #store_update_product(channelProductNo, salePrice, statusType, sellerCode, discountPrice, mobileDiscountPrice):
            # store_update_product(df_sub['상품번호'][i], price_margin, store_value[1], store_value[0], store_value[4], store_value[5])
    print(f"상품번호 : {df_sub['상품번호'][i]} , 상품명 : {df_sub['상품명'][i]} ,  변경후가격: {price_margin} , 변경전가격 : {store_value[3]}, 변경여부 : {price_update} , 판매상태 : {p['soldout']}")
    print("=====================================================================================================")



## 최종결과 출력
print(f"\n[RESULT] total: {failed+passed}, failed: {failed}, passed: {passed}")

df_prod = pd.DataFrame(products)
df_sub["상품명"] = df_prod["title"]
df_sub["소싱가격"] = df_prod["price"]
df_sub["품절여부"] = df_prod["soldout"]
df_sub["크롤링"] = df_prod["crawling"]
df_sub["쿠폰가"] = df_prod["coupon"]

dt_today = datetime.date.today()
dt_now = datetime.datetime.now()
date = dt_now.strftime('%Y%m%d%H%M')
today = dt_today.strftime('%Y%m%d')
path = base_path+'/사전작업/output_'+today+'.xlsx'

with pd.ExcelWriter(path) as writer:
    df_sub.to_excel(writer, sheet_name=today, index=False)

print(f"end time : {dt_now}")
