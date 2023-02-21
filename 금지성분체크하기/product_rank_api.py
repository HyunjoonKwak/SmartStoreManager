from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time
import pyperclip
import pyautogui
import os
import sys
import requests
import openpyxl
import re
import pandas as pd

client_id = "k9IWv41faJYngZh1tkQS"
client_secret = "1NBnolNm8Y"

def findBigmall(mall):
    if re.match(mall, "네이버"):
        res = True
    elif re.match(mall, "쿠팡"):
        res = True
    elif re.match(mall, "인터파크"):
        res = True
    elif re.match(mall, "11번가"):
        res = True
    elif re.match(mall, "옥션"):
        res = True
    elif re.match(mall, "G마켓"):
        res = True
    elif re.match(mall, "롯데ON"):
        res = True
    elif re.match(mall, "이마트몰"):
        res = True
    elif re.match(mall, "티몬"):
        res = True
    elif re.match(mall, "SSG닷컴"):
        res = True
    elif re.match(mall, "위메프"):
        res = True
    else:
        res = False
    return res

def naverapirank(cnt,key,code,src):
    storetotal = 0
    naverstore = 0
    store_rank = 0
    start, num = 1, 0
    excel_file = openpyxl.Workbook()
    excel_sheet = excel_file.active
    excel_sheet.column_dimensions['A'].width = 4
    excel_sheet.column_dimensions['B'].width = 5
    excel_sheet.column_dimensions['C'].width = 11
    excel_sheet.column_dimensions['D'].width = 50
    excel_sheet.column_dimensions['E'].width = 15
    excel_sheet.column_dimensions['F'].width = 15
    excel_sheet.column_dimensions['G'].width = 10
    excel_sheet.append(['Src' ,'num' , 'Product_id', 'title', 'Naver', 'Total', 'Store_rank'])

    key = key.replace("2개 세트","")
    key = key.replace("3개 세트","")
    key = key.replace("4개 세트","")
    key = key.replace("5개 세트","")
    key = key.replace("세트","")
    encText = key

    for index in range(2):
        start_number = start + (index * 50)
        url = 'https://openapi.naver.com/v1/search/shop.json?query='+encText+'&display=50&start=' + str(start_number)
        header_params = {"X-Naver-Client-Id":client_id, "X-Naver-Client-Secret":client_secret}
        res = requests.get(url, headers=header_params)

        if res.status_code == 200:
            data = res.json()
            for item in data['items']:
                storetotal += 1
                checkBig = findBigmall(item['mallName'])
                if checkBig == False:
                    naverstore += 1

                if "위더스" in item['mallName'] : # <<< 여기에 스토어명
                    store_rank = storetotal
                #num += 1
                #excel_sheet.append([src, num, code, key, item['mallName'], checkBig, item['link'],])
        else:
            print ("Error Code:", res.status_code)

    excel_sheet.append([src, cnt, code, key, naverstore, storetotal, store_rank])
    excel_file.save('./data/_rank_check_result.xlsx')
    excel_file.close()

def naverapirank_multi(cnt,title,code,src):
    storetotal = 0
    naverstore = 0
    store_rank = 0
    start, num = 1, 0
    excel_file = openpyxl.Workbook()
    excel_sheet = excel_file.active
    excel_sheet.column_dimensions['A'].width = 4
    excel_sheet.column_dimensions['B'].width = 5
    excel_sheet.column_dimensions['C'].width = 11
    excel_sheet.column_dimensions['D'].width = 50
    excel_sheet.column_dimensions['E'].width = 15
    excel_sheet.column_dimensions['F'].width = 15
    excel_sheet.column_dimensions['G'].width = 10
    excel_sheet.append(['Src' ,'num' , 'Product_id', 'title', 'Naver', 'Total', 'Store_rank'])

    for i, key in enumerate(title):
        key = key.replace("2개","")
        key = key.replace("3개","")
        key = key.replace("4개","")
        key = key.replace("5개","")
        key = key.replace("세트","")
        encText = key
        #print(key)
        print(src[i])
        print(code[i])
        for index in range(2):
            start_number = start + (index * 50)
            url = 'https://openapi.naver.com/v1/search/shop.json?query='+encText+'&display=50&start=' + str(start_number)
            header_params = {"X-Naver-Client-Id":client_id, "X-Naver-Client-Secret":client_secret}
            res = requests.get(url, headers=header_params)

            if res.status_code == 200:
                data = res.json()
                for item in data['items']:
                    storetotal += 1
                    checkBig = findBigmall(item['mallName'])
                    if checkBig == False:
                        naverstore += 1

                    if "위더스" in item['mallName'] : # <<< 여기에 스토어명
                        store_rank = storetotal
                    #num += 1
                    #excel_sheet.append([src, num, code, key, item['mallName'], checkBig, item['link'],])
            else:
                print ("Error Code:", res.status_code)

        excel_sheet.append(["src[i]", cnt, "code[i]", key, naverstore, storetotal, store_rank])
        excel_file.save('./data/_rank_check_result_multi.xlsx')
        excel_file.close()

#fr = open(r"./data/_rankcheck.csv",'r', encoding='CP949')#encoding='CP949''euc-kr', 'cp949' 'utf-8'
# NAME.csv 데이터 순서 -> NUM 검색어 판매자CODE
#csvReader = csv.reader(fr)

#cnt = 0
#for rd in csvReader :
#    cnt+=1
#    if cnt > 1 :
#        print("start = " + rd[1] + "/" + rd[2])
#        naverapirank(rd[1], rd[2], rd[3],rd[0])
#
#fr.close()

df1 = pd.read_excel("./data/Latest.xlsx", sheet_name=0)
df1=df1.fillna('')

naverapirank_multi(df1["NO"], df1["상품명"], df1["product_id"],df1["Src"])