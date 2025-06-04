import json
from pathlib import Path

DB_PATH = Path("users.json")  # Файл с пользователями


def load_users():
    if DB_PATH.exists():
        return set(json.loads(DB_PATH.read_text()))
    return set()


def save_users(users):
    DB_PATH.write_text(json.dumps(list(users), indent=2))


users_db = load_users()
