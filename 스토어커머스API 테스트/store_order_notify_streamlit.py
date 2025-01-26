import streamlit as st
import requests
import pybase64
import time
import bcrypt
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

# 클라이언트 정보
client_id = "213tGtVIri480GpHZ2K2tD"
client_secret = "$2a$04$/6qDc21MqIwmIggCYNKqwO"
access_token = None
token_expiry = 0  # 토큰 만료 시간


# Helper Functions
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
        st.error(f"Error fetching access token: {e}")
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
        url = f"https://api.commerce.naver.com/external/v1/pay-order/seller/product-orders/last-changed-statuses?lastChangedFrom={start_time}&lastChangedTo={end_time}&lastChangedType=PAYED"

        headers = {"Authorization": f"Bearer {token}"}

        # st.write(f"Request URL: {url}")
        # st.write(f"Start Time: {start_time}, End Time: {end_time}")        

        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            st.error(f"Request failed with status {res.status_code}")
            st.write(f"Response: {res.text}")
            return 0, []

        # res.raise_for_status()

        data = res.json()
        # st.write(f": {data}")
        if "data" not in data or not data["data"]:
            return 0, []

        orders = data["data"]["lastChangeStatuses"]
        order_ids = [order["productOrderId"] for order in orders]
        return len(order_ids), order_ids
    except Exception as e:
        st.error(f"Error fetching order status: {e}")
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
            st.warning(f"Order detail not found for ID {order_id}")
            return None

        order = data["data"][0]["order"]
        product_order = data["data"][0]["productOrder"]

        shipping_info = product_order["shippingAddress"]
        return {
            "Orderer Name": shipping_info["name"],
            "Phone": shipping_info["tel1"],
            "Address1": shipping_info["baseAddress"],
            "Address2": shipping_info["detailedAddress"],
            "Zip Code": shipping_info["zipCode"],
            "Order Date": order["orderDate"],
        }
    except Exception as e:
        st.error(f"Error fetching order detail for ID {order_id}: {e}")
        return None


def check_orders(start_time, end_time):
    count, order_ids = get_order_status(start_time, end_time)
    # st.write(f"Orders found: {count}")
    for order_id in order_ids:
        get_order_detail(order_id)


# Streamlit App Title
st.title("Naver Commerce Order Viewer")

# 현재 시간 가져오기
current_time = datetime.now()
st.write(f"Current Time: {current_time}")

# 세션 상태 초기화
if "start_date" not in st.session_state:
    st.session_state.start_date = current_time - timedelta(weeks=1)  # 1주일 전
if "end_date" not in st.session_state:
    st.session_state.end_date = current_time - timedelta(seconds=5)  # 5초 전

# 날짜 입력 UI (세션 상태 활용)
start_date = st.date_input("Start Date", value=st.session_state.start_date)
end_date = st.date_input("End Date", value=st.session_state.end_date)

# 시간 변환 (현재 시간 활용)
start_time = datetime.combine(start_date, datetime.min.time()).replace(
    hour=current_time.hour,
    minute=current_time.minute,
    second=current_time.second,
    microsecond=current_time.microsecond,
)

end_time = datetime.combine(end_date, datetime.min.time()).replace(
    hour=current_time.hour,
    minute=current_time.minute,
    second=current_time.second,
    microsecond=current_time.microsecond,
)

def fetch_orders_in_chunks(start_time, end_time):
    """
    24시간 단위로 검색 범위를 분할하여 API 호출. 요청 사이에 1초 딜레이 추가.
    """
    total_orders = 0
    order_details = []
    current_start = start_time

    while current_start < end_time:
        # 현재 시작 시간에서 24시간 뒤를 계산
        next_end = min(current_start + timedelta(days=1), end_time)

        st.write(f"주문일자별 검색 {current_start.date()} to {next_end.date()}...")
        # 

        # API 호출 (24시간 단위)
        count, order_ids = get_order_status(current_start, next_end)
        total_orders += count

        for order_id in order_ids:
            details = get_order_detail(order_id)
            if details:
                order_details.append(details)

        # 다음 24시간 구간으로 이동
        current_start = next_end

        # 1초 대기
        time.sleep(1)

    return total_orders, order_details

# Check Orders 버튼 클릭 시
if st.button("Check Orders"):
    # 세션 상태에 현재 입력된 날짜 저장
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date

    with st.spinner("주문검색 시작.."):
        # 하루 이상 검색이 필요한 경우 반복 호출
        total_orders, order_details = fetch_orders_in_chunks(start_time, end_time)

        st.write(f"총 주문건: {total_orders}")
        for detail in order_details:
            st.json(detail)