#!/bin/bash

# Функция для отправки ошибки по почте
send_error_email() {
    local error_message=$1
    local ip_address=$(hostname -I | awk '{print $1}')
    
    # Активация виртуального окружения и запуск Python-скрипта
    source /root/MetrikBot/venv/bin/activate
    python /root/MetrikBot/send_error_email.py "$error_message" "$ip_address"
    deactivate
}

# Остановка cron службы
sudo service cron stop

# Проверка, что cron остановлен
if pgrep cron > /dev/null; then
    send_error_email "Ошибка: служба cron не остановлена"
    exit 1
fi

# Переход в директорию репозитория
cd /root/MetrikBot || { send_error_email "Ошибка: не удалось перейти в директорию репозитория"; exit 1; }

# Активация виртуального окружения
source venv/bin/activate

# Обновление репозитория
git pull origin repo || { send_error_email "Ошибка: не удалось обновить репозиторий"; deactivate; exit 1; }

# Проверка успешности обновления
if [ $? -ne 0 ]; then
    send_error_email "Ошибка: не удалось обновить репозиторий"
    deactivate
    exit 1
fi

# Деактивация виртуального окружения
deactivate

# Запуск cron службы
sudo service cron start

# Проверка, что cron запущен
if ! pgrep cron > /dev/null; then
    send_error_email "Ошибка: служба cron не запущена"
    exit 1
fi

send_error_email "Обновление успешно завершено"
echo "Обновление успешно завершено"
