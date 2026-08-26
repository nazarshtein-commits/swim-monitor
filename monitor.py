import os
import requests

# Налаштування діапазону посилань
START_ID = 2995
END_ID = 3200

# Автоматичне створення списку
SITES_TO_CHECK = [
    f"https://swimtime.in.ua/meet/{i}/" for i in range(START_ID, END_ID + 1)
]

# Telegram settings from secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SUCCESS_FILE = "online_sites.txt"

# Ключова фраза для підтвердження наявності програми
KEYWORD = "ПРОГРАМА ЗМАГАНЬ"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[TG Alert]: {message}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"Помилка Telegram: {e}")

def load_working_sites():
    if os.path.exists(SUCCESS_FILE):
        with open(SUCCESS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def mark_site_as_working(url):
    with open(SUCCESS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")

def check_websites():
    already_working = load_working_sites()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for url in SITES_TO_CHECK:
        if url in already_working:
            continue

        try:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                # Шукаємо ключову фразу без урахування регістру (великі/малі літери)
                page_text = response.text.upper()
                
                if KEYWORD in page_text:
                    msg = f"🎉 Знайдено програму змагань!\nURL: {url}\nЗнайдено фразу: \"{KEYWORD}\""
                    print(msg)
                    send_telegram(msg)
                    mark_site_as_working(url)
                else:
                    print(f"[{url}] Сторінка відкривається, але 'ПРОГРАМА ЗМАГАНЬ' ще відсутня")
            else:
                print(f"[{url}] Код: {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"[{url}] Недоступний")

if __name__ == "__main__":
    check_websites()
