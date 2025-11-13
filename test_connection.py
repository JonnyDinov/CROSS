#!/usr/bin/env python
"""
Простой скрипт для проверки подключения к Ollama
"""

import requests
import sys

def test_ollama():
    print("=" * 50)
    print("Проверка подключения к Ollama")
    print("=" * 50)
    
    url = "http://127.0.0.1:11434"
    
    # Проверка доступности сервера
    print(f"\n1. Проверяем сервер: {url}")
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("   ✓ Сервер доступен")
        else:
            print(f"   ✗ Ошибка: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Сервер недоступен: {e}")
        print("\n   Убедитесь, что Ollama запущена:")
        print("   - Откройте Ollama приложение")
        print("   - Или запустите: ollama serve")
        return False
    
    # Получение списка моделей
    print("\n2. Получаем список моделей:")
    try:
        data = response.json()
        models = data.get("models", [])
        if not models:
            print("   ✗ Нет установленных моделей")
            print("\n   Установите модель:")
            print("   ollama pull gpt-oss:120b-cloud")
            return False
        
        print(f"   ✓ Найдено моделей: {len(models)}")
        for model in models:
            name = model.get("name", "Unknown")
            print(f"     - {name}")
        
        # Проверка нужной модели
        model_names = [m.get("name", "") for m in models]
        if "gpt-oss:120b-cloud" in model_names:
            print("\n   ✓ Модель gpt-oss:120b-cloud найдена!")
        else:
            print("\n   ⚠ Модель gpt-oss:120b-cloud не найдена")
            print("   Установите её: ollama pull gpt-oss:120b-cloud")
            
    except Exception as e:
        print(f"   ✗ Ошибка получения моделей: {e}")
        return False
    
    # Тестовый запрос
    print("\n3. Отправляем тестовый запрос...")
    try:
        test_payload = {
            "model": "gpt-oss:120b-cloud",
            "messages": [
                {"role": "user", "content": "Привет! Ответь одним словом: работаешь?"}
            ],
            "stream": False
        }
        
        response = requests.post(
            f"{url}/api/chat",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result.get("message", {}).get("content", "")
            print(f"   ✓ Ответ получен: {message}")
            print("\n" + "=" * 50)
            print("✅ ВСЁ РАБОТАЕТ! Можете запускать агента.")
            print("=" * 50)
            return True
        else:
            print(f"   ✗ Ошибка: HTTP {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ✗ Таймаут запроса (модель долго отвечает)")
        print("   Попробуйте ещё раз или увеличьте таймаут")
        return False
    except Exception as e:
        print(f"   ✗ Ошибка запроса: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    sys.exit(0 if success else 1)
