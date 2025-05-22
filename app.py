from flask import Flask, request, render_template_string
import sqlite3
import requests

app = Flask(__name__)

# Initialize a test SQLite DB
def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
    cur.execute("INSERT INTO users (name) VALUES ('Alice'), ('Bob')")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return '''
    <h1>Welcome</h1>
    <p><a href="/search?term=Bob">Search Users (XSS)</a></p>
    <p><a href="/fetch?url=http://localhost:5000/">Fetch URL (SSRF)</a></p>
    '''

# 1. SQL Injection from User-Agent header
@app.route('/log')
def log_user():
    user_agent = request.headers.get('User-Agent')
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    # VULN: SQL injection from headers
    cur.execute(f"INSERT INTO users (name) VALUES ('{user_agent}')")
    conn.commit()
    conn.close()
    return 'User-Agent logged!'

# 2. Reflected XSS from query parameter
@app.route('/search')
def search():
    term = request.args.get('term', '')
    # VULN: Reflected XSS
    html = f"<h2>Results for: {term}</h2>"
    return render_template_string(html)

# 3. SSRF vulnerability
@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    # VULN: SSRF without any validation
    r = requests.get(url)
    return f"<pre>{r.text}</pre>"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
