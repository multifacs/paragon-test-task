import argparse
import requests
import json
import os
import shortuuid
from colorama import Fore, Style, init

# Инициализация colorama
init(autoreset=True)


def fetch_tickets(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        return []


def process_tickets(tickets):
    open_tickets = [t for t in tickets if t["status"] == "open"]
    open_count = sum(1 for t in tickets if t["status"] == "open")

    by_category = {}
    for t in tickets:
        category = t["category"]
        by_category[category] = by_category.get(category, 0) + 1

    return {
        "open": {
            "tickets": open_tickets,
            "count": open_count
        },
        "by_category": by_category
    }


def print_report(report):
    print(f"\n{Fore.CYAN + Style.BRIGHT}📊 Отчёт по тикетам\n")
    print(f"{Fore.YELLOW}Открытые тикеты: {Fore.GREEN}{report['open']['count']}")
    
    for t in report['open']['tickets']:
        print(f"  {Fore.BLUE}- id: {Fore.GREEN}{str(t['id']).rjust(3)} {Fore.BLUE}  category: {Fore.GREEN}{t['category']}")
    
    print(f"\n{Fore.MAGENTA}Количество тикетов по категориям:")
    for category, count in report["by_category"].items():
        print(f"  {Fore.BLUE}- {category}: {Fore.GREEN}{count}")
    print("")
    
from datetime import datetime, timezone

def get_utc_timestamp():
    now_utc = datetime.now(timezone.utc)
    return now_utc.strftime('%y-%m-%d %H-%M-%S')

def save_report(report, log_path, use_uuid):
    os.makedirs(log_path, exist_ok=True)
    filename = ''
    if use_uuid:
        filename = f"{shortuuid.uuid()}.json"
    else:
        filename = f"{get_utc_timestamp()}.json"
        
    full_path = os.path.join(log_path, filename)
    with open(full_path, "w") as f:
        json.dump(report, f, indent=4)
    print(f"Отчёт сохранён в {full_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Process ticket data from API.")
    parser.add_argument("--api", help="URL для получения тикетов")
    parser.add_argument("--log", help="Путь для сохранения отчёта")
    parser.add_argument("--uuid", help="Использовать Short UUID вместо даты в именах файлов логов", action="store_true")
    args = parser.parse_args()

    tickets = fetch_tickets(args.api)
    report = process_tickets(tickets["tickets"])
    print_report(report)
    save_report(report, args.log, use_uuid=args.uuid)


if __name__ == "__main__":
    main()
