from flask import Flask, render_template, abort
from datetime import datetime
import sqlite3
import json

app = Flask(__name__)

def get_stories_for_date(date_str):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('SELECT stories FROM llmstories WHERE date = ?', (date_str,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    stories = get_stories_for_date(today)
    if stories is None:
        stories = []
    # Add comments_url to each story
    for story in stories:
        story['comments_url'] = f"https://news.ycombinator.com/item?id={story['id']}"
    return render_template('news.html', stories=stories, date=today)

@app.route('/<date>')
def show_date(date):
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        abort(404)
        
    stories = get_stories_for_date(date)
    if stories is None:
        abort(404)
    # Add comments_url to each story
    for story in stories:
        story['comments_url'] = f"https://news.ycombinator.com/item?id={story['id']}"
    return render_template('news.html', stories=stories, date=date)

if __name__ == '__main__':
    app.run(debug=True)
