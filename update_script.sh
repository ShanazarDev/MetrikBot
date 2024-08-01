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

# Переход в директорию репозитория
cd /root/MetrikBot || { send_error_email "Ошибка: не удалось перейти в директорию репозитория"; exit 1; }

# Активация виртуального окружения
source venv/bin/activate

# Обновление репозитория
git pull origin repo || { send_error_email "Ошибка: не удалось обновить репозиторий"; deactivate; exit 1; }

# Получаем информацию о последнем коммите
LAST_COMMIT=$(git log -1 --pretty=format:'%H')
LAST_COMMIT_MESSAGE=$(git log -1 --pretty=format:'%s')

# Формируем JSON данные
DATA=$(printf '{"commit": "%s", "message": "%s"}' "$LAST_COMMIT" "$LAST_COMMIT_MESSAGE")

# Отправляем данные на сервер
curl -X POST -H "Content-Type: application/json" -d "$DATA" http://192.168.0.252:8045/version/


# Проверка успешности обновления
if [ $? -ne 0 ]; then
    send_error_email "Ошибка: не удалось обновить репозиторий"
    deactivate
    exit 1
fi

# Деактивация виртуального окружения
deactivate

send_error_email "Обновление успешно завершено"
echo "Обновление успешно завершено"
