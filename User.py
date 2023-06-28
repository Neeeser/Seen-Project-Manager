from firebase_admin import db
import datetime


class User:

    def __init__(self, name: str, user_name: str, password: str,
                 date_joined: str = datetime.date.today().strftime("%B-%d-%Y"), projects: [] = None):
        if projects is None:
            projects = []
        self.name = name
        self.projects = projects
        self.user_name = user_name
        self.password = password
        self.date_joined = date_joined
        self.save_user()

    def asdict(self):
        return {self.user_name: {"name": self.name, "projects": self.projects, "date_joined": self.date_joined,
                                 "password": self.password}}

    # Format user_name, name, projects {}, password
    def save_user(self):
        user_path = db.reference("root/users/")
        user_path.update(self.asdict())
