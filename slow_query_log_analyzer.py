import re
import time
import pandas as pd
import os
import psutil

LOG_FILE = "slow-query.log"  # ✅ Replace with your slow query log file


def normalize_query(query):
    query = re.sub(r"\s+", " ", query.strip())
    query = re.sub(r"'[^']*'", "'?'", query)
    query = re.sub(r"\b\d+\b", "?", query)
    query = re.sub(r"IN\s*\([^)]*\)", "IN (?)", query, flags=re.I)
    return query


def analyze_large_mysql_log(log_path, slow_query_csv="slow_queries.csv", error_events_csv="mysql_errors.csv"):
    slow_query_pattern = re.compile(
        r"# Query_time: ([\d.]+)\s+Lock_time: ([\d.]+)\s+Rows_sent: (\d+)\s+Rows_examined: (\d+)",
        re.IGNORECASE
    )

    general_error_pattern = re.compile(
        r"(?:\d{6}\s+\d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z)?.*?(Error|Warning|Note): (.+)",
        re.IGNORECASE
    )

    special_event_keywords = [
        "Server shutdown", "Aborted connection", "Restarting", "Starting MySQL",
        "Out of memory", "InnoDB", "Unable to lock", "Table is marked as crashed",
        "Disk is full", "Lost connection", "Crash Recovery", "Can’t open"
    ]

    slow_queries = {}
    error_events = []

    current_stats = None
    collecting_query = False
    query_lines = []
    line_count = 0

    print("📥 Starting to scan the log file...")

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_count += 1

            if line_count % 100000 == 0:
                print(f"🔍 Processed {line_count:,} lines...")
            if line_count % 500_000 == 0:
                mem = psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)
                print(f"📦 Memory usage: {mem:.2f} MB")

            if line.startswith("# Query_time:"):
                match = slow_query_pattern.search(line)
                if match:
                    current_stats = {
                        "query_time": float(match.group(1)),
                        "lock_time": float(match.group(2)),
                        "rows_sent": int(match.group(3)),
                        "rows_examined": int(match.group(4)),
                    }
                collecting_query = False
                query_lines = []

            elif re.match(r"^\s*(SELECT|UPDATE|INSERT|DELETE)", line, re.IGNORECASE):
                if current_stats:
                    collecting_query = True
                    query_lines = [line.strip()]

            elif collecting_query:
                query_lines.append(line.strip())
                if ";" in line:
                    full_query = " ".join(query_lines)
                    norm_query = normalize_query(full_query)
                    if norm_query not in slow_queries:
                        slow_queries[norm_query] = {
                            "count": 0,
                            "total_query_time": 0.0,
                            "total_lock_time": 0.0,
                            "total_rows_sent": 0,
                            "total_rows_examined": 0,
                        }
                    q = slow_queries[norm_query]
                    q["count"] += 1
                    q["total_query_time"] += current_stats["query_time"]
                    q["total_lock_time"] += current_stats["lock_time"]
                    q["total_rows_sent"] += current_stats["rows_sent"]
                    q["total_rows_examined"] += current_stats["rows_examined"]
                    collecting_query = False
                    current_stats = None
                    query_lines = []

            elif any(keyword.lower() in line.lower() for keyword in special_event_keywords):
                error_events.append({
                    "timestamp_or_type": "Detected Event",
                    "line": line.strip()
                })

            elif "error" in line.lower() or "warning" in line.lower():
                ematch = general_error_pattern.search(line)
                if ematch:
                    error_events.append({
                        "timestamp_or_type": ematch.group(1),
                        "line": ematch.group(2).strip()
                    })

            if line_count % 1_000_000 == 0:
                checkpoint_path = f"checkpoint_{line_count}.csv"
                pd.DataFrame.from_dict(slow_queries, orient='index').to_csv(checkpoint_path)
                print(f"💾 Checkpoint saved: {checkpoint_path}")
            if line_count % 1_800_000 == 0:
                print(f"💾 break after : {line_count}")
                break

    print(f"✅ Completed log scan. Total lines read: {line_count:,}")
    print("🧮 Saving summary and error reports...")

    # Final output only if slow queries found
    if slow_queries:
        data = []
        for query, stats in slow_queries.items():
            count = stats["count"]
            data.append({
                "query": query,
                "count": count,
                "total_query_time": round(stats["total_query_time"], 3),
                "avg_query_time": round(stats["total_query_time"] / count, 3),
                "avg_lock_time": round(stats["total_lock_time"] / count, 3),
                "avg_rows_sent": round(stats["total_rows_sent"] / count, 2),
                "avg_rows_examined": round(stats["total_rows_examined"] / count, 2)
            })

        df = pd.DataFrame(data).sort_values(by="count", ascending=False)
        df.to_csv(slow_query_csv, index=False)
        print(f"✅ Saved slow query summary to: {slow_query_csv}")
    else:
        print("⚠️ No slow queries found. Skipping slow query CSV generation.")

    if error_events:
        err_df = pd.DataFrame(error_events)
        err_df.to_csv(error_events_csv, index=False)
        print(f"✅ Saved error events to: {error_events_csv}")
    else:
        print("✅ No error events found in log.")

    return line_count, slow_queries


if __name__ == "__main__":
    print("🚀 Starting analysis...")
    start_time = time.time()
    lines_read = 0

    try:
        lines_read, slow_queries = analyze_large_mysql_log(
            log_path=LOG_FILE,
            slow_query_csv="slow_queries.csv",
            error_events_csv="mysql_errors.csv"
        )
    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user. Saving partial results...")
        if 'slow_queries' in locals() and slow_queries:
            pd.DataFrame.from_dict(slow_queries, orient='index').to_csv("partial_slow_queries.csv")
            print("💾 Partial results saved to: partial_slow_queries.csv")
    except Exception as e:
        print(f"❌ ERROR during analysis: {e}")
    finally:
        end_time = time.time()
        mins, secs = divmod(end_time - start_time, 60)
        print(f"\n⏱️ Analysis complete in {int(mins)} min {secs:.2f} sec for {lines_read:,} lines.")
        with open("process_report.log", "a") as log_file:
            log_file.write(f"{time.ctime()}: Completed in {int(mins)}m {secs:.2f}s for file: {LOG_FILE}\n")
