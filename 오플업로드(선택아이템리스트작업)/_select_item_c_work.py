import time
import datetime
## 데이터 라이브러리
import pandas as pd
import os
from os import rename
import shutil
from distutils.dir_util import copy_tree

def file_check(path):
    file_name = path
    return os.path.isfile(file_name)

def my_code(list):
    code = df_final['상품코드'].copy()
    # print(code)
    for i, rd in enumerate(list['NO']):
        num_str = str(rd)
        # print("O"+num_str.zfill(4))
        code[i] = "O"+num_str.zfill(4)
    df_final['상품코드'] = code
    return

def make_image_name(list):
    img_src = 'https://cosmo2023.speedgabia.com/ople_upload/'
    f = df_final['대표이미지'].copy()
    a = df_final['추가이미지'].copy()
    for i, rd in enumerate(list['Prd_ID']):
        f_name = str(rd)+'.jpg'
        print(f_name)
        f[i] = img_src+f_name
        a_name = img_src+f_name
        for j in range(3):
            a_name += '\n'
            a_name += img_src+f_name
        a[i] = a_name      

    df_final['대표이미지'] = f
    df_final['추가이미지'] = a
    return

def detail_page(list):
    empty = '<p>&nbsp;</p>'
    event_img1 = '<img src="https://cosmo2023.speedgabia.com/banner_event1.jpg" />'
    event_img2 = '<img src="https://cosmo2023.speedgabia.com/banner_event2.jpg" />'
    notice_img1 = '<img src="https://cosmo2023.speedgabia.com/withusnotice1.jpg" />'
    notice_img2 = '<img src="https://cosmo2023.speedgabia.com/withusnotice2.jpg" />'
    img_src = '<img src="https://cosmo2023.speedgabia.com/ople_upload/'
    
    d = df_final['상세설명'].copy()
    # h = df_first['howto'].copy()
    
    for i, rd in enumerate(list['Prd_ID']):
        how = df_first['howto'][i]
        check = file_check('./renamed/'+str(rd)+'-type.jpg')
        d[i] = '<center>'
        d[i] += event_img1                  # event img 1
        d[i] += empty
        d[i] += '<h2 style="text-align: center;"><b>' + df_first['Brand'][i] + '</b></h2>'
        d[i] += empty
        d[i] += empty
        d[i] += empty
        d[i] += '<h1 style="text-align: center;font-size:30px"><b>' + df_first['Title'][i]  + '</b></h1>'
        d[i] += empty        
        d[i] += empty        
        d[i] += empty               
        d[i] += img_src + str(rd) +'.jpg"' + ' />'   # 상품이미지
        d[i] += empty
        d[i] += empty
        d[i] += empty        
        d[i] += '<h2>' + how + '</h2>'     # 용법
        d[i] += empty
        d[i] += empty        
        d[i] += empty
        if check:
            d[i] += img_src + str(rd) +'-type.jpg"' + ' />'   # 성분표
        d[i] += event_img2
        d[i] += empty
        d[i] += notice_img1
        d[i] += empty
        d[i] += notice_img2
        d[i] += empty
        d[i] += '</center>'
    df_final['상세설명'] = d    
    return

# 최종 업로드용 포맷으로 변경
def make_final_upload_format(list, final):
    if list['표시가격'][0] != '' :  #할인금액과 최종표시가격이 업데이트 된 상태에서만 작업할것.
        df_final['code'] = list['code']
        df_final['상품명'] = list['Title']
        df_final['판매가'] = list['표시가격']
        df_final['재고수량'] = 9999
        df_final['브랜드'] = list['Brand']
        df_final['브랜드'] = list['Brand']
        df_final['원산지코드'] = '0204000'
        df_final['수입사'] = '미국'
        df_final['배송비 템플릿코드'] = 2504042
        df_final['A/S 템플릿코드'] = 2504051
        df_final['PC즉시할인 값'] = 20000
        df_final['PC즉시할인 단위'] = '원'
        df_final['모바일즉시할인 값'] = 20000
        df_final['모바일즉시할인 단위'] = '원'
        df_final['포인트'] = 100
        df_final['포인트단위'] = '원'
        df_final['리뷰포인트1'] = 100
        df_final['리뷰포인트2'] = 100
        df_final['리뷰포인트3'] = 100
        df_final['리뷰포인트4'] = 100
        df_final['리뷰포인트5'] = 100
        return True
    else:
        print("표시가격 작업을 완료해주세요")
        return False

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

list_file = "./data_select/prod_result_ready.xlsx"
first_file = "./data_select/result_first.xlsx"

df_prod = pd.read_excel(list_file, keep_default_na=False)
df_prod = df_prod.fillna('')
df_first = pd.read_excel(first_file, keep_default_na=False)
df_first = df_first.fillna('')

df_final = pd.DataFrame(columns = ['상품코드','code','상품명','상품상태','판매가','부가세','재고수량','옵션형태','옵션명', \
'옵션값','옵션가','옵션 재고수량','직접입력 옵션','추가상품명','추가상품값','추가상품가','추가상품 재고수량', \
'대표이미지','추가이미지','상세설명','브랜드','제조사','제조일자','유효일자','원산지코드','수입사', \
'복수원산지여부','원산지 직접입력','미성년자 구매','배송비 템플릿코드','배송방법','택배사코드','배송비유형', \
'기본배송비','배송비 결제방식','"조건부무료-상품판매가 합계"','수량별부과-수량',"구간별-2구간수량", \
"구간별-3구간수량","구간별-3구간배송비","구간별-추가배송비",'반품배송비','교환배송비','지역별 차등 배송비', \
'별도설치비','상품정보제공고시 템플릿코드',"상품정보제공고시품명","상품정보제공고시모델명",\
"상품정보제공고시인증허가사항","상품정보제공고시제조자",'A/S 템플릿코드','A/S 전화번호','A/S 안내','판매자특이사항', \
"PC즉시할인 값","PC즉시할인 단위","모바일즉시할인 값","모바일즉시할인 단위","복수구매할인조건 값","복수구매할인조건 단위",\
"복수구매할인값","복수구매할인단위","포인트","포인트단위","리뷰포인트1", "리뷰포인트2","리뷰포인트3","리뷰포인트4", \
'리뷰포인트5',"무이자",'사은품','판매자바코드','구매평'])

res = make_final_upload_format(df_prod, df_final)
df_final = df_final.fillna('')

if res == True :
    my_code(df_prod) # 상품코드
    make_image_name(df_prod)   # 대표이미지, 추가이미지
    detail_page(df_prod)       # 상세페이지 

if res == True :
    dt_today = datetime.date.today()
    dt_now = datetime.datetime.now()
    date = dt_now.strftime('%Y%m%d%H%M')
    
    if(test):
        path = './data_select/final_result_'+date+'.xlsx'
    else:
        path = './data_select/final_result'+'.xlsx'
    # path = './final_result'+'.xlsx'
    with pd.ExcelWriter(path) as writer:
        df_final.to_excel(writer, sheet_name ='Sheet1', index=False)