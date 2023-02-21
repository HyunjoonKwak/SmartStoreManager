import time
import datetime
## 데이터 라이브러리
import pandas as pd
## 크롤링 라이브러리
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import urllib
import os
import shutil

###############################################################################################################
#   name_change
###############################################################################################################
def name_change(idx, rd1, rd2):
    changedSTR = ""
    title = ""
    brand = []

    changedSTR = rd1
    changedSTR = changedSTR.replace("-", " ")
    changedSTR = changedSTR.replace(",", "")
    changedSTR = changedSTR.replace(" 타블렛", "정")
    changedSTR = changedSTR.replace(" 캡슐", "정")
    changedSTR = changedSTR.replace(" 베지캡슐", "정")
    changedSTR = changedSTR.replace(" 베지타블렛", "정")
    changedSTR = changedSTR.replace(" 피쉬 소프트젤", "정")
    changedSTR = changedSTR.replace(" 소프트젤", "정")
    changedSTR = changedSTR.replace(" 장용 베지캡슐", "정")
    changedSTR = changedSTR.replace(" 츄어블 타블렛", "정")
    changedSTR = changedSTR.replace(" 리퀴드 베지캡슐", "정")
    changedSTR = changedSTR.replace(" 구미", "정")
    changedSTR = changedSTR.replace(" 미니 소프트젤", "정")
    changedSTR = changedSTR.replace(" 코팅 타블렛", "정")
    changedSTR = changedSTR.replace(" 캐플릿", "정")
    changedSTR = changedSTR.replace(" g", "g")
    changedSTR = changedSTR.replace(" mg", "mg")
    changedSTR = changedSTR.replace(" ml", "ml")

    title = changedSTR
    ch = rd2
    if ch.find(" ") > 0:
        ch = ch.replace(" ","")
        brand = ch.split(']')
        #print(brand[0], brand[1])
        title = brand[1] + " " + title
    return title

###############################################################################################################
#   naver_category
###############################################################################################################
client_id = "k9IWv41faJYngZh1tkQS"
client_secret = "1NBnolNm8Y"
def naver_category(key) :
    global result
    display = "1"
    query = key
    query = urllib.parse.quote(query)
    url = "https://openapi.naver.com/v1/search/shop?query=" + query+ "&display=" + display

    header_params = {"X-Naver-Client-Id":client_id, "X-Naver-Client-Secret":client_secret}
    html = requests.get(url, headers=header_params)
    if html.status_code == 200:
        data = html.json()
        for item in data['items']:
            result = (item['category1'], item['category2'], item['category3'], item['category4'])
    #print(html)
    return result

###############################################################################################################
#   get_ople_product
###############################################################################################################
def get_ople_product(cnt, ID, url):
    url = url + ID
    print(url)
    browser.get(url)
    
    time.sleep(0.7)
       
    try:
        brand_name = browser.find_element(By.CSS_SELECTOR ,'div.detailTitle > h1 > span.item_name_detail.item_name_brand_deatil').text
                                            
        product_title = browser.find_element(By.CSS_SELECTOR,'div.detailTitle > h1 > span.item_name_detail.item_name_eng_deatil').text    
        product_title = product_title.replace(",","")
    except Exception as e:
        print(f'Exception occurs: {e.args}')
        product_title = 'Fail'
        brand_name = ''

    try:
        price = browser.find_element(By.CSS_SELECTOR,'span.amount.amount_won').text  # 할인판매가격
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
        soldout = "o"
    except:
        soldout = ""  #hjoon.kwak 23.1.13 공백으로 변경 
    
    try:
        howto = browser.find_element(By.CSS_SELECTOR,'#div_explan > div:nth-child(5) > div > p:nth-child(2)').text
    except:
        try:
            howto = browser.find_element(By.CSS_SELECTOR,'#div_explan > div:nth-child(5) > div > p').text
        except:
            howto = ""
            print("용법 parsing error")
    
    ##이미지 스크린샷 위치   
    try:
        # print("download images : " + str(item_number))
        ##대표 이미지 다운로드
        url_productimage = "https://img.ople.com/ople/item/"+ str(ID) +"_l1"

        productimage_name = path + '/' + str(ID) +".jpg" #제품사진 파일명
        # print(url_productimage)
        # print(productimage_name)
        urllib.request.urlretrieve(url_productimage,productimage_name) #해당 url에서 이미지를 다운로드 메소드
        time.sleep(1)
        element = browser.find_element(By.CSS_SELECTOR,'table.SupplementFacts')  
        element_png = element.screenshot_as_png
        detailpage_name = path + '/' + str(ID) + "-type.jpg" #제품상세소개 파일명

        with open(detailpage_name, "wb") as file:  
            file.write(element_png) 
    except:
        print("이미지 parsing error")

    cat_title = name_change(cnt, product_title, brand_name)

    return {"Src":"O", "cnt":cnt, "Prd_ID":ID, "Brand": brand_name, "Title":cat_title, "Now": price, "soldout": soldout, "howto":howto, "링크":url}

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

# 선택할 아이템 번호 읽어오기 
def read_select_list():
    selectList = []
    f = open("./사전작업/itemlist.txt", "r")

    while True:
        line = f.readline().strip()
        if not line: break
        selectList.append(line)

    return selectList

def read_banlist_txt() : 
    banlist = []
    with open('./사전작업/banlist.txt', 'r') as fo : 
        while True :
            k=fo.readline()
            #print(k)
            if k=='' :
                break
            else : 
                k = k.replace("\n","")
                banlist.append(k) #data 분류 
    return banlist

# 옵션정보 읽어오기
def read_option():
    option = []
    f = open("./사전작업/worktype.txt", "r")

    while True:
        line = f.readline().strip()
        if not line: break
        option.append(line)

    for i, ID in enumerate(option):
        if(i == 0):
            self_crawl = ID
        else:
            test = ID

    if(self_crawl == 'True'): self_crawl = True
    else: self_crawl = False
    if(test == 'True'): test = True
    else: test = False

    return self_crawl, test
###############################################################################################################
#   <MAIN
###############################################################################################################
self_crawl, test = read_option()
print(" test : ", test)

path = ".\data_select\image"
createFolder('./data_select')
if os.path.exists(path):
    shutil.rmtree(path)
os.makedirs(path) #디테일 페이지 폴더 생성

select_list = read_select_list() # 아이템 번호 읽어오기
banlist = read_banlist_txt()

df1 = pd.DataFrame(columns=["Src", "Idx", "Prd_ID", "금지", "SoldOut","Now", "Brand", "Title", "code", "category3", "category4", "howto", "카테고리" \
                            "상품명_국어", "상품명_영어", "원래가격","마진가격","링크","썸네일주소"])

url = "https://www.ople.com/mall5/shop/item.php?it_id="
products = []
d_index = []
p = []

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--window-size=1920,1080')
options.add_experimental_option("excludeSwitches", ["enable-logging"])
browser = webdriver.Chrome(options=options)

for i, ID in enumerate(select_list):
    p = get_ople_product(i, ID, url)
    products.append(p)
# print(products)

df_prod = pd.DataFrame(products)
df1["Idx"] = df_prod["cnt"]
df1["Prd_ID"] = df_prod["Prd_ID"]
df1["SoldOut"] = df_prod["soldout"]
df1["Brand"] = df_prod["Brand"]
df1["Src"] = df_prod["Src"]
df1["Title"] = df_prod["Title"]
df1["Now"] = df_prod["Now"]
df1["howto"] = df_prod["howto"]
df1["링크"] = df_prod["링크"]

for i, ID in enumerate(select_list):
    category = naver_category(df_prod["Title"][i])		
    cat3 = df1["category3"].copy()
    cat4 = df1["category4"].copy()
    cat3[i] = category[2]
    cat4[i] = category[3]
    df1["category3"]= cat3
    df1["category4"]= cat4

    b = df_prod["Brand"].copy()
    if b[i].find(" ") > 0:
        b[i] = b[i].replace(" ","")
        brand = b[i].split(']')
        b[i] = brand[1]		
    df_prod["Brand"] = b

#카테고리 코드 확인
df1=df1.fillna('')
# df1.to_clipboard()
df2 = pd.read_excel("./사전작업/카테고리코드.xlsx", sheet_name=0)
df2=df2.fillna('')
df3 = pd.merge(df1, df2, how="left",on='category3')
df3=df3.fillna('')
df4 = pd.merge(df1, df2, how="left",on='category4')
# df4.to_clipboard()
df4=df4.fillna('')

for i, value in enumerate(df1["category4"]):
    # print("check category i:",i," value: ", value)
    if(value == ''):
        value = df1["category3"][i]
        index = df3.index[df3['category3']==value]
        cat_code = df3.loc[index, ['카테고리번호']].values[0]
    else:
        index = df4.index[df4['category4']==value]
        cat_code = df4.loc[index, ['카테고리번호']].values[0]

    # print(cat_code, cat_code[0])
    c = df1["code"].copy()
    c[i] = cat_code[0]
    df1["code"] = c
dt_today = datetime.date.today()
dt_now = datetime.datetime.now()
date = dt_now.strftime('%Y%m%d%H%M')
if(test):
    path = './data_select/result_'+date+'.xlsx'
else:
    path = './data_select/result_first'+'.xlsx'

with pd.ExcelWriter(path) as writer:
    df1.to_excel(writer, sheet_name=date, index=False)