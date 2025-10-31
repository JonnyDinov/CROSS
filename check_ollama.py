#!/usr/bin/env python3
"""
Простая проверка Ollama без зависимостей от PyQt5
"""
import sys

try:
    import requests
except ImportError:
    print("❌ Модуль 'requests' не установлен")
    print("   Установите: pip install requests")
    sys.exit(1)


def check_ollama(url="http://localhost:11434"):
    print(f"🔍 Проверка Ollama на {url}")
    print("=" * 60)
    
    # Проверка доступности
    try:
        r = requests.get(f"{url}/", timeout=5)
        print(f"✅ Ollama доступна (статус: {r.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"❌ Ollama НЕ доступна!")
        print(f"\n📝 Что делать:")
        print(f"   1. Установите Ollama: https://ollama.ai")
        print(f"   2. Запустите: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    # Проверка моделей
    try:
        r = requests.get(f"{url}/api/tags", timeout=5)
        data = r.json()
        models = data.get("models", [])
        
        if models:
            print(f"✅ Найдено моделей: {len(models)}")
            for m in models:
                print(f"   • {m['name']}")
        else:
            print(f"⚠️  Модели не найдены!")
            print(f"\n📝 Загрузите модель:")
            print(f"   ollama pull llama2")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка получения моделей: {e}")
        return False
    
    # Тест генерации
    print(f"\n🧪 Тестовая генерация...")
    try:
        model = models[0]["name"]
        payload = {
            "model": model,
            "prompt": "Say hello",
            "stream": False
        }
        r = requests.post(f"{url}/api/generate", json=payload, timeout=30)
        data = r.json()
        
        if "response" in data:
            print(f"✅ Генерация работает!")
            print(f"   Ответ: {data['response'][:50]}...")
        else:
            print(f"⚠️  Неожиданный ответ: {data}")
            
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Всё готово! Можно запускать приложение:")
    print("   python main.py")
    return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:11434"
    success = check_ollama(url)
    sys.exit(0 if success else 1)
