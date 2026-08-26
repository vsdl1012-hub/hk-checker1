import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

TARGET_URL = "https://p-bandai.com/hk/item/A2866729001"
WEBHOOK_URL = "https://discord.com/api/webhooks/1541789079786487828/XvaI0Ol-R0z4Q4vp2E9U7SOX8ILXEvToXcnxYV1iSf-6-VdqHo2podEJP0VBXtg78f63"

def check_stock():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print(f"페이지 접속 중: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        # 자바스크립트 로딩 대기
        time.sleep(5)
        
        page_text = driver.page_source.lower()
        
        # 1. 대만어 '送出訂單' 또는 2. 영어 'pre-order' 중 하나라도 있는지 검사
        has_chinese_btn = "送出訂單" in driver.page_source
        has_english_btn = "pre-order" in page_text
        
        if has_chinese_btn or has_english_btn:
            send_alert(f"🚨 [알림] 대만 반다이 상품 구매 가능 상태 감지!\n주소: {TARGET_URL}")
            print("구매 문구(送出訂單 또는 pre-order) 감지 성공!")
            return True
        else:
            print("아직 '送出訂單' 또는 'pre-order' 문구가 없습니다. (품절 상태)")
            return False
            
    except Exception as e:
        print(f"에러 발생: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def send_alert(message):
    data = {"content": message}
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"웹훅 전송 실패: {e}")

if __name__ == "__main__":
    check_stock()
