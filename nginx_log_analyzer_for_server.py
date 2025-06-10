import re
import smtplib
import requests
import subprocess
from collections import Counter, defaultdict
from email.mime.text import MIMEText
from datetime import datetime

# === CONFIGURATION ===
LOG_FILE = 'shinjukuhalalfood.com-error.log'  # Your log file path
REDIS_ERROR_THRESHOLD = 100
EMAIL_ALERTS_ENABLED = False
TELEGRAM_ALERTS_ENABLED = True
AUTO_RESTART_REDIS = True

# Email Settings (if needed)
EMAIL_FROM = 'youremail@example.com'
EMAIL_TO = 'admin@example.com'
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USERNAME = 'youremail@example.com'
SMTP_PASSWORD = 'yourpassword'

# Telegram Settings
TELEGRAM_BOT_TOKEN = '8149141738:AAECwyXV9sJAh5wQ7M4BoeehLIxVZsA-cFI'
TELEGRAM_CHAT_ID = '5801225850'

# === REGEX PATTERNS ===
redis_error_pattern = re.compile(r'RedisException: (.*?) in')
fastcgi_pattern = re.compile(r'FastCGI sent in stderr')
php_fatal_pattern = re.compile(r'PHP Fatal')
shutdown_pattern = re.compile(r'shutdown_action_hook')

# === MAIN FUNCTION ===
def analyze_log():
    error_counts = Counter()
    redis_messages = defaultdict(int)

    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if '2025/' not in line:
                    continue
                timestamp = line.split()[0]
                try:
                    log_time = datetime.strptime(timestamp, '%Y/%m/%d')
                except:
                    continue

                if fastcgi_pattern.search(line):
                    error_counts['FastCGI'] += 1
                if redis_error_pattern.search(line):
                    error_counts['RedisException'] += 1
                    msg = redis_error_pattern.search(line).group(1).strip()
                    redis_messages[msg] += 1
                if shutdown_pattern.search(line):
                    error_counts['Shutdown Hook'] += 1
                if php_fatal_pattern.search(line):
                    error_counts['PHP Fatal'] += 1
    except Exception as e:
        print(f"❌ Failed to read log: {e}")
        return

    if error_counts['RedisException'] >= REDIS_ERROR_THRESHOLD:
        alert_message = f"[ALERT] High Redis error count: {error_counts['RedisException']}\nDetails:\n" + \
                        "\n".join([f"- {msg}: {count} times" for msg, count in redis_messages.items()])

        print(alert_message)  # Always print summary

        if EMAIL_ALERTS_ENABLED:
            send_email("Redis Error Alert", alert_message)
        if TELEGRAM_ALERTS_ENABLED:
            send_telegram(alert_message)
        if AUTO_RESTART_REDIS:
            restart_redis()

# === REDIS RESTART FUNCTION ===
def restart_redis():
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'redis'], check=True)
        print("✅ Redis restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to restart Redis: {e}")

# === EMAIL FUNCTION (OPTIONAL) ===
def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("✅ Email alert sent.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# === TELEGRAM FUNCTION ===
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram alert sent.")
        else:
            print("❌ Telegram send failed:", response.text)
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# === ENTRY POINT ===
if __name__ == '__main__':
    analyze_log()
