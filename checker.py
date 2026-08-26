import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

TARGET_URL = "https://p-bandai.com/hk/item/AZ005710001"
WEBHOOK_URL = "https://discord.com/api/webhooks/1541789079786487828/XvaI0Ol-R0z4Q4vp2E9U7SOX8ILXEvToXcnxYV1iSf-6-VdqHo2podEJP0VBXtg78f63"

def check_stock():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=zh-TW")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"페이지 접속 중: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        # 페이지 렌더링 대기
        time.sleep(7)
        
        page_source = driver.page_source
        
        if "PAGE NOT AVAILABLE" in page_source:
            print("홍콩 서버의 봇 차단(PAGE NOT AVAILABLE)에 걸렸습니다.")
            return False
            
        # 구매 가능 여부 판단
        is_available = "送出訂單" in page_source
        
        if is_available:
            send_alert(f"🚨 [홍콩 알림] 상품 구매 가능 상태 감지!\n주소: {TARGET_URL}")
            print("구매 문구 감지 성공 및 디스코드 알림 전송!")
            return True
        else:
            print("아직 구매 문구가 없습니다. (품절 상태)")
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
