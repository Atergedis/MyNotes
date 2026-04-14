from datetime import datetime

class Note:
    def __init__(self, id=None, title="", text="", created_at=None, updated_at=None):
        self.id = id or self._generate_id()
        self.title = title
        self.text = text

        now = datetime.now().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def _generate_id(self):
        import time
        import random
        import string

        timestamp = str(int(time.time()*1000))
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return timestamp + random_str
    
    def update(self, title, text):
        self.title = title
        self.text = text
        self.updated_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            text=data.get("text", ""),
            created_at=data.get("createdAt"),
            updated_at=data.get("updatedAt")
        )