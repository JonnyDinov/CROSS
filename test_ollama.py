#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к Ollama
Запустите: python test_ollama.py
"""

import requests
import sys


def test_ollama_connection(api_url: str = "http://localhost:11434"):
    print(f"Проверка подключения к Ollama: {api_url}")
    print("-" * 50)
    
    # Тест 1: Проверка доступности сервера
    print("1. Проверка доступности сервера...")
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        print(f"   ✓ Сервер доступен (статус: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"   ✗ ОШИБКА: Сервер недоступен!")
        print(f"   Решение: Запустите Ollama командой 'ollama serve'")
        return False
    except Exception as e:
        print(f"   ✗ ОШИБКА: {e}")
        return False
    
    # Тест 2: Получение списка моделей
    print("\n2. Получение списка моделей...")
    try:
        response = requests.get(f"{api_url}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        models = data.get("models", [])
        
        if models:
            print(f"   ✓ Найдено моделей: {len(models)}")
            for model in models:
                print(f"     - {model['name']}")
        else:
            print(f"   ⚠ Модели не найдены!")
            print(f"   Решение: Загрузите модель командой 'ollama pull llama2'")
            return False
    except Exception as e:
        print(f"   ✗ ОШИБКА: {e}")
        return False
    
    # Тест 3: Простая генерация текста
    print("\n3. Тестовая генерация текста...")
    try:
        model_name = models[0]["name"]
        print(f"   Используем модель: {model_name}")
        
        payload = {
            "model": model_name,
            "prompt": "Say hello in Russian",
            "stream": False
        }
        
        response = requests.post(
            f"{api_url}/api/generate",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if "response" in data:
            print(f"   ✓ Генерация работает!")
            print(f"   Ответ: {data['response'][:100]}...")
        else:
            print(f"   ⚠ Неожиданный формат ответа: {data}")
    except Exception as e:
        print(f"   ✗ ОШИБКА: {e}")
        return False
    
    # Тест 4: Chat API
    print("\n4. Тестовая генерация через Chat API...")
    try:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": "Say hello in Russian"}
            ],
            "stream": False
        }
        
        response = requests.post(
            f"{api_url}/api/chat",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if "message" in data and "content" in data["message"]:
            print(f"   ✓ Chat API работает!")
            print(f"   Ответ: {data['message']['content'][:100]}...")
        else:
            print(f"   ⚠ Неожиданный формат ответа: {data}")
    except Exception as e:
        print(f"   ✗ ОШИБКА Chat API: {e}")
        print(f"   (Возможно, ваша версия Ollama не поддерживает Chat API)")
        print(f"   (Приложение будет использовать generate API)")
    
    print("\n" + "=" * 50)
    print("✓ Тестирование завершено успешно!")
    print("Ollama готова к работе с приложением.")
    return True


if __name__ == "__main__":
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:11434"
    
    success = test_ollama_connection(api_url)
    sys.exit(0 if success else 1)
