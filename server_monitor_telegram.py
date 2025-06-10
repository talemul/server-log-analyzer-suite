
import os
import time
import requests
import psutil
from datetime import datetime

# === CONFIGURATION ===
TELEGRAM_BOT_TOKEN = '8149141738:AAECwyXV9sJAh5wQ7M4BoeehLIxVZsA-cFI'
TELEGRAM_CHAT_ID = '5801225850'
CHECK_INTERVAL_SECONDS = 60  # Check every minute

# Alert thresholds
CPU_THRESHOLD = 85.0  # in percent
MEMORY_THRESHOLD = 85.0  # in percent
DISK_THRESHOLD = 90.0  # in percent
SHOW_TOP_IF_ABOVE = 50.0  # show top processes if above this %

last_alert_time = {}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def should_alert(metric, interval=300):
    now = time.time()
    if metric not in last_alert_time or now - last_alert_time[metric] > interval:
        last_alert_time[metric] = now
        return True
    return False

def get_top_processes(sort_by='cpu', count=5):
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    key = 'cpu_percent' if sort_by == 'cpu' else 'memory_percent'
    sorted_procs = sorted(procs, key=lambda x: x.get(key, 0), reverse=True)
    return sorted_procs[:count]

def check_metrics():
    alerts = []

    # CPU Usage
    cpu = psutil.cpu_percent(interval=1)
    if cpu > CPU_THRESHOLD and should_alert('cpu'):
        alerts.append(f"🔥 *High CPU usage:* {cpu}%")

    # Memory Usage
    mem = psutil.virtual_memory().percent
    if mem > MEMORY_THRESHOLD and should_alert('memory'):
        alerts.append(f"💾 *High Memory usage:* {mem}%")

    # Disk Usage
    disk = psutil.disk_usage('/').percent
    if disk > DISK_THRESHOLD and should_alert('disk'):
        alerts.append(f"🗄️ *High Disk usage:* {disk}%")

    # Top culprits if CPU or MEM exceeds 50%
    details = ""
    if cpu > SHOW_TOP_IF_ABOVE or mem > SHOW_TOP_IF_ABOVE:
        top_cpu = get_top_processes('cpu')
        top_mem = get_top_processes('memory')
        details += "\n\n🧠 *Top 5 by Memory:*\n"
        for p in top_mem:
            details += f"- {p['name']} (PID: {p['pid']}) - {p['memory_percent']:.1f}%\n"
        details += "\n⚙️ *Top 5 by CPU:*\n"
        for p in top_cpu:
            details += f"- {p['name']} (PID: {p['pid']}) - {p['cpu_percent']:.1f}%\n"

    # Uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')

    # Send alerts
    if alerts:
        status_report = "\n".join(alerts)
        full_message = f"*🔔 Server Health Alert*\n{status_report}{details}\n\n🕒 Uptime since: {boot_time}"
        send_telegram(full_message)
    else:
        print(f"{datetime.now()} - OK")

if __name__ == "__main__":
    while True:
        check_metrics()
        time.sleep(CHECK_INTERVAL_SECONDS)
