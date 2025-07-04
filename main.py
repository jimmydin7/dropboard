from flask import Flask, render_template, request, redirect, jsonify
from utils import db
from datetime import datetime, timedelta
import dateutil.parser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/drop', methods=['GET', 'POST'])
def drop():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        country = request.form['country']

        if len(content) < 30:
            return "Content must be at least 30 characters.", 400

        if any(word in content.lower() for word in ['fuck', 'shit', 'bitch']):  # Simple swear filter
            return "Swearing not allowed.", 400

        db.post_confession(title, content, country)
        return redirect('/success')
    return render_template('upload.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/browse')
def browse():
    confessions = db.get_all_confessions()
    return render_template('view.html', confessions=confessions)

@app.route('/api/upvote', methods=['POST'])
def upvote():
    confession_id = request.json.get("id")
    success = db.upvote_confession(confession_id)
    return jsonify({"success": success})

@app.route('/api/comment', methods=['POST'])
def comment():
    confession_id = request.json.get("id")
    content = request.json.get("comment")
    success = db.post_comment(confession_id, content)
    return jsonify({"success": success})

@app.template_filter('humantime')
def humantime_filter(iso_str):
    try:
        dt = dateutil.parser.isoparse(iso_str)
    except Exception:
        return iso_str
    now = datetime.utcnow()
    diff = now - dt.replace(tzinfo=None)
    if diff < timedelta(minutes=1):
        return 'just now'
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() // 60)
        return f'{mins} minute{"s" if mins != 1 else ""} ago'
    elif diff < timedelta(hours=24):
        hours = int(diff.total_seconds() // 3600)
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif diff < timedelta(days=2):
        return 'yesterday'
    else:
        days = diff.days
        return f'{days} days ago'

if __name__ == '__main__':
    app.run(debug=True)
