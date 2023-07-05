from firebase_admin import db
from User import User


class Group:

    def __init__(self, name: str, users: [] = None):
        self.name = name
        if users is None:
            users = []
        self.users = set(users)
        self.users.discard(None)
        self.firebase_path = "root/groups/" + self.name

    def asdict(self):
        return {"users": list(self.users)}

    def save_group(self):
        db.reference(self.firebase_path).update(self.asdict())

    def add_user(self, user: User):
        self.users.add(user.user_name)
        self.save_group()
