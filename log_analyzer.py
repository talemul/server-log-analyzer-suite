import re
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt


# CONFIGURATION: Set your error log file path
LOG_FILE = 'shinjukuhalalfood.com-error.log'

# COMMON ERROR PATTERNS
error_keywords = ['PHP Fatal', 'RedisException', 'FastCGI', 'ID was called incorrectly', 'SIGTERM', 'shutdown']

def extract_timestamp(line):
    """Extract timestamp from line like '2025/05/31 00:00:34 ...'"""
    match = re.match(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2})", line)
    if match:
        return match.group(1)
    return None

def analyze_error_log(log_file):
    keyword_counter = Counter()
    message_counter = Counter()
    error_by_time = defaultdict(int)

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for keyword in error_keywords:
                if keyword in line:
                    message_counter[line.strip()] += 1
                    keyword_counter[keyword] += 1

                    timestamp = extract_timestamp(line)
                    if timestamp:
                        error_by_time[timestamp] += 1
                    break

    return keyword_counter, message_counter, error_by_time


# RUN ANALYSIS
keywords, messages, timeline = analyze_error_log(LOG_FILE)

# 🔢 Show Top Error Keywords
print("🔍 Top Error Types:")
for key, count in keywords.most_common():
    print(f"{key}: {count} times")

print("\n📌 Top Unique Error Messages:")
for msg, count in messages.most_common(5):
    print(f"\n[{count}x]\n{msg[:300]}...")

# 📈 Plot Errors Over Time
if timeline:
    sorted_times = sorted(timeline.items(), key=lambda x: datetime.strptime(x[0], "%Y/%m/%d %H:%M"))
    x = [t[0] for t in sorted_times]
    y = [t[1] for t in sorted_times]

    plt.figure(figsize=(12, 4))
    plt.plot(x, y, marker='o')
    plt.xticks(rotation=45)
    plt.title("Error Frequency Over Time")
    plt.xlabel("Time (HH:MM)")
    plt.ylabel("Errors")
    plt.tight_layout()
    plt.show()
