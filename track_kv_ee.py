import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import matplotlib.pyplot as plt

def get_objects_count():
    urls = [
        "https://www.kv.ee/en/apartments-for-sale",
        "http://webcache.googleusercontent.com/search?q=cache:https://www.kv.ee/en/apartments-for-sale"  # Google Cache
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            # Ищем "Objects found" в HTML
            match = re.search(r"Objects found (\d[\d\s]+)", response.text)
            if match:
                count_text = match.group(1).replace(" ", "")
                return int(count_text)

            # Ищем по классу
            soup = BeautifulSoup(response.text, "html.parser")
            span = soup.find("span", class_=re.compile(r"large|stronger"))
            if span:
                text = span.get_text(strip=True)
                match = re.search(r"Objects found (\d[\d\s]+)", text)
                if match:
                    count_text = match.group(1).replace(" ", "")
                    return int(count_text)

            # Ищем в тексте всех элементов
            for element in soup.find_all(string=re.compile(r"Objects found \d")):
                count_text = re.sub(r"\D", "", str(element))
                if count_text:
                    return int(count_text)

        except Exception as e:
            print(f"Ошибка при запросе {url}: {e}")
            continue

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
