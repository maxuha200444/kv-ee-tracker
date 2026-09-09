import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import matplotlib.pyplot as plt

def get_objects_count():
    url = "https://www.kv.ee/en/apartments-for-sale"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Пробуем найти "Objects found" напрямую в тексте
        match = re.search(r"Objects found (\d[\d\s]*)", response.text)
        if match:
            count_text = match.group(1).replace(" ", "").replace("&nbsp;", "")
            return int(count_text)

        # Если не нашли, парсим как HTML
        soup = BeautifulSoup(response.text, "html.parser")
        span = soup.find("span", class_="large stronger")
        if span:
            text = span.get_text(strip=True)
            if "Objects found" in text:
                count_text = text.replace("Objects found", "").strip().replace(" ", "")
                return int(count_text)

        return None
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        print(f"Ответ сервера: {response.text[:500]}")  # Выводим первые 500 символов для отладки
        return None

def save_data(count):
    data_file = "data.json"
    new_entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "count": count
    }

    data = []
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    existing_entry = next((entry for entry in data if entry["date"] == today), None)
    if not existing_entry:
        data.append(new_entry)
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Добавлена запись: {new_entry}")
    else:
        print(f"Запись за сегодня уже есть: {existing_entry}")

    return data

def plot_graph(data):
    if len(data) < 2:
        print("Недостаточно данных для графика.")
        return

    dates = [entry["date"] for entry in data]
    counts = [entry["count"] for entry in data]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, counts, marker="o", linestyle="-", color="b")
    plt.title("Количество объектов на kv.ee")
    plt.xlabel("Дата")
    plt.ylabel("Объекты")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("graph.png")
    plt.close()
    print("График сохранён.")

def main():
    print("Парсинг kv.ee...")
    count = get_objects_count()
    if count is None:
        print("Не удалось получить данные.")
        return
    print(f"Найдено объектов: {count}")
    data = save_data(count)
    plot_graph(data)

if __name__ == "__main__":
    main()
