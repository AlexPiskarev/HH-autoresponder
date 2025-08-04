# selenium_agent.py — альтернатива без API, с авторизацией через браузер и куками

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import time
import pickle
import os
from datetime import datetime
import config

HH_LOGIN = "alexpiskarev02@gmail.com"  # твоя почта от HH
RESUME_ID = "362722d3ff0f3803f80039ed1f6f4f37564456"  # ID резюме
MAX_APPLICATIONS_PER_RUN = 5
COOKIES_FILE = "hh_cookies.pkl"

options = Options()
options.add_argument("-headless")  # Можно отключить, если хочешь видеть браузер

driver = webdriver.Firefox(options=options)
driver.implicitly_wait(10)

def log(text):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now}] {text}")
    with open("applied.log", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {text}\n")

def login():
    driver.get("https://hh.ru/")

    # 1. Попытка загрузить куки
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                if "expiry" in cookie:
                    del cookie["expiry"]
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(3)
        if "account" in driver.page_source or "Выход" in driver.page_source:
            log("✅ Сессия восстановлена через куки.")
            return

    # 2. Логин вручную
    log("🔐 Не удалось загрузить сессию. Необходима авторизация.")
    driver.get("https://hh.ru/account/login")
    time.sleep(3)

    try:
        email_input = driver.find_element(By.NAME, "username")
        email_input.send_keys(HH_LOGIN)
        email_input.send_keys(Keys.ENTER)

        log("📨 Введи одноразовый код из почты вручную в браузере.")
        input("▶ Нажми Enter, когда код введён и ты авторизован...")

        with open(COOKIES_FILE, "wb") as f:
            pickle.dump(driver.get_cookies(), f)

        log("💾 Куки сохранены.")
    except Exception as e:
        log(f"⚠️ Не удалось найти форму логина: {e}")
        log("⏭ Пропускаем авторизацию, возможно, сессия уже активна.")

def search_and_apply():
    driver.get("https://hh.ru/search/vacancy?area=1&text=" + "+".join(config.KEYWORDS))
    time.sleep(3)

    vacancies = driver.find_elements(By.CSS_SELECTOR, "div.vacancy-serp-item")
    count = 0

    for vacancy in vacancies:
        title_el = vacancy.find_element(By.CSS_SELECTOR, "a.bloko-link")
        title = title_el.text.lower()

        if any(x.lower() in title for x in config.EXCLUDE_WORDS):
            continue
        if not all(x.lower() in title for x in config.KEYWORDS):
            continue

        try:
            title_el.click()
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)

            apply_btn = driver.find_element(By.CSS_SELECTOR, "button[data-qa='vacancy-response-button-top']")
            apply_btn.click()
            time.sleep(2)

            log(f"✔ Отклик на вакансию: {title_el.text}")
            count += 1
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            if count >= MAX_APPLICATIONS_PER_RUN:
                break
        except Exception as e:
            log(f"✖ Не удалось откликнуться: {title_el.text} — {str(e)}")
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

if __name__ == "__main__":
    login()
    search_and_apply()
    driver.quit()
