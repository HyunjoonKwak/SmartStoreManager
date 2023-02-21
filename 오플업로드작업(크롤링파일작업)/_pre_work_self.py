import time
import time
import datetime
## 데이터 라이브러리
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os

###############################################################################################################
# 선택아이템 : it_id
# https://www.ople.com/mall5/shop/item.php?it_id=

# 대상별 
# https://www.ople.com/mall5/shop/list.php?ca_id=

# 판매량 많은 순서 200개 url  ca_id
# https://www.ople.com/mall5/shop/list.php?ca_id=10&ev_id=&sort=sales_volume+desc&it_maker=&items=200&page=

#hot 100
# https://www.ople.com/mall5/shop/best_item.php?s_id=1  # 뷰티용품
# https://www.ople.com/mall5/shop/best_item.php?s_id=2  # 식품
# https://www.ople.com/mall5/shop/best_item.php?s_id=3  # 건강식품
# https://www.ople.com/mall5/shop/best_item.php?s_id=4  # 생활용품
# https://www.ople.com/mall5/shop/best_item.php?s_id=5  # 출산육아
# https://www.ople.com/mall5/shop/best_item.php?s_id=6  # 건강식품
# https://www.ople.com/mall5/shop/best_item.php?s_id=7  # 헬스다이어트
###############################################################################################################

def get_ople_list(url_ople, page):
    url_ople = url_ople + str(page)
    print(url_ople)
    
    #페이지 접근
    browser.get(url_ople)
    results_title = browser.find_elements(By.CSS_SELECTOR, ".item_box")
    for result in results_title:
        product_link = result.find_element(By.CSS_SELECTOR, ".item_title>a").get_attribute("href")
        p = {"링크":product_link}
        products.append(p)
    return 

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

if __name__ == '__main__':
    print('main function')

    self_crawl, test = read_option()
    print("self_crawl : ", self_crawl, " test : ", test)

    #hot 100
    url = "https://www.ople.com/mall5/shop/best_item.php?s_id=3"
    url = "https://www.ople.com/mall5/shop/best_item.php?s_id=7"
    # url = "https://www.ople.com/mall5/shop/list.php?ca_id=70&ev_id=&sort=sales_volume+desc&it_maker=&items=200&page="
    page = 3
    sheetname = 'hot100'


    createFolder('./data_collect')

    df1 = pd.DataFrame(columns=["Src", "Idx", "Prd_ID", "금지", "SoldOut","Now", "Brand", "Title", "code", "category3", "category4", "howto", "카테고리", \
                                "브랜드", "상품명_국어", "상품명_영어", "원래가격","마진가격","링크","썸네일주소"])

    products = []

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(options=options)

    for i in range(page) : 
        get_ople_list(url, i+1) #크롤링 1page
        time.sleep(1)

    df_prod = pd.DataFrame(products)
    df1["링크"] = df_prod["링크"]

    if(test):
        dt_today = datetime.date.today()
        dt_now = datetime.datetime.now()
        date = dt_now.strftime('%Y%m%d%H%M')
        path = './data_collect/OpleMakeForm_'+date+'.xlsx'
    else:
        path = './data_collect/OpleMakeForm'+'.xlsx'

    with pd.ExcelWriter(path) as writer:
        df1.to_excel(writer, sheet_name=sheetname, index=False)
    print("main function end")