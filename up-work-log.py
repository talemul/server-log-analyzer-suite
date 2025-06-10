import os
import re
from datetime import datetime
import pandas as pd

# Folder containing all access log files
log_folder = r"apache2"  # ✅ Update this path if needed

# Pattern to match Apache combined log format
log_pattern = re.compile(
    r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<url>\S+) HTTP/[\d\.]+" '
    r'(?P<status>\d{3}) (?P<size>\d+) "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
)

# Target URL pattern to find
target_url_pattern = "/index.php/admin/customer_notification_action/"
results = []

# Read all matching log files
for filename in os.listdir(log_folder):
    if filename.startswith("access.log"):
        file_path = os.path.join(log_folder, filename)
        with open(file_path, "r", errors="ignore") as f:
            for line in f:
                match = log_pattern.search(line)
                if match:
                    data = match.groupdict()
                    if target_url_pattern in data["url"]:
                        try:
                            timestamp = datetime.strptime(data["timestamp"], "%d/%b/%Y:%H:%M:%S %z")
                        except Exception:
                            timestamp = data["timestamp"]
                        results.append({
                            "IP": data["ip"],
                            "Timestamp": timestamp,
                            "Method": data["method"],
                            "URL": data["url"],
                            "Status": data["status"],
                            "Size": data["size"],
                            "Referrer": data["referrer"],
                            "User-Agent": data["user_agent"]
                        })

# Convert to DataFrame
df = pd.DataFrame(results)

# ✅ Fix: Remove timezone info so Excel can handle the timestamp
df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.tz_localize(None)

# Save to Excel
df.to_excel("notification_hits_all_logs.xlsx", index=False)

print(f"✅ Exported {len(df)} entries to notification_hits_all_logs.xlsx")
