from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time
import pyperclip
import pyautogui

def navershopping(num, key, code, src, csvwriter) :
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    browser = webdriver.Chrome(options=chrome_options)
    url = "https://search.shopping.naver.com/search/all?frm=NVSHATC&pagingIndex=1&pagingSize=80&productSet=total&sort=rel&timestamp=&viewType=list&query="
    key = key.replace("2개 세트","")
    key = key.replace("3개 세트","")
    key = key.replace("4개 세트","")
    key = key.replace("5개 세트","")
    key = key.replace("세트","")

    browser.get(url+key)

    for i in range(9) :
        pyautogui.hotkey('end') #<< 스크롤 end키로 9번 내려서 80개 끝까지 내리기
        time.sleep(0.5)
    time.sleep(0.5)
    storettl = 0
    naverstore = 0
    boga_num = 0

    try : 
        itemes = browser.find_elements(By.CLASS_NAME,'basicList_mall__BC5Xu')
        for item in itemes :
            storettl += 1
            if len(item.text) > 1 :
                naverstore += 1
            if item.text.find("위더스") >= 0 : # <<< 여기에 스토어명
                boga_num = storettl
    except :
        print("error")

    csvwriter.writerow([src, num, code, key, naverstore, storettl, boga_num])
    print(str(naverstore) + " / " + str(storettl))
    browser.close()


f = open(r"./data/rankcheck_result.csv",'w', encoding='CP949', newline='')
csvWriter = csv.writer(f)
csvWriter.writerow(["Source","num", "product_id", "title", "Naver", "Total", "store_rank"])

fr = open(r"./data/_rankcheck.csv",'r', encoding='CP949')#encoding='CP949''euc-kr', 'cp949' 'utf-8'
# NAME.csv 데이터 순서 -> NUM 검색어 판매자CODE
csvReader = csv.reader(fr)

cnt = 0
for rd in csvReader :
    cnt+=1
    if cnt > 1 :
        print("start = " + rd[1] + "/" + rd[3])
        navershopping(rd[1], rd[3], rd[2],rd[0], csvWriter)

f.close()
fr.close()