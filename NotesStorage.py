import json
from pathlib import Path
from note import Note

class NotesStorage:
    def __init__(self):
        self.data_dir = Path.home() / "MyNotes"
        self.data_file = self.data_dir / "notes.json"
        self.data_dir.mkdir(exist_ok=True)
        self.notes = self.load()

    def load(self):
        if not self.data_file.exists():
            return[]
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Note.from_dict(note_data) for note_data in data]
        except Exception as e:
            print(f"Error load notes: {e}")
            return []
        
    def save(self):
        try:
            data = [note.to_dict() for note in self.notes]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                return True
        except Exception as e:
            print(f"Error load notes: {e}")
            return False
        
    def add_note(self, note):
        self.notes.insert(0, note)
        self.save()

    def delete_note(self, note_id):
        self.notes = [n for n in self.notes if n.id != note_id]
        self.save()

    def get_note(self, note_id):
        for note in self.notes:
            if note.id == note_id:
                return note
        return None