# Инструкция по установке Dinov AI Tools

## Требования

- **Python**: версия 3.7 или выше
- **Ollama**: локально установленная и запущенная
- **ОС**: Linux, macOS, Windows

## Шаг 1: Установка Python зависимостей

```bash
pip install -r requirements.txt
```

Или установка вручную:
```bash
pip install PyQt5>=5.15.9 requests>=2.31.0
```

## Шаг 2: Установка Ollama

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### macOS

```bash
brew install ollama
```

Или скачайте с официального сайта: https://ollama.ai

### Windows

Скачайте инсталлятор с https://ollama.ai и следуйте инструкциям.

## Шаг 3: Загрузка модели

После установки Ollama загрузите одну из моделей:

```bash
# Базовая модель (рекомендуется для начала)
ollama pull llama2

# Более качественная модель
ollama pull mistral

# Специализированная на диалогах
ollama pull neural-chat

# Для русского языка (если доступна)
ollama pull saiga
```

Проверьте список установленных моделей:
```bash
ollama list
```

## Шаг 4: Запуск Ollama

Ollama обычно запускается автоматически как служба. Если нет, запустите вручную:

```bash
ollama serve
```

Проверьте, что Ollama работает:
```bash
curl http://localhost:11434/api/tags
```

Должен вернуться JSON со списком моделей.

## Шаг 5: Запуск приложения

```bash
python main.py
```

Или сделайте файл исполняемым:

### Linux/macOS
```bash
chmod +x main.py
./main.py
```

### Windows
```bash
python main.py
```

## Проверка установки

После запуска приложения:

1. Откройте вкладку **Настройки**
2. Нажмите **Обновить список моделей**
3. Если модели появились - всё работает!
4. Если нет - проверьте, что Ollama запущена

## Создание ярлыка запуска

### Linux

Создайте файл `~/.local/share/applications/dinov-ai-tools.desktop`:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Dinov AI Tools
Comment=AI-powered RPG content generator
Exec=/usr/bin/python3 /path/to/dinov-ai-tools/main.py
Icon=/path/to/dinov-ai-tools/icon.png
Terminal=false
Categories=Utility;Development;
```

### Windows

Создайте ярлык с командой:
```
pythonw.exe "C:\path\to\dinov-ai-tools\main.py"
```

### macOS

Создайте скрипт `dinov-ai-tools.command`:
```bash
#!/bin/bash
cd "/path/to/dinov-ai-tools"
python3 main.py
```

Сделайте исполняемым:
```bash
chmod +x dinov-ai-tools.command
```

## Решение проблем

### Проблема: ModuleNotFoundError: No module named 'PyQt5'

**Решение:**
```bash
pip install PyQt5
```

### Проблема: Connection refused при подключении к Ollama

**Решение:**
1. Проверьте, запущена ли Ollama:
   ```bash
   ps aux | grep ollama
   ```
2. Запустите Ollama:
   ```bash
   ollama serve
   ```

### Проблема: Ollama возвращает "model not found"

**Решение:**
Загрузите модель:
```bash
ollama pull llama2
```

### Проблема: Приложение не запускается / чёрное окно

**Решение:**
Запустите из терминала, чтобы увидеть ошибки:
```bash
python main.py
```

### Проблема: База данных не создаётся

**Решение:**
Создайте директорию вручную:
```bash
mkdir -p data
```

## Обновление

Чтобы обновить приложение:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Удаление

Для полного удаления:

```bash
# Удалить приложение
rm -rf /path/to/dinov-ai-tools

# Удалить базу данных (если нужно)
# Внимание: это удалит все ваши данные!
rm -rf /path/to/dinov-ai-tools/data
```

## Производительность

### Рекомендуемые системные требования

- **ЦП**: 4+ ядра
- **ОЗУ**: 8+ ГБ (16 ГБ для больших моделей)
- **Место**: 5-20 ГБ (в зависимости от моделей)

### Оптимизация

Для ускорения генерации:
- Используйте GPU (если поддерживается Ollama)
- Выберите более легкую модель
- Уменьшите контекст диалогов в настройках

## Поддержка

Если возникли проблемы:
1. Проверьте раздел "Решение проблем" выше
2. Просмотрите логи Ollama
3. Создайте issue в репозитории проекта

## Дополнительно

### Настройка Ollama для GPU (NVIDIA)

Ollama автоматически использует GPU, если он доступен.

Проверьте использование GPU:
```bash
nvidia-smi
```

### Использование через Docker (экспериментально)

```bash
# Запуск Ollama в Docker
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Загрузка модели
docker exec -it ollama ollama pull llama2

# Запуск приложения
python main.py
```
