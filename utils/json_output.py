# json_output.py

import json
import os
from datetime import datetime

def save(results):
    # Создание директории результатов, если не существует
    os.makedirs("results", exist_ok=True)

    # Уникальное имя файла с датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/result_{timestamp}.json"

    # Сохранение в файл
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"[JSON OUTPUT] Saved detailed results to {filename}")
