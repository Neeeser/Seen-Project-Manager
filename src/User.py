from firebase_admin import db
import datetime
import hashlib


class User:

    def __init__(self, name: str, user_name: str, password: str = None, un_hashed_password: str = None,
                 date_joined: str = None, projects: [] = None):
        if projects is None:
            projects = []
        self.name = name
        self.projects = set(projects)
        self.projects.discard(None)
        self.user_name = user_name
        self.password = password

        if password is None:
            self.update_password_hash(un_hashed_password)
        if date_joined is None:
            date_joined = datetime.date.today().strftime("%B-%d-%Y")
        self.date_joined = date_joined

        # self.update_password_hash(password)

    def asdict(self):
        return {self.user_name: {"name": self.name, "projects": list(self.projects), "date_joined": self.date_joined,
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

    def add_to_projects(self, projects: []):
        if isinstance(projects, str):
            projects = [projects]
        self.projects.update(projects)
        self.projects.discard(None)
        self.save_user()

    def remove_from_project(self, project_name: str):
        try:
            self.projects.remove(project_name)
            self.save_user()
        except KeyError:
            print("Issue removing project:" + project_name + " from user " + self.user_name)
