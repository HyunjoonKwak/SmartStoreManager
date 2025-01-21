###############################################################################################################
# 쿠팡,오플 가격 읽어서 스토어에 직접 가격 과 품절상태를 업데이트 하는 프로그램 v3
#   2023.05.03 : Update 시작
#   Ople 가격 도 읽어서 업데이트 하도록 수정
#   2023.05.07 : Update 시작
#   2023.05.14 : v2 시작
#   Target 기능 
#    - 개별적인 상품 인상율 적용 기능 추가
#    - Fail item retry 기능 추가
#    - result share by telegram 기능 추가
#   
###############################################################################################################
import datetime
import pandas as pd
import requests
from urllib3.exceptions import InsecureRequestWarning
import openpyxl as op
import win32com.client
import shutil
import os
import glob
from get_source_product_info import get_product, get_ople_product
from get_source_product_info import get_fail_reason_list
from get_source_product_info import reset_fail_reason_list
from store_product_work import get_price_update_list
from store_product_work import reset_price_update_list
from store_product_work import store_get_product, store_update_product
from tkinter import Tk, Label, Entry, Button

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

soldout_list = []       # 품절 list 변수 생성 
fail_list = []          # Fail list 변수 생성
fail_count = 0          # Fail count 변수 생성

# sellerCode, statusType, ProdutName, StorePrice, DiscountPrice, MobileDiscountPrice
sellerCode = "A001"
statusType = "SALE"
productName = "테스트 상품"
storePrice = 100000

discountPrice = 20000
mobileDiscountPrice = 20000
default_discountPrice = 20000
ople_default_discountPrice = 17500
soldout_discoutPrice = 1000
stock_amount = 9999

###############################################################################################################
#   product_info_update_raw : 상품정보를 업데이트 한다.
#   wss : 엑셀파일의 worksheet
#   value : 업데이트 할 값
###############################################################################################################
def product_info_update_raw(wss, pos, source_value, store_value, soldout, stock_amount, today):
    soldout_status = False

    if(store_value != 0 ):
        wss.cells(pos+2, 11).Value = store_value
    if(source_value != 0 ):
        wss.cells(pos+2, 12).Value = source_value

    wss.cells(pos+2, 9).ClearContents()
    if(stock_amount != 0 ):
        wss.cells(pos+2, 9).Value = stock_amount
       
    wss.cells(pos+2, 15).ClearContents()
    if(soldout != 0 ):
        soldout_status = wss.cells(pos+2, 14).Value      
        if(soldout_status == None): # 기존에 품절이 아니었음
            if(soldout == True):
                wss.cells(pos+2, 15).Value = "신규"
        else:
            if(soldout == False):
                wss.cells(pos+2, 15).Value = "해제"
            elif(soldout == True):
                wss.cells(pos+2, 15).Value = "유지"

    wss.cells(pos+2, 14).ClearContents()
    if(soldout != 0 ):
        wss.cells(pos+2, 14).Value = soldout

    wss.cells(pos+2, 16).Value = today
    return wss

###############################################################################################################
#   read_option_without_comment : 옵션파일을 읽어온다.
# path : 파일 경로
# fname : 상품목록 파일 이름
# start : 시작행 , paging : 읽어올 행의 수 
# up_margin : 인상 마진 , dn_margin : 인하 마진
# test : True 면 디버깅로그 출력 , False 면 디버깅로그 출력 안함
# margin : 기준 마진
# soldoutOption : 품절상태 처리 옵션 (Price_Up : 가격 인상, SoldOut_Disp : 품절표시)
# scan_range : 스캔 범위 (All : 전체, C : 쿠팡, O : 오플, A : Amazon, I: Iherb)
###############################################################################################################
def read_option_without_comment():
    option_list = []
    with open("./option.ini", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().split('#')[0].strip()
            decoded_line = line.encode('utf-8').decode('utf-8')
            option_list.append(decoded_line)
    path, fname, start, paging, up_margin, dn_margin, test, margin, soldoutOption, scan_range = option_list
    test = True if test == "True" else False
    margin = float(margin)
    return path, fname, int(start), int(paging), int(up_margin), int(dn_margin), test, margin , soldoutOption, scan_range


###############################################################################################################
#   Main 실행코드
###############################################################################################################
def main_function():
    passed, failed, skip = 0, 0, 0
    fail_list, result = [], []
    soldout_count = 0       # 품절 count 변수 생성

    dt_now = datetime.datetime.now()
    today = dt_now.strftime("%y%m%d")
    start_time = dt_now

    # Option 파일 읽기
    path, fname, start, paging, up_margin, dn_margin, test, margin, soldoutOption, scan_range = read_option_without_comment()

    # 파일 경로 생성
    list_file = path+fname
    if(test):
        print(f"file path : {list_file} , start = {start} , end = {paging}")    #files 리스트 값 출력

    # 인상 및 인하 마진 설정
    up = float(up_margin)
    dn = float(dn_margin)

    # 목표 마진율 설정
    t_margin = (float(margin) - 1.0) * 100
    t_margin = round(t_margin, 2)  # 소수점 2자리까지만 출력
    print(f"상품 마진율 : {t_margin}%, 기준마진 : up:{up} %, dn:{dn}%")

    # 상품리스트 엑셀파일 읽어서 DataFrame 형태로 저장
    df= pd.read_excel(list_file, keep_default_na=False)
    df=df.fillna('')

    df=df.iloc[:, :13]      # 13열까지만 읽어오기

    # 상품구분에 따라서 시작위치를 맞춰주는 작업 필요함. To Do List
    df_sub=df[start:paging].reset_index(drop=True) # start ~ paging 까지만 읽어오기

    #df_sub 의 갯수 출력
    print(f"상품 갯수 : {len(df_sub)}")

    ###############################################################################################################
    # Data Frmae 형태가 아닌 Excel 직접 컨트롤 해서 개별 Cell 에 접근
    ###############################################################################################################
    #엑셀 직접 실행
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True  #앞으로 실행과정을 보이게

    current_directory = os.getcwd()
    product_file = os.path.join(current_directory, list_file)

    wb = excel.Workbooks.Open(product_file) #기존에 생성된 문서를 Workbook 객체로 생성
    ws = wb.ActiveSheet #활성화 된 시트 "Sheet1"을 객체로 생성    
    col_max = wb.ActiveSheet.UsedRange.Columns.Count
    row_max = wb.ActiveSheet.UsedRange.Rows.Count
    # print(f"총 행 : {row_max}, 총 열 : {col_max}")
    ###############################################################################################################

    # 상품별로 for 문을 돌면서 구매처 링크에서 상품 정보를 읽어온다.
    for i, url in enumerate(df_sub["구매처링크"]):
        product_from = {"C": "CP", "O": "OP", "I": "IH",
                        "A": "AM"}.get(df_sub["구분"][i], "XX")
        if scan_range != "ALL":
            valid_product_from = {
                "C": "CP",
                "O": "OP",
                "I": "IH",
                "A": "AM"
            }
            if product_from != valid_product_from.get(scan_range):
                skip += 1
                continue
            else:
                pass
        else:
            pass
        
        ##################################################################################################################
        # 1. 구매처별로 상품 정보를 읽어온다.  
        # get_source_product_info.py
        ##################################################################################################################
        if product_from == "CP":
            p = get_product(url, 0, 4)
        elif product_from == "OP":
            p = get_ople_product(url, 0, 4)
        else:
            print(f"Get other price value {product_from}")
            passed += 1
        ##################################################################################################################
        
        # 상품 정보가 없으면 Fail list 에 추가하고 다음 상품으로 넘어간다.
        if p.get("price", 0) == 0:
            fail_list.append(f"{df_sub['판매자코드'][i]}:{df_sub['상품번호'][i]}")
            failed += 1
            ws = product_info_update_raw(ws, i, "상품정보없음", 0, 0, 0, 0)
            
        else:
            passed += 1

        #price 와 soldout 을 스토어 가격과 비교하는 루틴 추가
        #df 의 상품번호를 이용해서 스토어 가격을 가져온다.
        if p["price"] != 0 :       
            ##################################################################################################################
            # 2. 스마트스토어에 올라가 있는 정보를 읽어온다.  
            # store_product_work.py
            ##################################################################################################################
            sellerCode, statusType, productName, storePrice, discountPrice, mobileDiscountPrice, stock_amount = store_get_product(df_sub['상품번호'][i])            

            # 리스트에는 있으나 store 에 상품이 없는 경우 에러 처리 해야 함. 폴스가 리턴되는경우 처리ㅣ
            ##################################################################################################################
            if test:
                print("=====================================================================================================")
                print(f"읽어온 가격들과 모든 정보들을 출력한다. 여기서 부터 시작!")
                print(f"소싱처정보 : productNo : {df_sub['상품번호'][i]} , price(실제소싱가격) : {p['price']} , soldout : {p['soldout']} ")
                print(f"스토어정보 : Seller Code: {sellerCode} , Status Type : {statusType} , Product Name : {productName} , Store Price(할인전) : {storePrice} , Discount Price : {discountPrice} , Mobile Discount Price : {mobileDiscountPrice}, Stock Amount : {stock_amount}")
                
            soldout = True if p["soldout"] != "" else False
            
            if soldout:
                soldout_list.append(f"{sellerCode} : {df_sub['상품번호'][i]}")  # 품절상태인 경우 soldout_list 에 추가한다.
                soldout_count += 1
            

            ##################################################################################################################
            # 3.  소싱처의 정보와 스마트스토어의 정보를 비교해서 가격 업데이트를 할것인지 여부를 결정한다.
            # Main Logic
            ##################################################################################################################
            price_update = False

            # print(f"statusType : {statusType} , soldout : {soldout}, discountPrice : {discountPrice}, stock_amount : {stock_amount}")

            soldout_product = False
            if discountPrice == soldout_discoutPrice : soldout_product = True
            
            ############################################################################################
            # 소싱처에 따른 기본할인가격 반영
            ############################################################################################
            if product_from == 'CP':
                discountPrice = default_discountPrice
                mobileDiscountPrice = default_discountPrice
            elif product_from == 'OP':
                discountPrice = ople_default_discountPrice
                mobileDiscountPrice = ople_default_discountPrice
            else:
                print(f"Get other price value {product_from}")      

            # 여기서 각 상품별 마진율과 판매량을 읽어온다. To Do List
            margin_flag = True
            price_changed = False
            soldout_changed = False

            t_margin = ws.cells(i+2, 13).Value
            if(t_margin == None) :
                print(" 마진조정 하지 않음")
                margin_flag = False
                t_margin = 0.0

            if(margin_flag) :
                ############################################################################################
                # 가격 반영 조건 1 - 가격이 변한경우
                ############################################################################################
                # price_margin 을 구한다. : 소싱처에서 읽어온 가격에 마진 25% 를 더한 값에 할인값을 더한값
                t_margin += 1.0
                if test : print(f"개별 상품 마진율 : {t_margin*100}%")
                if(t_margin != margin) :
                    price_margin = int(p["price"] * t_margin) # price_margin : 개별마진 적용
                else :
                    price_margin = int(p["price"] * margin) # price_margin : 소싱처 가격에 공통마진 적용
                # price_margin += int(default_discountPrice)     # price_margin 에 Discount Price 를 더한 값
                price_margin += int(discountPrice)     # price_margin 에 Discount Price 를 더한 값

                # price_margin 과 storePrice 를 비교한다.
                # price_gap 을 구하고 up, dn 을 비교한다.
                if(test == True) :
                    print(f"price_margin(소싱처가격 + 스토어할인가격 + 마진) : {price_margin} , storePrice(할인반영 안된 스토어판매가격) : {storePrice}")

                # price_gap : 소싱처 가격과 Store Price 의 차이
                # percent : price_gap 을 Store Price 로 나눈 값에 100 을 곱한 값. 즉, 소싱처 가격이 Store Price 보다 얼마나 높은지 낮은지를 퍼센트로 표시한 값
                price_gap = price_margin - int(storePrice)
                percent = round(float(price_gap) / float(storePrice) * 100, 2)

                if price_gap != 0:        # price_gap 이 0 이면 가격변동 없고 price_gap 이 0 이 아니면 가격변동 있음
                    if price_gap > 0 and percent >= up:
                        price_update = True
                    elif price_gap < 0 and percent * -1 >= dn:
                        price_update = True     

                price_margin = round(price_margin, -1) # price_margin 을 10원단위로 반올림한다.

                if(price_update == True):
                    # print(f"가격변화 있어서 업데이트 필요함")
                    price_changed = True

                # 만약 price_update 가 False 이면 품절상태를 체크한다.
                # 즉, 가격변화는 없어서 업데이트 할 필요성은 없느나 품절상태가 변한 경우에는 업데이트 한다.
                if price_update == False:  
                    ############################################################################################
                    # 가격 반영 조건 2 - 품절상태가 변한경우
                    ############################################################################################
                    # soldout 이 True 인경우
                    if soldout == True:                              # 1
                        if soldoutOption == "Price_Up" :                 # 2
                            if statusType == "SOLD_OUT" :                   # 3    
                                if soldout_product == True :                    # 4    
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 1")
                                elif soldout_product == False :                 # 4
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 2")

                            elif statusType == "SALE" :                     # 3  
                                if soldout_product == True :                    # 4
                                    price_update = False
                                elif soldout_product == False :                 # 4
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 3 ====================================")

                        elif soldoutOption == "Soldout_Disp" :           # 2    
                            if statusType == "SOLD_OUT" :                   # 3    
                                if soldout_product == True :                    # 4
                                    price_update = False
                                elif soldout_product == False :                 # 4    
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 4")

                            elif statusType == "SALE" :                     # 3
                                if soldout_product == True :                    # 4    
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 5")
                                elif soldout_product == False :                 # 4    
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 6")

                    elif soldout == False:                          # 1
                        if soldoutOption == "Price_Up" :                # 2
                            if statusType == "SOLD_OUT" :                   # 3    
                                if soldout_product == True :                    # 4
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 7")
                                elif soldout_product == False :                 # 4
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 8")

                            elif statusType == "SALE" :                     # 3
                                if soldout_product == True :                    # 4   
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 9 ====================================")
                                elif soldout_product == False :                 # 4        
                                    price_update = False

                        elif soldoutOption == "Soldout_Disp" :          # 2
                            if statusType == "SOLD_OUT" :                   # 3
                                if soldout_product == True :                    # 4        
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 10")
                                elif soldout_product == False :                 # 4
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 11")

                            elif statusType == "SALE" :                     # 3
                                if soldout_product == True :                    # 4        
                                    soldout_changed = True
                                    print(f" 품절 상태 업데이트 필요 # 12")
                                elif soldout_product == False :                 # 4
                                    price_update = False
                    else:
                        print(f"soldout 상태 체크 오류")
                        price_update = False
                
                    if(soldout_changed) : 
                        print(f"품절상태 업데이트!! ")
                        price_update = True           
            else :
                print(f"가격 조정 하지 않음")
                price_update = False

            ##################################################################################################################
            # 4.  Price Update 가 True 이면 가격을 업데이트 한다. 
            # store_product_work.py
            ##################################################################################################################       
            if price_update:
                store_update_product(df_sub['상품번호'][i], price_margin, sellerCode, statusType, discountPrice, mobileDiscountPrice , soldout, soldoutOption)
            # if test:
                # print("")
                # print(f"가격 업데이트!!  변화율 : {percent} , 가격차이 : {price_gap} , 마진고려가격(할인전) : {price_margin} , 스토어가격(할인전) : {storePrice}")            
            # else:
                # if test:
                    # print(f"가격반영 안함 : 변화율 : {percent} , 가격차이 : {price_gap} , 마진고려가격(할인전) : {price_margin} , 스토어가격(할인전) : {storePrice}")
            ###########################################################################################################################################################################
            print("=====================================================================================================")        
            change_reason = ""
            if(price_update == True):
                if(price_changed == True):
                    change_reason = "가격변경"
                elif(soldout_changed == True):
                    change_reason = "품절변경"

            
            sold_disp = ""
            if(soldout == True):
                sold_disp = "품절"
            else:
                sold_disp = "판매중"

            if(price_update == True):
                final_disp_price_after = price_margin - discountPrice
                final_disp_price_before = storePrice-discountPrice      
                print(f"판매자코드: {sellerCode}, 상품번호: {df_sub['상품번호'][i]} , 변경여부: {change_reason} ,변경후: {final_disp_price_after} <= 변경전: {final_disp_price_before} , 판매상태 : {sold_disp}")
                result.append(f"판매자코드: {sellerCode}, 상품번호: {df_sub['상품번호'][i]} , 변경여부: {change_reason} ,변경후: {final_disp_price_after} <= 변경전: {final_disp_price_before} , 판매상태 : {sold_disp}")
            else:
                print(f"판매자코드: {sellerCode}, 상품번호: {df_sub['상품번호'][i]} , 판매상태 : {sold_disp}")
                result.append(f"판매자코드: {sellerCode}, 상품번호: {df_sub['상품번호'][i]} , 판매상태 : {sold_disp}")                
            

            if(soldout == False):
                if(price_update == True):
                    ws = product_info_update_raw(ws, i, p["price"], final_disp_price_after , soldout, stock_amount, today)
                else:
                    ws = product_info_update_raw(ws, i, p["price"], 0 , soldout, stock_amount, today)
            else:
                if(price_update == True):
                    ws = product_info_update_raw(ws, i, p["price"], price_margin - 1000 , soldout, stock_amount, today)
                else:
                    ws = product_info_update_raw(ws, i, p["price"], 0 , soldout, stock_amount, today)

        print("=====================================================================================================")        

    wb.Save()

    ## 최종결과 출력
    print(f"\n[RESULT] total: {failed+passed}, failed: {failed}, passed: {passed}")
    print(f"\n[SOLDOUT Count] total: {soldout_count}")
    for i, item in enumerate(soldout_list, start=1):
        print(f"{i} : {item}")
    print(f"\n[FAIL Count] total: {failed}")
    for i, item in enumerate(fail_list, start=1):
        print(f"{i} : {item}")

    nowDatetime = start_time.strftime('%Y%m%d%H%M%S')  # 20230101235959
    nowDatetime = nowDatetime[2:12] # nowDatetime 에서 날짜와 시간 추출
    # print(nowDatetime)

    if soldout_list:
        with open(f"{nowDatetime}_soldout_list.txt", 'w') as f:
            f.write('\n'.join(soldout_list))

    if fail_list:
        with open(f"{nowDatetime}_fail_list.txt", 'w') as f:
            f.write('\n'.join(fail_list))

    fail_reason_list = get_fail_reason_list()
    if fail_reason_list:
        with open(f"{nowDatetime}_fail_reason.txt", 'w') as f:
            f.write('\n'.join(fail_reason_list))
        reset_fail_reason_list()

    price_update_list = get_price_update_list()
    if price_update_list:    
        price_update_list = [str(item) for item in price_update_list] # int 형태로 저장되어 있어서 str 로 변환
        with open(f"{nowDatetime}_update_list.txt", 'w') as f:
            f.write('\n'.join(price_update_list))
        reset_price_update_list()

    if result:
        with open(f"{nowDatetime}_update_result.txt", 'w') as f:
            f.write('\n'.join(result))

    debug_folder_name = "DebugFolder"
    os.makedirs(debug_folder_name, exist_ok=True)

    for file in glob.glob(f"{nowDatetime}*.txt"):
        if os.path.isfile(os.path.join(debug_folder_name, file)):
            os.remove(os.path.join(debug_folder_name, file))
        shutil.move(file, debug_folder_name)

    excel.quit()

    end_time = datetime.datetime.now()

    print(f"start time : {start_time}")
    print(f"end time : {end_time}")

main_function()