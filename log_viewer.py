from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# ✅ Change this to the actual path of your log file (drag the file into PyCharm to get the path)
LOG_FILE = 'redis-server.log'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Log Viewer</title>
    <style>
        body { font-family: monospace; background: #111; color: #0f0; padding: 20px; }
        input { width: 300px; padding: 5px; }
        .log-line { margin-bottom: 4px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h2>Viewing: {{ log_file }}</h2>
    <form method="get">
        <input type="text" name="q" placeholder="Search keyword..." value="{{ q }}">
        <button type="submit">Filter</button>
    </form>
    <hr>
    {% for line in lines %}
        <div class="log-line">{{ line }}</div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def view_log():
    q = request.args.get("q", "")
    if not os.path.exists(LOG_FILE):
        return f"<h3>Log file not found: {LOG_FILE}</h3>"

    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()[-500:]  # Show last 500 lines
        if q:
            lines = [line for line in lines if q.lower() in line.lower()]

    return render_template_string(HTML_TEMPLATE, lines=lines, q=q, log_file=LOG_FILE)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
