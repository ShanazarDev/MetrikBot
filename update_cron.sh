#!/bin/bash

crontab -l > mycron

sed -i '\|/root/MetrikBot/run_script.sh|d' mycron

echo '*/3 * * * * /root/MetrikBot/run_script.sh' >> mycron

crontab mycron

rm mycron

service cron restart

send_error_email() {
    local message=$1
    local ip_address=$(hostname -I | awk '{print $1}')
    
    source /root/MetrikBot/venv/bin/activate
    python /root/MetrikBot/send_error_email.py "$message" "$ip_address"
    deactivate
}

message="Crontab успешно обновлен и cron сервис перезапущен."

send_error_email "$message"
