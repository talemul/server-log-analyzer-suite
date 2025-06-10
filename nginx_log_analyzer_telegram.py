import re
import socket
import time
import requests
from collections import Counter
from datetime import datetime, timedelta

# === CONFIGURATION ===
ACCESS_LOG = 'shinjukuhalalfood.com-access.log'
ERROR_LOG = 'shinjukuhalalfood.com-error.log'
TELEGRAM_BOT_TOKEN = '8149141738:AAECwyXV9sJAh5wQ7M4BoeehLIxVZsA-cFI'
TELEGRAM_CHAT_ID = '5801225850'

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

def analyze_access_log(filepath):
    status_counter = Counter()
    method_counter = Counter()
    ip_counter = Counter()
    timestamps = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.split()
                if len(parts) > 8:
                    ip = parts[0]
                    method = parts[5].strip('"')
                    status = parts[8]
                    date_part = " ".join(parts[3:5]).strip("[]")
                    try:
                        log_time = datetime.strptime(date_part, '%d/%b/%Y:%H:%M:%S %z')
                        timestamps.append(log_time)
                    except:
                        pass
                    ip_counter[ip] += 1
                    method_counter[method] += 1
                    status_counter[status] += 1
    except Exception as e:
        return f"⚠️ *Access Log Error:* {e}", 0, 0

    total_hits = len(timestamps)
    duration = (max(timestamps) - min(timestamps)).total_seconds() / 60 if timestamps else 1
    avg_per_min = total_hits / duration if duration > 0 else total_hits

    summary = "📈 *Access Log Summary:*\n"
    summary += f"🔢 *Total Hits:* `{total_hits}`\n"
    summary += f"📊 *Avg Requests/min:* `{avg_per_min:.2f}`\n\n"
    summary += "✅ *Top Status Codes:*\n" + "\n".join([f"`{k}`: {v}" for k, v in status_counter.most_common(5)]) + "\n\n"
    summary += "⚙️ *Top Methods:*\n" + "\n".join([f"`{k}`: {v}" for k, v in method_counter.most_common(5)]) + "\n\n"
    summary += "🌍 *Top IPs:*\n" + "\n".join([f"`{k}`: {v}" for k, v in ip_counter.most_common(5)]) + "\n"
    return summary, total_hits, avg_per_min

def analyze_error_log(filepath):
    error_counter = Counter()
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'FastCGI sent in stderr' in line:
                    match = re.search(r'stderr: "([^"]+)"', line)
                    if match:
                        message = match.group(1)
                        if 'PHP message:' in message:
                            message = message.split('PHP message:')[-1].strip()
                        error_counter[message[:100]] += 1
                elif '[error]' in line:
                    msg = line.split(':', 1)[-1].strip()
                    error_counter[msg[:100]] += 1
    except Exception as e:
        return f"⚠️ *Error Log Error:* {e}"

    summary = "🚨 *Error Log Summary:*\n"
    for msg, count in error_counter.most_common(5):
        summary += f"❗ `{msg}` _({count}x)_\n"
    return summary

def generate_summary():
    access_summary, total_hits, avg_req = analyze_access_log(ACCESS_LOG)
    error_summary = analyze_error_log(ERROR_LOG)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hostname = socket.gethostname()

    final_message = f"🧾 *NGINX Log Summary* – `{timestamp}`\n🖥️ *Host:* `{hostname}`\n\n"
    final_message += f"{access_summary}\n{error_summary}"

    send_telegram(final_message)

if __name__ == "__main__":
    generate_summary()
