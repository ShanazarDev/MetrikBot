#!/bin/bash

# Проверка на наличие всех необходимых аргументов
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <username> <ip> <port> <password> <command>"
    exit 1
fi

# Присвоение переменных из аргументов
USERNAME=$1
IP=$2
PORT=$3
PASSWORD=$4
COMMAND=$5

# Выполнение удаленной команды через SSH с использованием sshpass
sshpass -p ${PASSWORD} ssh -o StrictHostKeyChecking=no ${USERNAME}@${IP} -p ${PORT} "${COMMAND}"

