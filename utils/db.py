import firebase_admin
from firebase_admin import credentials
import firebase_admin.db as fb_db
from datetime import datetime
import uuid

class FirebaseConfessionDB:
    def __init__(self, database_url: str, cred_path="service.json"):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                "databaseURL": database_url
            })
        self.ref = fb_db.reference("confessions")

        import json
        import uuid
        try:
            self.ref.delete() 
            with open("db.json", "r", encoding="utf-8") as f:
                entries = json.load(f)
            for entry in entries:
                post_id = str(uuid.uuid4())
                confession = {
                    "id": post_id,
                    "title": entry["title"],
                    "content": entry["content"],
                    "country": entry.get("country", "Anonymous"),
                    "upvote_count": entry.get("upvote_count", 0),
                    "created_at": entry["created_at"],
                    "comments": entry.get("comments", [])
                }
                self.ref.child(post_id).set(confession)
            print(f"Cleared and seeded {len(entries)} confessions to Firebase.")
        except Exception as e:
            print(f"Could not seed database: {e}")

    def post_confession(self, title: str, content: str, country: str):
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
        self.ref.child(post_id).set(confession)
        return post_id

    def get_all_confessions(self):
        confessions = self.ref.get()
        if not confessions:
            return []

        return sorted(confessions.values(), key=lambda x: x["created_at"], reverse=True)

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

database_url = ""
db = FirebaseConfessionDB(database_url)


def upvote_confession(post_id):
    return db.upvote(post_id)

def post_confession(title, content, country):
    return db.post_confession(title, content, country)

def get_all_confessions():
    return db.get_all_confessions()

def post_comment(post_id, content):
    return db.post_comment(post_id, content)

if __name__ == "__main__":
    import json
    from datetime import datetime
    with open("db.json", "r", encoding="utf-8") as f:
        entries = json.load(f)
    db = FirebaseConfessionDB("https://chatting-app-81842-default-rtdb.firebaseio.com/")
    for entry in entries:

        import uuid
        post_id = str(uuid.uuid4())
        confession = {
            "id": post_id,
            "title": entry["title"],
            "content": entry["content"],
            "country": entry.get("country", "Anonymous"),
            "upvote_count": entry.get("upvote_count", 0),
            "created_at": entry["created_at"],
            "comments": entry.get("comments", [])
        }
        db.ref.child(post_id).set(confession)
    print(f"Imported {len(entries)} confessions to Firebase.")
