import http.client
import pybase64
import json
import bcrypt
import schedule
import time
import requests
import datetime
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

client_id = "213tGtVIri480GpHZ2K2tD"
client_secret = "$2a$04$/6qDc21MqIwmIggCYNKqwO"
access_token = None
token_expiry = 0  # 토큰 만료 시간

def generate_client_secret_sign(timestamp):
    password = f"{client_id}_{timestamp}"
    hashed = bcrypt.hashpw(password.encode("utf-8"), client_secret.encode("utf-8"))
    return hashed

def get_access_token():
    global access_token, token_expiry
    current_time = int(time.time() * 1000)

    # 기존 토큰이 유효하면 재사용
    if access_token and current_time < token_expiry:
        return access_token

    try:
        client_secret_sign = generate_client_secret_sign(current_time)
        client_secret_sign = pybase64.standard_b64encode(client_secret_sign).decode("utf-8")

        url = "https://api.commerce.naver.com/external/v1/oauth2/token"
        data = {
            "client_id": client_id,
            "timestamp": current_time,
            "client_secret_sign": client_secret_sign,
            "grant_type": "client_credentials",
            "type": "SELF"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = requests.post(url, data=data, headers=headers)
        res.raise_for_status()

        json_data = res.json()
        access_token = json_data.get("access_token")
        token_expiry = current_time + 3600 * 1000  # 1시간 만료 시간 설정
        return access_token
    except Exception as e:
        print(f"Error fetching access token: {e}")
        return None

def format_datetime(dt):
    return quote(dt.astimezone(timezone.utc).isoformat())

def get_order_status(start_time, end_time):
    try:
        token = get_access_token()
        if not token:
            return 0, []

        start_time = format_datetime(start_time)
        end_time = format_datetime(end_time)
        url = f"https://api.commerce.naver.com/external/v1/pay-order/seller/product-orders/last-changed-statuses?lastChangedFrom={start_time}&lastChangedType=PAYED"
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(url, headers=headers)
        res.raise_for_status()

        data = res.json()
        if "data" not in data or not data["data"]:
            return 0, []

        orders = data["data"]["lastChangeStatuses"]
        order_ids = [order["productOrderId"] for order in orders]
        return len(order_ids), order_ids
    except Exception as e:
        print(f"Error fetching order status: {e}")
        return 0, []

def get_order_detail(order_id):
    try:
        token = get_access_token()
        if not token:
            return None

        url = "https://api.commerce.naver.com/external/v1/pay-order/seller/product-orders/query"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {"productOrderIds": [order_id]}
        res = requests.post(url, json=payload, headers=headers)
        res.raise_for_status()

        data = res.json()
        if "data" not in data or not data["data"]:
            print(f"Order detail not found for ID {order_id}")
            return None

        order = data["data"][0]["order"]
        productOrder = data["data"][0]["productOrder"]
        print("========================================")
        print(f"주문 상세 정보")
        for key, value in order.items():
            print(f"{key}: {value}")
        print("========================================")
        # print(f"상품 주문 정보: {productOrder}")
        print("상품주문정보")
        for key, value in productOrder.items():
            print(f"{key}: {value}")
        print("========================================")
# ========================================
# 주문 상세 정보
# payLocationType: MOBILE
# orderId: 2025012420927911
# paymentDate: 2025-01-24T00:59:41.0+09:00
# chargeAmountPaymentAmount: 19900
# generalPaymentAmount: 0
# naverMileagePaymentAmount: 0
# orderDiscountAmount: 0
# ordererId: king****
# ordererName: 곽현준
# payLaterPaymentAmount: 0
# orderDate: 2025-01-24T00:59:36.0+09:00
# paymentMeans: 포인트결제
# isDeliveryMemoParticularInput: false
# ordererTel: 01089765834
# ordererNo: 206643731
# ========================================
# 상품주문정보
# merchantChannelId: 101150711
# quantity: 1
# mallId: ncp_1o6fme_01
# productOrderId: 2025012451007191
# deliveryDiscountAmount: 0
# optionCode: 39079754319
# packageNumber: 2025012499775747
# placeOrderStatus: NOT_YET
# shippingAddress: {'isRoadNameAddress': True, 'addressType': 'DOMESTIC', 'detailedAddress': '1501동 2202호', 'tel1': '010-8976-5834', 'zipCode': '18476', 'baseAddress': '경기도 화성시 동탄대로시범길 134 (청계동, 시범 반도유보라 아이비파크4.0)', 'name': '곽현준'}
# shippingDueDate: 2025-02-04T23:59:59.0+09:00
# shippingFeeType: 무료
# totalPaymentAmount: 19900
# totalProductAmount: 69000
# productOrderStatus: PAYED
# productId: 8975618028
# productName: [GAP] 당일수확 신선한 대추방울토마토 오색 대추 방울토마토 1.5kg,3kg
# productOption: 품목선택: 빨강 대추방울토마토 1.5 kg
# unitPrice: 69000
# productDiscountAmount: 49100
# deliveryFeeAmount: 0
# sellerBurdenDiscountAmount: 49100
# deliveryAttributeType: NORMAL
# itemNo: 39079754319
# productClass: 조합형옵션상품
# optionPrice: 0
# deliveryPolicyType: 무료
# sectionDeliveryFee: 0
# knowledgeShoppingSellingInterlockCommission: 398
# expectedDeliveryMethod: DELIVERY
# initialProductDiscountAmount: 49100
# remainProductDiscountAmount: 49100
# originalProductId: 8933338895
# initialQuantity: 1
# remainQuantity: 1
# sellerProductCode: P001
# takingAddress: {'isRoadNameAddress': True, 'addressType': 'DOMESTIC', 'detailedAddress': '마두길 59-450', 'tel1': '010-4671-2023', 'tel2': '010-4671-2023', 'zipCode': '17702', 'baseAddress': '경기도 평택시 서탄면', 'name': '평택농장'}
# initialPaymentAmount: 19900
# remainPaymentAmount: 19900
# initialProductAmount: 69000
# remainProductAmount: 69000
# commissionRatingType: 결제수수료
# commissionPrePayStatus: GENERAL_PRD
# paymentCommission: 394
# saleCommission: 0
# expectedSettlementAmount: 19108
# inflowPath: 네이버페이>홈(네이버쇼핑)
# inflowPathAdd: null
# optionManageCode: 1
# channelCommission: 0
# productImediateDiscountAmount: 49100
# sellerBurdenImediateDiscountAmount: 49100
# expectedDeliveryCompany: HANJIN
# ========================================

        return order
    except Exception as e:
        print(f"Error fetching order detail for ID {order_id}: {e}")
        return None

def check_orders(start_time, end_time):
    count, order_ids = get_order_status(start_time, end_time)
    print(f"Orders found: {count}")
    for order_id in order_ids:
        get_order_detail(order_id)

# 실행
start_time = datetime.now() - timedelta(days=1)
end_time = datetime.now()
check_orders(start_time, end_time)