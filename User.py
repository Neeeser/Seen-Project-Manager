from firebase_admin import db
import datetime
import hashlib


class User:

    def __init__(self, name: str, user_name: str, password: str,
                 date_joined: str = datetime.date.today().strftime("%B-%d-%Y"), projects: [] = None):
        if projects is None:
            projects = []
        self.name = name
        self.projects = projects
        self.user_name = user_name
        self.password = ""
        self.update_password_hash(password)
        self.date_joined = date_joined

        # self.save_user()

    def asdict(self):
        return {self.user_name: {"name": self.name, "projects": self.projects, "date_joined": self.date_joined,
                                 "password": self.password}}

    # Format user_name, name, projects {}, password
    def save_user(self):
        user_path = db.reference("root/users/")
        user_path.update(self.asdict())

    def update_password_hash(self, password):
        password_utf = password.encode('utf-8')
        sha1hash = hashlib.sha1()
        sha1hash.update(password_utf)
        self.password = sha1hash.hexdigest()
