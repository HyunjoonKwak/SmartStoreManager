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
        # print("========================================")
        # print(f"주문 상세 정보")
        # for key, value in order.items():
        #     print(f"{key}: {value}")
        # print("========================================")
        # # print(f"상품 주문 정보: {productOrder}")
        # print("상품주문정보")
        # for key, value in productOrder.items():
        #     print(f"{key}: {value}")
        # print("========================================")

        # print(f" Address : {productOrder['shippingAddress']}")
        print(f" Name : {productOrder['shippingAddress']['name']}")
        print(f" Phone : {productOrder['shippingAddress']['tel1']}")
        print(f" Address1 : {productOrder['shippingAddress']['baseAddress']}")
        print(f" Address2 : {productOrder['shippingAddress']['detailedAddress']}")
        print(f" ZipCode : {productOrder['shippingAddress']['zipCode']}")
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
