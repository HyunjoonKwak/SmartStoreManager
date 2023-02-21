###############################################################################################################
#   Selenium 사용
###############################################################################################################
import time
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

###############################################################################################################
#   get_product()
###############################################################################################################
def get_ople_product(url, tries, max_retries):
    if url == "":
        print('URL is invalid')
        return {"title": "-", "price": 0, "soldout": "", "crawling": "", "coupon": ""}    # print(url)

    time.sleep(0.5)
    browser.get(url)

    try:
        title = browser.find_element(By.CSS_SELECTOR,'div.detailTitle > h1 > span.item_name_detail.item_name_eng_deatil').text    
        title = title.replace(",","")


        try:
            price = browser.find_element(By.CSS_SELECTOR,'span.amount.amount_won').text  # 할인판매가격
            price = price.replace(",","")
        except:
            try:
                price = browser.find_element(By.CSS_SELECTOR,'span.amount.public_amount_won').text  # 정상판매가격
            except:
                try:
                    price = browser.find_element(By.CSS_SELECTOR,'span.cust_amount_won').text  # 권장소비자가격
                except:
                    #price = browser.find_element(By.CSS_SELECTOR,'span.amount.amount_won').text  # 정상판매가격
                    price = 0
                    print("가격 오류 error")

        # print("price :", price)
        # print(product_title)
        try:
            soldout = browser.find_element(By.CSS_SELECTOR,'div.item-order > div:nth-child(3) > p > span').text
            soldout = "x"
        except:
            soldout = ""  #hjoon.kwak 23.1.13 공백으로 변경 

        return {"title": title, "price": int(price), "soldout": soldout, "crawling": ""}
    
    except Exception as e:
        sleep = tries+0.5
        print(f'Exception occurs: {e.args}')
        title = 'Fail'
        if tries >= max_retries:
            print(f'Max reties exceeded. returns default value. \n url: {url}')
            return {"title": "-", "price": 0, "soldout": "", "crawling": False}      
        return get_ople_product(url, sleep, 4)


def read_option():
    df_option = pd.read_csv('./사전작업/ople_option.txt', header=None)
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

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--window-size=1920,1080')
options.add_experimental_option("excludeSwitches", ["enable-logging"])
browser = webdriver.Chrome(options=options)

for i, url in enumerate(df_sub["오플링크"]):
    if(df_sub["구분"][i] == "O"):
        p = get_ople_product(url, 0, 4)
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
# df_sub["쿠폰가"] = df_prod["coupon"]

dt_today = datetime.date.today()
dt_now = datetime.datetime.now()
date = dt_now.strftime('%Y%m%d%H%M')
today = dt_today.strftime('%Y%m%d')
path = './사전작업/output_Ople'+today+'.xlsx'

with pd.ExcelWriter(path) as writer:
    df_sub.to_excel(writer, sheet_name=today, index=False)

print(f"end time : {dt_now}")
