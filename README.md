# Paragon Тестовое задание

## Задание

У вас есть список тикетов, вам необходимо написать Python скрипт, который покажет, а также запишет в файл с автоматически сгенерированным уникальным именем:
1. Количество нерешённых тикетов и выдаст их список.
2. Количество тикетов по каждой категории.


Список тикетов:

```js
tickets = [
    {"id": 1, "category": "customer_service", "status": "open"},
    {"id": 2, "category": "technical", "status": "closed"},
    {"id": 3, "category": "customer_service", "status": "open"},
    {"id": 4, "category": "technical", "status": "open"},
    {"id": 5, "category": "customer_service", "status": "open"},
]
```

Вы написали скрипт tickets.py. Вам нужно настроить автоматический запуск этого скрипта на Linux каждые три часа.
Напишите команды которыми вы будете это делать.

## Выполнение

### Mock API

Mock API написано на NodeJS+Express и генерирует список рандомных тикетов по адресу http://localhost:3000/tickets

Запуск:

```bash
cd mock-api
docker build --tag ticket-api .
docker run -d -p 3000:3000 ticket-api
```

Исходный код:
https://github.com/multifacs/paragon-test-task/blob/master/mock-api/index.js

### tickets.py

Скрипт для запроса тикетов по API и формирования отчёта.

Запуск:

```bash
cd script
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

Использование:

```bash
python tickets.py --api http://localhost:3000/tickets --log /root/paragon-test-task/logs --uuid
```

Флаги:
1) --api: URL для получения тикетов
2) --log: Путь для сохранения отчёта
3) --uuid: Использовать Short UUID вместо даты в именах файлов логов

Формат имени лога: ГГ-ММ-ДД ЧЧ-ММ-СС либо Short UUID

Пример лога в принте:

```
📊 Отчёт по тикетам

Открытые тикеты: 6
  - id: 1  category: customer_service
  - id: 2  category: billing
  - id: 3  category: customer_service
  - id: 5  category: customer_service
  - id: 6  category: technical
  - id: 8  category: technical

Количество тикетов по категориям:
  - customer_service: 5
  - billing: 2
  - technical: 3
```

Пример лога в файле:

```json
{
    "open": {
        "tickets": [
            {
                "id": 1,
                "category": "customer_service",
                "status": "open"
            },
            {
                "id": 2,
                "category": "billing",
                "status": "open"
            },
            {
                "id": 3,
                "category": "customer_service",
                "status": "open"
            },
            {
                "id": 5,
                "category": "customer_service",
                "status": "open"
            },
            {
                "id": 6,
                "category": "technical",
                "status": "open"
            },
            {
                "id": 8,
                "category": "technical",
                "status": "open"
            }
        ],
        "count": 6
    },
    "by_category": {
        "customer_service": 5,
        "billing": 2,
        "technical": 3
    }
}
```

Исходный код:
https://github.com/multifacs/paragon-test-task/blob/master/script/tickets.py

### Автоматизация

Задача: запускать скрипт каждые 3 часа. Это можно реализовать несколькими способами.

1. Банально прописать в скрипте `while True` и `sleep(3 * 60 * 60)`
2. Создать демон в `systemd` и таймер к нему
3. Воспользоваться планировщиком `cron`

#### systemd

`/etc/systemd/system/tickets.service`
```ini
[Unit]
Description=Tickets Report Service
Wants=tickets.timer

[Service]
Type=oneshot
ExecStart=/root/paragon-test-task/script/env/bin/python /root/paragon-test-task/script/tickets.py
WorkingDirectory=/root/paragon-test-task/script
```

`/etc/systemd/system/tickets.timer`
```ini
[Unit]
Description=Run Tickets Report Service every 3 hours

[Timer]
# Вариант 1 - запуск на старте таймера через 10 сек + каждые 3 часа
OnBootSec=10s
OnUnitActiveSec=3h

# Вариант 2 - запуск каждые 3 часа начиная с 00:00
OnCalendar=0/3:00:00

AccuracySec=1m
Unit=tickets.service

[Install]
WantedBy=timers.target
```

Запуск:
```bash
systemctl daemon-reload
systemctl enable --now tickets.timer
```

#### cron

Добавление новых задач в `cron` делается через команду:

```
crontab -e
```

Запуск каждые 3 часа в 00 минут:
```
0 */3 * * * /root/paragon-test-task/script/env/bin/python /root/paragon-test-task/script/tickets.py
```