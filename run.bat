@echo off
chcp 65001 > nul
title Windows AI Agent - Меню запуска

:menu
cls
echo ╔════════════════════════════════════════╗
echo ║     Windows AI Agent - Запуск         ║
echo ╚════════════════════════════════════════╝
echo.
echo Выберите режим запуска:
echo.
echo  [1] GUI (графический интерфейс)
echo  [2] CLI (командная строка)
echo  [3] Проверить Ollama
echo  [4] Установить зависимости
echo  [0] Выход
echo.
echo ═══════════════════════════════════════════
echo.

set /p choice=Введите номер: 

if "%choice%"=="1" goto gui
if "%choice%"=="2" goto cli
if "%choice%"=="3" goto test
if "%choice%"=="4" goto install
if "%choice%"=="0" goto end

echo Неверный выбор!
timeout /t 2 >nul
goto menu

:gui
cls
echo.
echo Запускаем GUI...
echo.
python agent\gui_app.py
pause
goto menu

:cli
cls
echo.
echo Запускаем CLI (интерактивный режим)...
echo.
python agent\cli_app.py interactive
pause
goto menu

:test
cls
echo.
echo Проверка подключения к Ollama...
echo.
python test_connection.py
echo.
pause
goto menu

:install
cls
echo.
echo Установка зависимостей...
echo.
pip install -r requirements.txt
echo.
echo Готово!
pause
goto menu

:end
echo.
echo До свидания!
timeout /t 1 >nul
exit
