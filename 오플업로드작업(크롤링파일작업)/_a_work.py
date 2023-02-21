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
    # df1 = pd.read_csv("./data_select/_data_select.csv",encoding='CP949')

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
    changedSTR = changedSTR.replace("X", "")
    changedSTR = changedSTR.replace(" 개", "개")
    changedSTR = changedSTR.replace(" 팩", "팩")
    changedSTR = changedSTR.replace("*", "")

    title = changedSTR
    ch = rd2
    if ch.find(" ") > 0:
        ch = ch.replace(" ","")
        brand = ch.split(']')
        #print(brand[0], brand[1])
        title = brand[1] + " " + title
        # print(title)
    t = df1["Title"].copy()
    t[idx] = title
    df1["Title"] = t
    return title
###############################################################################################################
#   naver_category
###############################################################################################################
client_id = "k9IWv41faJYngZh1tkQS"
client_secret = "1NBnolNm8Y"
tries = 0
def naver_category(key) :
    global result
    display = "1"
    try:
        query = key
        query = urllib.parse.quote(query)
        url = "https://openapi.naver.com/v1/search/shop?query=" + query+ "&display=" + display

        header_params = {"X-Naver-Client-Id":client_id, "X-Naver-Client-Secret":client_secret}
        time.sleep(1.0)
        html = requests.get(url, headers=header_params)
        if html.status_code == 200:
            data = html.json()
            for item in data['items']:
                result = (item['category1'], item['category2'], item['category3'], item['category4'])
        #print(html)
    except Exception as e:
        print(f'Exception occurs: {e.args}')
        if tries >= 3:
            print(f'Max reties exceeded. returns default value. \n url: {url}')
            result = (item['category1'], item['category2'], item['category3'], item['category4'])
            return result
        tries += 1
        return naver_category(key)
    
    return result

###############################################################################################################
#   get_ople_product
###############################################################################################################
def get_ople_product(cnt, url):

    # print(url)
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
        if product_title != 'Fail':
            if self_crawl == True:
                url_productimage = "https://img.ople.com/ople/item/"+ str(df1["Prd_ID"][i]) +"_l1"
                productimage_name = img_path + '/' + str(df1["Prd_ID"][i]) +".jpg" #제품사진 파일명
                urllib.request.urlretrieve(url_productimage,productimage_name) #해당 url에서 이미지를 다운로드 메소드

            element = browser.find_element(By.CSS_SELECTOR,'table.SupplementFacts')  
            element_png = element.screenshot_as_png
            detailpage_name = img_path+ '/' + str(df1["Prd_ID"][i]) + "-type.jpg" #제품상세소개 파일명

            with open(detailpage_name, "wb") as file:  
                file.write(element_png) 
    except:
        print("이미지 parsing error")

    #상품명 변경 (브랜드+)
    cat_title = name_change(cnt, product_title, brand_name)
    # df1.rename(columns={'브랜드','code'}, inplace=True)
    category = naver_category(cat_title)
    cat3 = df1["category3"].copy()
    cat4 = df1["category4"].copy()
    cat3[cnt] = category[2]
    cat4[cnt] = category[3]
    df1["category3"]= cat3
    df1["category4"]= cat4
    # print(category[2])
    # print(category[3])
    b = brand_name
    if b.find(" ") > 0:
        b = b.replace(" ","")
        brand = b.split(']')
        brand_name = brand[1]

    return {"src":"O", "brand": brand_name, "title":product_title, "price": price, "soldout": soldout, "howto":howto}

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)


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
###############################################################################################################
#   self_crawl 설정
#   제공된 폼 이용 = False,  자체 크롤링 폼 이용 = True
#   True : Prework 작업 선결할 것
#   False : 사전작업/OpleMakeForm.xlsx 작업 선결할 것
###############################################################################################################
sheetname = 'ople'

dt_now = datetime.datetime.now()
print(f"start time : {dt_now}")

self_crawl, test = read_option()
print("self_crawl : ", self_crawl, " test : ", test)

if self_crawl == True:
    path = './data_collect'
else:
    path = './data_crawl'

createFolder(path)

if self_crawl == True:
    img_path = path + '/image'
else:
    img_path = path + '/renamed'

if os.path.exists(img_path):
    shutil.rmtree(img_path)
os.makedirs(img_path) #디테일 페이지 폴더 생성

if self_crawl == True:
    list_file = "./data_collect/OpleMakeForm.xlsx"
else:
    list_file = "./사전작업/OpleMakeForm.xlsx"
df1 = pd.read_excel(list_file, keep_default_na=False)
df1 = df1.fillna('')

for i, prdID in enumerate(df1["링크"]):
    prdID = prdID.replace("https://www.ople.com/mall5/shop/item.php?it_id=","")
    q = df1["Prd_ID"].copy()
    q[i] = prdID
    df1["Prd_ID"] = q

products = []
d_index = []
p = []

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--window-size=1920,1080')
options.add_experimental_option("excludeSwitches", ["enable-logging"])
browser = webdriver.Chrome(options=options)

for i,link in enumerate(df1["링크"]):
    progress = str(i+1) + " of " + str(len(df1["링크"])) + ' : '+ link
    print(progress)  # 작업진행상태 알림

    if(df1["금지"][i] == 'o'):
        d_index.append(i)
        p = {"src":"O", "brand": '', "title":'금지성분', "price": 0, "soldout": '', "howto":''}
        products.append(p)
        print(f"{i+1} is 금지성분")
    else:
        p = get_ople_product(i, link)
        products.append(p)

        if products[i]['brand'] == '':
            d_index.append(i)
            print(f"{i+1} is 판매불가")

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

df_prod = pd.DataFrame(products)
df1["SoldOut"] = df_prod["soldout"]
df1["Brand"] = df_prod["brand"]
df1["Src"] = df_prod["src"]
df1["Now"] = df_prod["price"]
df1["howto"] = df_prod["howto"]
# print("P size:", len(products))
# print("d_index:", d_index)
df1.drop(d_index, axis=0, inplace=True)

dt_today = datetime.date.today()
dt_now = datetime.datetime.now()
date = dt_now.strftime('%Y%m%d%H%M')

if self_crawl == True:
    if(test):
        path = './data_collect/result_'+date+'.xlsx'
        sheetname += date
    else:
        path = './data_collect/result_first'+'.xlsx'
else:
    if(test):
        path = './data_crawl/result_'+date+'.xlsx'
        sheetname += date
    else:
        path = './data_crawl/result_first'+'.xlsx'
with pd.ExcelWriter(path) as writer:
    df1.to_excel(writer, sheet_name=sheetname, index=False)

print(f"end time : {dt_now}")    