from flask import Flask, render_template, request, redirect, jsonify
from utils import db
from datetime import datetime, timedelta
import dateutil.parser
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

whiteboard_lines = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/drop', methods=['GET', 'POST'])
def drop():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        country = request.form['country']
        
        poll_question = request.form.get('poll_question', '').strip()
        poll_options = []
        for i in range(1, 6):
            option = request.form.get(f'poll_option_{i}', '').strip()
            if option:
                poll_options.append(option)

        if len(content) < 30:
            return "Content must be at least 30 characters.", 400

        if any(word in content.lower() for word in ['fuck', 'shit', 'bitch']):
            return "Swearing not allowed.", 400

        if poll_question and len(poll_options) >= 2:
            db.post_confession(title, content, country, poll_question, poll_options)
        else:
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

@app.route('/post/<id>/live')
def live(id):
    confession = next((c for c in db.get_all_confessions() if c['id'] == id), None)
    if not confession:
        return 'Post not found', 404
    return render_template('live.html', confession=confession)

@app.route('/api/whiteboard/<post_id>', methods=['GET', 'POST'])
def api_whiteboard(post_id):
    if request.method == 'GET':
        lines = db.get_whiteboard_lines(post_id)
        return jsonify({'lines': lines})
    elif request.method == 'POST':
        data = request.get_json()
        x1 = data.get('x1')
        y1 = data.get('y1')
        x2 = data.get('x2')
        y2 = data.get('y2')
        color = data.get('color')
        line = db.add_whiteboard_line(post_id, x1, y1, x2, y2, color)
        return jsonify({'line': line})

@app.route('/api/livechat/<post_id>', methods=['GET', 'POST'])
def api_livechat(post_id):
    if request.method == 'GET':
        messages = db.get_livechat_messages(post_id)
        return jsonify({'messages': messages})
    elif request.method == 'POST':
        data = request.get_json()
        text = data.get('text')
        msg = db.add_livechat_message(post_id, text)
        return jsonify({'message': msg})

@app.route('/api/poll/<post_id>/vote', methods=['POST'])
def vote_poll_api(post_id):
    option_index = request.json.get("option_index")
    if option_index is None:
        return jsonify({"success": False, "error": "Option index required"}), 400
    
    try:
        poll = db.vote_poll(post_id, option_index)
        socketio.emit('poll_update', {'post_id': post_id, 'poll': poll}, room=post_id)
        return jsonify({"success": True, "poll": poll})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/poll/<post_id>', methods=['GET'])
def get_poll_api(post_id):
    poll = db.get_poll(post_id)
    if poll:
        return jsonify({"success": True, "poll": poll})
    return jsonify({"success": False, "error": "Poll not found"}), 404

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

@socketio.on('join')
def on_join(data):
    post_id = data['post_id']
    join_room(post_id)
    emit('init_lines', {'lines': whiteboard_lines.get(post_id, [])}, room=request.sid)
    emit('init_messages', {'messages': db.get_livechat_messages(post_id)}, room=request.sid)

@socketio.on('draw_line')
def on_draw_line(data):
    post_id = data['post_id']
    line = {
        'x1': data['x1'], 'y1': data['y1'], 'x2': data['x2'], 'y2': data['y2'], 'color': data['color']
    }
    whiteboard_lines.setdefault(post_id, []).append(line)
    emit('draw_line', line, room=post_id, include_self=False)

@socketio.on('chat_message')
def on_chat_message(data):
    post_id = data['post_id']
    color = data.get('color', '#00ff88')
    msg = db.add_livechat_message(post_id, data['text'], color)
    emit('chat_message', msg, room=post_id, include_self=False)

@socketio.on('poll_vote')
def on_poll_vote(data):
    post_id = data['post_id']
    option_index = data['option_index']
    try:
        poll = db.vote_poll(post_id, option_index)
        emit('poll_update', {'post_id': post_id, 'poll': poll}, room=post_id)
    except ValueError as e:
        emit('poll_error', {'error': str(e)}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)
