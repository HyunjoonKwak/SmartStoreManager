###############################################################################################################
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
#   get_product()
###############################################################################################################

s=requests_retry_session()

def get_product(url, tries, max_retries):
    try:
        if url == "":
            print('URL is invalid')
            return {"title": "-", "price": 0, "soldout": "", "crawling": "", "coupon": ""}
        sleep_time = 1.5 + tries
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
    df_option = pd.read_csv('./사전작업/option.txt', header=None)
    df_option.columns = ['option']
    path = df_option['option'][0]
    fname = df_option['option'][1]
    start = int(df_option['option'][2])
    paging = int(df_option['option'][3])
    return path, fname, start, paging

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

path, fname, start, paging = read_option()
list_file = path+fname
print(f"file path : {list_file} , start = {start} , end = {paging}")    #files 리스트 값 출력


df= pd.read_excel(list_file, keep_default_na=False)    #   상품리스트 액셀 읽기
df=df.fillna('')
df=df.iloc[:,:7] ## 엑셀 수정할 것.

df_sub=df[start:paging].reset_index(drop=True)

passed=0
failed=0
products= []

for i, url in enumerate(df_sub["쿠팡링크"]):
    if(df_sub["구분"][i] == "C"):
        p = get_product(url, 0, 4)
        if p["price"] == 0:
            failed+=1
        else:
            passed+=1
    else :
        print("Get other price value")
        passed+=1
    print(f"total/failed/passed: ({failed+passed}/{failed}/{passed})")
    products = products + [p]

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
