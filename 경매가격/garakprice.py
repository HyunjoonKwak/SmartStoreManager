import requests
from bs4 import BeautifulSoup
import datetime as dt
import xml.etree.ElementTree as ET

def strip_text(data):
    sdata = data.replace("[","").replace("]","").replace("CDATA","").replace("<","").replace(">","").replace("!","")
    return sdata

def get_url(bubin, date, pm, sangi, page):
    url = "http://www.garak.co.kr/publicdata/dataOpen.do?id=3327&passwd=guswns72!&dataid=data12&pagesize=10&" \
        + "pageidx=" + str(page) \
        + "&portal.templet=false&" \
        + "s_date=" + str(date) \
        + "&s_bubin=" + str(bubin) \
        + "&s_pummok=" + pm \
        + "&s_sangi=" + sangi
    url = url.encode('utf8')
    return url

def get_total_page(bubin, date, pm, sangi, page):
    url = get_url(bubin, date, pm, sangi, page)
    res = requests.get(url)
    soup = BeautifulSoup(res.text,"lxml")
    count = int(soup.find("list_total_count").get_text())
    total_page = int(count / 11 + 1)
    print(f"count {count} , page {total_page}")
    return total_page

def get_garak_price(bubin, date, pm, sangi, page):
    url = get_url(bubin, date, pm, sangi, page)
    res = requests.get(url)
    soup = BeautifulSoup(res.text,"lxml")
    lists = soup.find_all("list")

    for list in lists:
        pummok =  strip_text(list.find("pummok").get_text())
        pumjong = strip_text(list.find("pumjong").get_text())
        pumjong2 = strip_text(list.find("pum_name_imsi").get_text())
        ddd = strip_text(list.find("ddd").get_text())
        uun = strip_text(list.find("uun").get_text())
        corp_nm = strip_text(list.find("corp_nm").get_text())
        adj_dt = strip_text(list.find("adj_dt").get_text())
        injung = strip_text(list.find("injung_gubun").get_text())

        price = int(strip_text(list.find("pprice").get_text()))
        print(f"{adj_dt} {corp_nm} {pumjong2} {ddd} {uun} {injung} {price}")

#서울청과 : 11000101
#중앙청과 : 11000103
bubin_list = {11000101, 11000103}

pageidx = 1
pummok = "대추"
sangi = "평택"
dt_today = dt.date.today()
date = dt_today.strftime('%Y%m%d')
date = 20230219

for bubin in bubin_list:
    page = get_total_page(bubin, date, pummok, sangi, pageidx) #크롤링 1page

    for i in range(page):
        get_garak_price(bubin, date, pummok, sangi,i+1) #크롤링 1page
