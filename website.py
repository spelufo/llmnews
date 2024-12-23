from flask import Flask, render_template, abort
from datetime import datetime, timedelta
import sqlite3
import json
from functools import wraps
from flask import request, Response
import os

app = Flask(__name__)

def check_auth(username, password):
  correct_username = os.environ.get('LLMNEWS_READER_USERNAME')
  correct_password = os.environ.get('LLMNEWS_READER_PASSWORD')
  return username == correct_username and password == correct_password

def authenticate():
  return Response(
    'Could not verify your credentials.\n'
    'Please authenticate.', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'}
  )

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
      return authenticate()
    return f(*args, **kwargs)
  return decorated

def get_stories_for_date(date_str):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('SELECT stories FROM llmstories WHERE date = ?', (date_str,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

def get_date_navigation(date_str):
  current_date = datetime.strptime(date_str, '%Y-%m-%d')
  prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
  next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
  
  # Don't show future dates
  today = datetime.now().date()
  if current_date.date() >= today:
    next_date = None
    
  return {
    'prev_date': prev_date,
    'next_date': next_date
  }

@app.route('/')
@requires_auth
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    stories = get_stories_for_date(today)
    if stories is None:
        stories = []
    nav = get_date_navigation(today)
    return render_template('news.html', stories=stories, date=today, **nav)

@app.route('/<date>')
@requires_auth
def show_date(date):
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        abort(404)
        
    stories = get_stories_for_date(date)
    if stories is None:
        abort(404)
    nav = get_date_navigation(date)
    return render_template('news.html', stories=stories, date=date, **nav)

if __name__ == '__main__':
    app.run(debug=True)
