import firebase_admin
from firebase_admin import credentials
import firebase_admin.db as fb_db
from datetime import datetime
import uuid
import random

class FirebaseConfessionDB:
    def __init__(self, database_url: str, cred_path="service.json"):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                "databaseURL": database_url
            })
        self.ref = fb_db.reference("confessions")

    def seed_db(self, db_json_path="db.json"):
        import json
        with open(db_json_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        
        self.ref.delete()
        
        demo_polls = [
            {
                "question": "What should I do about my crush?",
                "options": [
                    {"text": "Tell them how you feel", "votes": 0},
                    {"text": "Stay friends for now", "votes": 0},
                    {"text": "Ask friends for advice", "votes": 0},
                    {"text": "Focus on yourself first", "votes": 0}
                ]
            },
            {
                "question": "Which outfit should I wear to prom?",
                "options": [
                    {"text": "The classic black dress", "votes": 0},
                    {"text": "Something colorful and fun", "votes": 0},
                    {"text": "Go with a suit instead", "votes": 0}
                ]
            },
            {
                "question": "Should I tell my parents about my grades?",
                "options": [
                    {"text": "Be honest, they'll understand", "votes": 0},
                    {"text": "Wait until you can improve them", "votes": 0},
                    {"text": "Ask for help with studying", "votes": 0},
                    {"text": "Make a plan to do better", "votes": 0}
                ]
            },
            {
                "question": "What's the best way to handle this situation?",
                "options": [
                    {"text": "Talk it out calmly", "votes": 0},
                    {"text": "Take some time to think", "votes": 0},
                    {"text": "Ask for advice from someone you trust", "votes": 0}
                ]
            },
            {
                "question": "Should I try out for the team?",
                "options": [
                    {"text": "Go for it! You have nothing to lose", "votes": 0},
                    {"text": "Practice more first", "votes": 0},
                    {"text": "Maybe next year", "votes": 0}
                ]
            }
        ]
        
        for i, entry in enumerate(entries):
            post_id = str(entry["id"])
            confession = {
                "id": post_id,
                "title": entry["title"],
                "content": entry["content"],
                "country": entry.get("country", "Anonymous"),
                "upvote_count": random.randint(1, 5),
                "created_at": entry["created_at"],
                "comments": []
            }
            
            if i < len(demo_polls):
                confession["poll"] = demo_polls[i]
            
            self.ref.child(post_id).set(confession)
        
        print(f"Database reset and seeded with {len(entries)} demo posts (with polls and random upvotes 1-5)")

    def post_confession(self, title: str, content: str, country: str, poll_question=None, poll_options=None):
        if len(content) < 30:
            raise ValueError("Content too short.")
        if any(bad in content.lower() for bad in ["nigga", "nigger"]):
            raise ValueError("Inappropriate content.")

        post_id = str(uuid.uuid4())
        confession = {
            "id": post_id,
            "title": title,
            "content": content,
            "country": country,
            "upvote_count": 0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "comments": []
        }
        
        if poll_question and poll_options:
            confession["poll"] = {
                "question": poll_question,
                "options": [{"text": option, "votes": 0} for option in poll_options]
            }
        
        self.ref.child(post_id).set(confession)
        return post_id

    def get_all_confessions(self):
        confessions = self.ref.get()
        if not confessions:
            return []

        if isinstance(confessions, list):
            valid_confessions = [c for c in confessions if c and c.get("created_at")]
            return sorted(valid_confessions, key=lambda x: x["created_at"], reverse=True)
        else:
            valid_confessions = [c for c in confessions.values() if c and c.get("created_at")]
            return sorted(valid_confessions, key=lambda x: x["created_at"], reverse=True)

    def upvote(self, post_id: str):
        post_ref = self.ref.child(post_id)
        current = post_ref.get()
        if current:
            current["upvote_count"] = current.get("upvote_count", 0) + 1
            post_ref.update({"upvote_count": current["upvote_count"]})
            return current["upvote_count"]
        else:
            raise ValueError("Post not found.")

    def post_comment(self, post_id: str, content: str):
        if len(content.strip()) == 0:
            raise ValueError("Empty comment.")
        comment = {
            "content": content.strip(),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        comments_ref = self.ref.child(post_id).child("comments")
        comments = comments_ref.get() or []
        comments.append(comment)
        comments_ref.set(comments)
        return comment

    def get_whiteboard_lines(self, post_id):
        ref = fb_db.reference(f'whiteboard/{post_id}/lines')
        lines = ref.get()
        if not lines:
            return []
        return list(lines.values())

    def add_whiteboard_line(self, post_id, x1, y1, x2, y2, color):
        ref = fb_db.reference(f'whiteboard/{post_id}/lines')
        line = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'color': color, 'time': datetime.utcnow().isoformat() + 'Z'}
        ref.push(line)
        return line

    def get_livechat_messages(self, post_id):
        ref = fb_db.reference(f'livechat/{post_id}/messages')
        messages = ref.get()
        if not messages:
            return []
        return list(messages.values())

    def add_livechat_message(self, post_id, text, color):
        ref = fb_db.reference(f'livechat/{post_id}/messages')
        msg = {'text': text, 'color': color, 'time': datetime.utcnow().isoformat() + 'Z'}
        ref.push(msg)
        return msg

    def vote_poll(self, post_id: str, option_index: int):
        post_ref = self.ref.child(post_id)
        current = post_ref.get()
        if current and "poll" in current:
            if 0 <= option_index < len(current["poll"]["options"]):
                current["poll"]["options"][option_index]["votes"] += 1
                post_ref.update({"poll": current["poll"]})
                return current["poll"]
        raise ValueError("Invalid poll or option.")

    def get_poll(self, post_id: str):
        post = self.ref.child(post_id).get()
        return post.get("poll") if post else None

def load_config(path='config.txt'):
    config = {}
    with open(path, 'r') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                config[k] = v
    return config

config = load_config()
database_url = config.get('FIREBASE_URL')
cred_path = config.get('FIREBASE_CRED_PATH', 'service.json')
db = FirebaseConfessionDB(database_url, cred_path)

def upvote_confession(post_id):
    return db.upvote(post_id)

def post_confession(title, content, country, poll_question=None, poll_options=None):
    return db.post_confession(title, content, country, poll_question, poll_options)

def get_all_confessions():
    return db.get_all_confessions()

def post_comment(post_id, content):
    return db.post_comment(post_id, content)

def get_whiteboard_lines(post_id):
    return db.get_whiteboard_lines(post_id)

def add_whiteboard_line(post_id, x1, y1, x2, y2, color):
    return db.add_whiteboard_line(post_id, x1, y1, x2, y2, color)

def get_livechat_messages(post_id):
    return db.get_livechat_messages(post_id)

def add_livechat_message(post_id, text, color):
    return db.add_livechat_message(post_id, text, color)

def vote_poll(post_id, option_index):
    return db.vote_poll(post_id, option_index)

def get_poll(post_id):
    return db.get_poll(post_id)

if __name__ == "__main__":
    db = FirebaseConfessionDB(config.get('FIREBASE_URL'), config.get('FIREBASE_CRED_PATH', 'service.json'))
    db.seed_db()
    print("Database reset and seeded with demo posts (polls + random upvotes 1-5)")
