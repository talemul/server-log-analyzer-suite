<<<<<<< HEAD

# 📊 Server Log Analyzer Suite

A collection of Python-based tools to analyze NGINX, Apache, MySQL slow query logs, and server health — with optional real-time alerts via Telegram or email.

---

## 🔧 Features

- **Apache & NGINX Access/Error Log Analyzers**
  - Detects bot hits, frequent errors, traffic patterns.
  - Exports detailed log data to Excel or sends summaries via Telegram.

- **MySQL Slow Query Analyzer**
  - Normalizes and aggregates long-running queries.
  - Generates CSV reports and identifies performance issues.

- **Redis/Shutdown Error Detection**
  - Detects Redis exceptions, shutdown hooks, PHP fatals.
  - Automatically restarts Redis or notifies admins.

- **Server Health Monitor**
  - Monitors CPU, memory, and disk usage.
  - Sends alert summaries and top processes via Telegram.

---

## 📁 Included Tools

| Script | Purpose |
|--------|---------|
| `log_analyzer.py` | Scan generic error logs for PHP, Redis, SIGTERM, etc. |
| `nginx_log_analyzer.py` | Detect NGINX errors and optionally alert via Telegram/email |
| `nginx_log_analyzer_for_server.py` | Same as above, with auto-restart support |
| `nginx_log_analyzer_telegram.py` | Sends traffic/error summaries via Telegram |
| `server_monitor_telegram.py` | Sends system resource usage alerts via Telegram |
| `slow_query_log_analyzer.py` | Scans MySQL slow queries and exports summary CSV |
| `up-work-log.py` | Extracts full hit logs for sensitive URL patterns (like email triggers) |

---

## 🚀 Getting Started

1. **Clone the repo**
```bash
git clone https://github.com/your-org/log-sentinel.git
cd log-sentinel
```

2. **Install dependencies**
```bash
pip install pandas openpyxl psutil matplotlib requests
```

3. **Update config**
- Open each script and update:
  - `LOG_FILE` paths
  - Telegram/Email credentials
  - Threshold values (CPU, error count, etc.)

4. **Run a tool**
```bash
python slow_query_log_analyzer.py
python server_monitor_telegram.py
```

---

## 📦 Outputs
- CSV files (`slow_queries.csv`, `mysql_errors.csv`)
- Excel sheets (`notification_hits_all_logs.xlsx`)
- Telegram or email alerts (optional)

---

## 🔐 Security Notes
Avoid committing `.log` files or bot tokens. Use `.env` or config templates for sensitive values.

---

## 👨‍💻 Author

**Talemul Islam**  
Email: talemulislam@gmail.com  
Software Architect | 11+ years in scalable CRM, HRM, and enterprise systems  
Expertise: Python, PHP, Laravel, DevOps, Log Analysis, System Monitoring  
GitHub: [github.com/talemul](https://github.com/talemul)

---

## 📜 License

MIT License
=======
# server-log-analyzer-suite
A Python toolkit for analyzing server logs, detecting performance bottlenecks, and sending alerts via Telegram and email.
>>>>>>> d45d3696dbaaacce913fe30c8aabc736de00dcf9
