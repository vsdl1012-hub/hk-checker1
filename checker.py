import time
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


TARGET_URL = "https://p-bandai.com/hk/item/A2866726001"
WEBHOOK_URL = "https://discord.com/api/webhooks/1541789079786487828/XvaI0Ol-R0z4Q4vp2E9U7SOX8ILXEvToXcnxYV1iSf-6-VdqHo2podEJP0VBXtg78f63"

CHECK_INTERVAL = 60
# GitHub Actions가 강제 종료되기 전에 정상 종료
RUN_TIME = 340 * 60

def create_driver():
    options = Options()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )
    options.add_experimental_option(
        "useAutomationExtension",
        False
    )
    options.add_argument(
        "user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    driver.execute_script(
        "Object.defineProperty("
        "navigator, 'webdriver', "
        "{get: () => undefined})"
    )
    return driver

def check_stock():

    driver = None
    try:
        print("=" * 60)
        print(f"홍콩 페이지 접속: {TARGET_URL}")

        driver = create_driver()
        driver.get(TARGET_URL)

        time.sleep(12)

        driver.execute_script(
            "window.scrollTo(0, 500);"
        )

        time.sleep(3)

        buttons = driver.find_elements(
            By.CLASS_NAME,
            "p-button--red"
        )

        print(f"발견된 버튼: {len(buttons)}개")

        for btn in buttons:

            text = btn.text.strip()

            print(f"버튼 텍스트: [{text}]")

            if (
                "PLACE PRE-ORDER" in text.upper()
                or "送出訂單" in text
            ):
                print(
                    f"🟢 구매 가능 버튼 발견: {text}"
                )

                return True, text

        print("🔴 현재 품절")

        return False, None

    except Exception as e:

        print(f"⚠️ 확인 오류: {e}")

        # 오류는 품절로 처리하지 않음
        return None, None
    finally:

        if driver:
            driver.quit()

def send_alert(button_text):

    message = (
        "🚨🇭🇰 **P-Bandai 홍콩 재입고 감지!**\n\n"
        f"🔍 감지된 버튼: `{button_text}`\n"
        f"🔗 **상품 페이지:** {TARGET_URL}"
    )

    try:

        response = requests.post(
            WEBHOOK_URL,
            json={
                "content": message
            },
            timeout=10
        )

        if response.status_code in (200, 204):

            print("✅ Discord 알림 전송 성공")

        else:

            print(
                f"❌ Discord 알림 실패: "
                f"{response.status_code}"
            )

    except Exception as e:

        print(
            f"❌ Discord 전송 오류: {e}"
        )


def main():

    start_time = time.time()

    # 이전 재고 상태
    was_available = False

    print("=" * 60)
    print("🇭🇰 P-Bandai 1분 재고 감시 시작")
    print("⏱ 확인 주기: 60초")
    print("⏳ 약 340분 후 자동 종료")
    print("=" * 60)

    while True:

        # 340분이 지나면 정상 종료
        elapsed = time.time() - start_time

        if elapsed >= RUN_TIME:

            print("=" * 60)
            print("⏰ 340분 감시 완료")
            print("🔄 다음 GitHub Actions 실행을 기다립니다.")
            print("=" * 60)

            break

        available, button_text = check_stock()

        # 사이트 오류
        if available is None:

            print(
                "⚠️ 오류 발생 → "
                "이번 체크에서는 상태 변경 없음"
            )

        # 구매 가능
        elif available:

            if not was_available:

                print("🚨🚨 재입고 최초 감지!")

                send_alert(button_text)

            else:

                print(
                    "🟢 계속 구매 가능 "
                    "→ 중복 알림 없음"
                )

            was_available = True

        # 품절
        else:

            if was_available:

                print("🔴 다시 품절됨")

            else:

                print("🔴 품절 상태")

            was_available = False

        print(
            "⏳ 60초 후 다시 확인합니다..."
        )

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
