import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import requests
from bs4 import BeautifulSoup
import urllib.request as req
import datetime as dt

def strip_text(data):
    sdata = data.replace("[","").replace("]","").replace("CDATA","").replace("<","").replace(">","").replace("!","").replace("청과","").replace("토마토대추","")
    sdata = sdata.replace("(","").replace(")","").replace("방울토마토","")
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
    if count == 0: return 0
    return total_page

def get_garak_price(bubin, date, pm, sangi, page):
    url = get_url(bubin, date, pm, sangi, page)
    res = requests.get(url)
    soup = BeautifulSoup(res.text,"lxml")
    lists = soup.find_all("list")

    result = ""
    for list in lists:
        pummok =  strip_text(list.find("pummok").get_text())
        pumjong = strip_text(list.find("pumjong").get_text())
        pumjong2 = strip_text(list.find("pum_name_imsi").get_text())
        ddd = strip_text(list.find("ddd").get_text())
        uun = strip_text(list.find("uun").get_text())
        corp_nm = strip_text(list.find("corp_nm").get_text())
        adj_dt = strip_text(list.find("adj_dt").get_text())
        injung = strip_text(list.find("injung_gubun").get_text())

        price = strip_text(list.find("pprice").get_text())
        print(f"{adj_dt} {corp_nm} {pumjong2} {ddd} {uun} {injung} {price}")
        result += adj_dt+" "+ corp_nm + " " + pumjong2 + " " +price + "\n"
    return result

def bubin_name(bubin):
    if(bubin == 11000101) :
        name = "서울청과"
    elif(bubin == 11000103) :        
        name = "중앙청과"
    else:
        name = "기타"
    return(name)
######## 크롤링 관련 함수 ########
def covid_num_crawling():
    code = req.urlopen("https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=%ED%99%95%EC%A7%84%EC%9E%90")
    soup = BeautifulSoup(code, "html.parser")
    info_num = soup.select("div.status_today em")
    result = int(info_num[0].string) + int(info_num[1].string)
    return result
 
def covid_news_crawling():
    code = req.urlopen("https://search.naver.com/search.naver?where=news&sm=tab_jum&query=%EC%BD%94%EB%A1%9C%EB%82%98")
    soup = BeautifulSoup(code, "html.parser")
    title_list = soup.select("a.news_tit")
    output_result = ""
    for i in title_list:
        title = i.text
        news_url = i.attrs["href"]
        output_result += title + "\n" + news_url + "\n\n"
        if title_list.index(i) == 2:
            break
    return output_result
 
####################################
 
######## 텔레그램 관련 코드 ########
token = "5989120682:AAHn2_eNEQO2IvsWIpS-bJLjU9xKT75jFTc"
id = "5705723422"

#서울청과 : 11000101
#중앙청과 : 11000103
bubin_list = {11000101, 11000103}

pageidx = 1
pummok = "대추"
sangi = "평택"
# date = 20230220

bot = telegram.Bot(token)
info_message = '''
가락시장 가격 업데이트 
오늘자 : go 또는 ㄱㄹ
특정일자 : Date
코로나뉴스 : ㅋㄹㄴ
'''
empty_message = '''
오늘은 경매결과가 없어요.
'''

bot.sendMessage(chat_id=id, text=info_message)
 
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
updater.start_polling()
 
### 챗봇 답장
def handler(update, context):
    user_text = update.message.text # 사용자가 보낸 메세지를 user_text 변수에 저장합니다.
    if (user_text == "go") or (user_text == "ㄱㄹ"):
        dt_today = dt.date.today()
        date = dt_today.strftime('%Y%m%d')
        for bubin in bubin_list:
            name = bubin_name(bubin)
            page = get_total_page(bubin, date, pummok, sangi, pageidx) #크롤링 1page
            if(page == 0) :
                message = name + empty_message
                bot.sendMessage(chat_id=id, text=message)
            else :
                for i in range(page):
                    result = get_garak_price(bubin, date, pummok, sangi,i+1) #크롤링 1page
                    bot.send_message(chat_id=id, text=result)
        bot.sendMessage(chat_id=id, text=info_message)

   # 코로나 관련 뉴스 답장
    elif (user_text == "Date"):
        bot.sendMessage(chat_id=id, text=info_message)
    elif (user_text[0:4] == "Date") :
        date = user_text[5:13]
        for bubin in bubin_list:
            name = bubin_name(bubin)
            page = get_total_page(bubin, date, pummok, sangi, pageidx) #크롤링 1page
            if(page == 0) :
                message = name + empty_message
                bot.sendMessage(chat_id=id, text=message)
            else :
                for i in range(page):
                    result = get_garak_price(bubin, date, pummok, sangi,i+1) #크롤링 1page
                    bot.send_message(chat_id=id, text=result)
        bot.sendMessage(chat_id=id, text=info_message)
    elif (user_text == "ㅋㄹㄴ"):
        covid_news = covid_news_crawling()
        bot.send_message(chat_id=id, text=covid_news)
        bot.sendMessage(chat_id=id, text=info_message)

echo_handler = MessageHandler(Filters.text, handler)
dispatcher.add_handler(echo_handler)
####################################
 