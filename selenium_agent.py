# selenium_agent.py — авторизация с паролем и обходом нового интерфейса

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os
from datetime import datetime
import config

HH_LOGIN = "alexpiskarev02@gmail.com"
HH_PASSWORD = "29081989+"
RESUME_ID = "e13c4571ff0f38e6c40039ed1f484e694e366f"
MAX_APPLICATIONS_PER_RUN = 15
COOKIES_FILE = "hh_cookies.pkl"

options = Options()
# options.add_argument("--headless")  # Отключаем headless для ручного ввода
options.add_experimental_option("detach", True)  # не закрывать окно после завершения

# путь до драйвера Chrome, если не прописан в PATH
# driver = webdriver.Chrome(executable_path="/path/to/chromedriver", options=options)
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

def log(text):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now}] {text}")
    with open("applied.log", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {text}\n")

def login():
    driver.get("https://hh.ru/")

    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                if "expiry" in cookie:
                    del cookie["expiry"]
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    log(f"⚠️ Не удалось добавить куки: {e}")
        driver.refresh()
        time.sleep(5)
        if "Выход" in driver.page_source:
            log("✅ Сессия восстановлена через куки.")
            return

    log("🔐 Не удалось загрузить сессию. Необходима авторизация.")

    try:
        driver.get("https://hh.ru/account/login")
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='email']"))).send_keys(HH_LOGIN)
        driver.find_element(By.XPATH, "//button[text()='Дальше']").click()
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Войти с паролем')]"))).click()
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password']"))).send_keys(HH_PASSWORD + Keys.ENTER)

        # Ожидание авторизации (появления кнопки "Выход")
        WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/logout')]"))
        )

        with open(COOKIES_FILE, "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        log("💾 Куки сохранены после авторизации.")
    except Exception as e:
        log(f"⚠️ Ошибка при логине: {e}")
        log("⏭ Пропускаем авторизацию, возможно, сессия уже активна.")

def search_and_apply():
    log("🔎 Начинаем поиск и отклик на вакансии...")
    count = 0

    for keyword in config.KEYWORDS:
        page = 0
        while True:
            search_url = f"https://hh.ru/search/vacancy?text={keyword}&search_period=1&schedule=remote&area=&page={page}"
            try:
                driver.get(search_url)
            except Exception as e:
                log(f"❌ Ошибка перехода по адресу: {search_url} — {e}")
                break

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-qa='serp-item']"))
                )
            except:
                if page == 0:
                    log(f"❌ Вакансии не найдены по запросу: {keyword}")
                break

            vacancies = driver.find_elements(By.CSS_SELECTOR, "div[data-qa='serp-item']")
            if not vacancies:
                break

            for vacancy in vacancies:
                try:
                    title_el = vacancy.find_element(By.CSS_SELECTOR, "a.bloko-link")
                    title = title_el.text.lower()

                    if any(x.lower() in title for x in config.EXCLUDE_WORDS):
                        continue

                    driver.execute_script("arguments[0].scrollIntoView(true);", title_el)
                    title_el.click()
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(5)

                    apply_btn = driver.find_element(By.CSS_SELECTOR, "button[data-qa='vacancy-response-button-top']")
                    apply_btn.click()
                    time.sleep(3)

                    log(f"✔ Отклик на вакансию: {title_el.text}")
                    count += 1
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    if count >= MAX_APPLICATIONS_PER_RUN:
                        return

                except Exception as e:
                    log(f"✖ Не удалось откликнуться: {title_el.text if 'title_el' in locals() else '[no title]'} — {str(e)}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

            page += 1

if __name__ == "__main__":
    login()
    search_and_apply()
    driver.quit()
