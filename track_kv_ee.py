from apify import ApifyClient
import json
import os
import re
from datetime import datetime
import matplotlib.pyplot as plt

def get_objects_count():
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        print("Apify API токен не найден!")
        return None

    try:
        # Создаём клиент Apify
        client = ApifyClient(api_token)

        # Запускаем актор для скрапинга страницы
        run_input = {
            "startUrls": [{"url": "https://www.kv.ee/en/apartments-for-sale"}],
            "resultsType": "text",  # Получаем HTML страницы
            "maxDepth": 0,  # Только стартовая страница
        }

        # Запускаем синхронный актор (web-scraper)
        run = client.actor("apify/web-scraper").call(run_input=run_input)

        # Получаем результаты
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

        if not dataset_items:
            print("Нет данных от Apify.")
            return None

        # Берём первый результат (HTML страницы)
        html = dataset_items[0]["html"]
        if not html:
            print("HTML не получен.")
            return None

        # Ищем "Objects found" в HTML
        match = re.search(r"Objects found (\d[\d\s]+)", html)
        if match:
            count_text = match.group(1).replace(" ", "")
            return int(count_text)

        # Ищем по классу
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
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

        return None
    except Exception as e:
        print(f"Ошибка Apify: {e}")
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
    print("Парсинг kv.ee через Apify...")
    count = get_objects_count()
    if count is None:
        print("Не удалось получить данные.")
        return
    print(f"Найдено объектов: {count}")
    data = save_data(count)
    plot_graph(data)

if __name__ == "__main__":
    main()
