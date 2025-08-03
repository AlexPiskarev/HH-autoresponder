# HH-autoresponder: main.py
# Агент для поиска вакансий и авто-отклика на HH.ru

import requests
import time
import config

HEADERS = {
    "User-Agent": "HH-autoresponder",
    "Authorization": f"Bearer {config.HH_ACCESS_TOKEN}"
}

RESUME_ID = "1b343d9cff0f20138a0039ed1f6f676a4a5943"  # ID ИТ-резюме

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

# Шаг 3: отклик на вакансию

def apply_to_vacancy(vacancy_id):
    response = requests.post(
        f"{config.HH_API_URL}vacancies/{vacancy_id}/send",
        headers=HEADERS,
        data={
            "message": config.COVER_LETTER,
            "resume_id": RESUME_ID
        }
    )
    if response.status_code == 204:
        print(f"[✔] Отклик на вакансию {vacancy_id} отправлен")
    else:
        print(f"[!] Ошибка отклика: {response.status_code}")

# Цикл работы

def run_agent():
    while True:
        vacancies = search_vacancies()
        for v in vacancies:
            if is_suitable(v):
                apply_to_vacancy(v["id"])
        print("--- Ожидание 10 минут ---")
        time.sleep(600)

if __name__ == "__main__":
    run_agent()
