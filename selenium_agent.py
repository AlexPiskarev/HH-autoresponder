# selenium_agent.py — авторизация с паролем и обходом нового интерфейса

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import time
import pickle
import os
from datetime import datetime
import config

HH_LOGIN = "alexpiskarev02@gmail.com"
HH_PASSWORD = "29081989+"
RESUME_ID = "e13c4571ff0f38e6c40039ed1f484e694e366f"
MAX_APPLICATIONS_PER_RUN = 5
COOKIES_FILE = "hh_cookies.pkl"

options = Options()
# options.add_argument("-headless")  # Отключаем headless для ручного ввода

driver = webdriver.Firefox(options=options)
driver.implicitly_wait(10)

def log(text):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now}] {text}")
    with open("applied.log", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {text}\n")

def login():
    driver.get("https://hh.ru/")

    # Попытка загрузить cookies
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

    log("🔐 Не удалось загрузить сессию. Необходима авторизация.")

    # Авторизация вручную через интерфейс
    try:
        driver.get("https://hh.ru/")
        time.sleep(20)
        driver.find_element(By.XPATH, "//button[text()='Войти']").click()
        time.sleep(20)
        driver.find_element(By.XPATH, "//div[contains(text(), 'Я ищу работу')]").click()
        time.sleep(20)
        driver.find_element(By.XPATH, "//button[text()='Войти']").click()
        time.sleep(30)
        driver.find_element(By.XPATH, "//input[@type='email']").send_keys(HH_LOGIN)
        driver.find_element(By.XPATH, "//button[text()='Дальше']").click()
        time.sleep(30)
        driver.find_element(By.XPATH, "//button[contains(text(),'Войти с паролем')]").click()
        time.sleep(30)
        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        password_input.send_keys(HH_PASSWORD)
        password_input.send_keys(Keys.ENTER)
        time.sleep(40)

        with open(COOKIES_FILE, "wb") as f:
            pickle.dump(driver.get_cookies(), f)

        log("💾 Куки сохранены после авторизации.")
    except Exception as e:
        log(f"⚠️ Ошибка при логине: {e}")
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
