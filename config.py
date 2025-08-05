# config.py

# ⚠️ Получи токен авторизации HH здесь: https://dev.hh.ru
HH_API_URL = "https://api.hh.ru/"
HH_ACCESS_TOKEN = "ваш_токен_сюда"

# Фильтры вакансий
KEYWORDS = [
    "операционный директор",
    "операционный менеджер",
    "COO",
    "operations manager",
    "бизнес-аналитик",
    "business analyst",
    "project manager",
    "IT project manager",
    "product operations",
    "ERP консультант",
    "автоматизация бизнес-процессов",
    "lead generation",
    "cold outreach",
    "SDR",
    "outbound-маркетинг",
    "LinkedIn маркетинг"
]
# Исключаем технические / нецелевые роли
EXCLUDE_WORDS = ["developer", "QA", "инженер", "DevOps"]

# Локация (по желанию)
LOCATION = "удаленно"

# Текст отклика
COVER_LETTER = """
Здравствуйте! Меня заинтересовала ваша вакансия. У меня сильный опыт в операционном управлении, автоматизации процессов и построении систем в цифровых бизнесах. Буду рад обсудить, чем могу быть полезен.
"""
