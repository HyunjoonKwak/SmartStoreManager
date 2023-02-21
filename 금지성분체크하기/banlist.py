import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv
import os

#
#  현재 banlist 랑 _data_detail.csv 읽어서 비교하는 부분만 떼서 정리했고, 금지성분을 원래 액셀에 업데이트 하는 부분 추가완성필요함. (23.1.15)
#

#read banlist.txt
def read_banlist_txt() : 
    banlist = []
    with open('banlist.txt', 'r') as fo : 
        while True :
            k=fo.readline()
            #print(k)
            if k=='' :
                break
            else : 
                k = k.replace("\n","")
                banlist.append(k) #data 분류 
    return banlist

def start_banlist_check(banlist, itemNumber):
    option = Options()
    option.add_argument('headless')
    option.add_argument('--window-size=1920,1080')
    browser = webdriver.Chrome(options=option)

    url_detailpage = "https://www.ople.com/mall5/shop/item.php?it_id=" + itemNumber
    print(url_detailpage)
    browser.get(url_detailpage)
    print("sleep start")
    time.sleep(3)
    
    try : 
        #금지성분 파싱
        html = browser.page_source
        b_soup = BeautifulSoup(html, 'html.parser')
        htmltext = b_soup.get_text().lower()
        htmltext = htmltext.replace("box","")
        ban = "no"
        ban1 = "no"
        for list in banlist :
            list_text = list.lower()
            list_text1 = " " + list_text + " "
            list_text2 = list_text + " "
            if htmltext.find(list_text1) > -1 :
                ban = list_text

            if htmltext.find(list_text2) > -1 :
                ban1 = list_text
    except Exception as e:
        print("error@@@@@@@@@ ", e)
    
data_csv = []
with open('_data_detail.csv', 'r') as f : 
    while True :
        k=f.readline()
        print(k)
        if k=='' :
            break
        else : 
            k = k.split(",")
            #k[7] = k[7].replace("\n","")
            data_csv.append([k[0], k[1], k[2]]) #data 분류 (num, product_id)

banList = read_banlist_txt()
print("items : " + str(len(data_csv)-1))
print("banlist : " + str(len(banList)))

list_size = int(str(len(data_csv)-1))

numTemp = 0

#URL 이나 상품명을 입력받고 그 페이지를 찾아서 금지성분을 체크한다.
for num in range(list_size):
    numtemp = num
    start_banlist_check(banList, data_csv[numtemp+1][1])

f.close