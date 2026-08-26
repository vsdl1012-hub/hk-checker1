import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

TARGET_URL = "여기에_대만_또는_홍콩_상품_상세_URL_입력" 
WEBHOOK_URL = "https://discord.com/api/webhooks/1541789079786487828/XvaI0Ol-R0z4Q4vp2E9U7SOX8ILXEvToXcnxYV1iSf-6-VdqHo2podEJP0VBXtg78f63"

def check_stock():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"홍콩 페이지 접속 중: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        time.sleep(12)
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(3)
        
        buttons = driver.find_elements(By.CLASS_NAME, "p-button--red")
        
        detected_keyword = None
        for btn in buttons:
            btn_text = btn.text.strip()
            print(f"발견된 버튼 텍스트: {btn_text}")
            
            # 영어 문구 혹은 중국어(번체) 문구가 포함되어 있는지 동시 체크
            if "PLACE PRE-ORDER" in btn_text.upper() or "送出訂單" in btn_text:
                detected_keyword = btn_text
                break

        if detected_keyword:
            message = (
                f"🇭🇰/🇹🇼 [홍콩 알림] 프리오더 버튼 활성화 감지!\n"
                f"🔍 **감지된 문구:** `{detected_keyword}`\n"
                f"🔗 **주소:** {TARGET_URL}"
            )
            send_alert(message)
            print(f"'{detected_keyword}' 감지 성공 및 디스코드 알림 전송!")
            return True
        else:
            print("아직 프리오더 버튼이 활성화되지 않았습니다.")
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
