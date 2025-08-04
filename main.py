# HH-autoresponder: main.py
# Агент для поиска вакансий и авто-отклика на HH.ru с логированием и ограничением откликов

import requests
import time
from datetime import datetime
import config

HEADERS = {
    "User-Agent": "HH-autoresponder",
    "Authorization": f"Bearer {config.HH_ACCESS_TOKEN}"
}

RESUME_ID = "362722d3ff0f3803f80039ed1f6f4f37564456"  # ID ИТ-резюме
MAX_APPLICATIONS_PER_RUN = 5  # Максимум откликов за один запуск цикла

# Шаг 1: поиск вакансий

def search_vacancies():
    response = requests.get(
        config.HH_API_URL + "vacancies",
        params={"text": " ".join(config.KEYWORDS), "area": 1, "per_page": 20},
        headers=HEADERS
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        print("[!] Ошибка при поиске:", response.text)
        return []

# Шаг 2: фильтрация вакансий

def is_suitable(vacancy):
    title = vacancy["name"].lower()
    return all(word.lower() in title for word in config.KEYWORDS) and not any(
        ex.lower() in title for ex in config.EXCLUDE_WORDS
    )

# Шаг 3: отклик на вакансию с логированием

def apply_to_vacancy(vacancy_id, vacancy_title):
    response = requests.post(
        f"{config.HH_API_URL}vacancies/{vacancy_id}/send",
        headers=HEADERS,
        data={
            "message": config.COVER_LETTER,
            "resume_id": RESUME_ID
        }
    )
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if response.status_code == 204:
        log_line = f"{now} | ✔ Отклик на вакансию: {vacancy_title} (ID: {vacancy_id})\n"
        print(log_line.strip())
    else:
        log_line = f"{now} | ✖ Ошибка отклика на {vacancy_title} (ID: {vacancy_id}) — {response.status_code}\n"
        print(log_line.strip())

    with open("applied.log", "a", encoding="utf-8") as f:
        f.write(log_line)

# Цикл работы

def run_agent():
    while True:
        vacancies = search_vacancies()
        applied_count = 0
        for v in vacancies:
            if applied_count >= MAX_APPLICATIONS_PER_RUN:
                break
            if is_suitable(v):
                apply_to_vacancy(v["id"], v["name"])
                applied_count += 1
        print(f"--- Ожидание 60 минут (откликов отправлено: {applied_count}) ---")
        time.sleep(3600)

if __name__ == "__main__":
    run_agent()
