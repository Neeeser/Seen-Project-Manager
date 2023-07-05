from firebase_admin import db
from firebase_admin import credentials
import firebase_admin
from User import User
from Project import Project
import hashlib
from Group import Group


class Database:

    def __init__(self):
        self.users = {}
        self.projects = {}
        self.groups = {}
        self.firebase_address = "seenworkflow_private_key.json"

        self.cred = credentials.Certificate(self.firebase_address)
        self.app = firebase_admin.initialize_app(self.cred,
                                                 {'databaseURL': "https://seenworkflow-default-rtdb.firebaseio.com/"})
        self.root_path = db.reference('root')
        self.users_path = db.reference('root/users')
        self.projects_path = db.reference('root/projects')
        self.groups_path = db.reference('root/groups')

    def load_all_users(self):
        users_db = self.users_path.get()
        for user in users_db:
            self.users[user] = User(users_db[user]["name"], user, password=users_db[user]["password"],
                                    date_joined=users_db[user]["date_joined"], projects=users_db[user]["projects"])

    def load_all_projects(self):
        projects_db = self.projects_path.get()
        for project in projects_db:
            project_dict = projects_db[project]
            self.projects[project] = Project(project, project_dict["owner"], project_dict["reports_to"],
                                             project_dict["date_created"],
                                             project_dict["due_date"],
                                             project_dict["people"])

    def load_all_groups(self):
        group_db = self.groups_path.get()
        for group in group_db:
            group_dict = group_db[group]
            self.groups[group] = Group(group, group_dict["users"])

    def add_users_to_project(self, project, users: []):
        if isinstance(project, str):
            if project in self.projects:
                project = self.projects[project]

            else:
                return False

        if isinstance(users, str):
            users = [users]

        for user in users:
            project.add_user(user)

        print(project.people)
        return True

    def validate_user(self, username, password):
        if username in self.users:
            user = self.users[username]
            if self.password_matches(password, user.password):
                return True

        return False

    def validate_user_hash(self, username, pass_hash):
        if username in self.users:
            user = self.users[username]
            if user.password == pass_hash:
                return True
        return False

    def password_matches(self, password, a_hash):
        password_utf = password.encode('utf-8')
        sha1hash = hashlib.sha1()
        sha1hash.update(password_utf)
        password_hash = sha1hash.hexdigest()
        return password_hash == a_hash

    def close(self):
        firebase_admin.delete_app(self.app)

    def add_user_to_projects(self, user: User, projects: []):
        if isinstance(projects, str):
            projects = [projects]

        user.add_to_projects(projects)

        for project in projects:
            self.projects[project].add_user(user.user_name)


if __name__ == '__main__':
    db = Database()
    db.load_all_projects()
    db.add_users_to_project("Muni Sma", ["buck", "l"])
    print(db.projects)
    Project("Ant ETF", "Bob", ["GWAM", "LEN"]).save_project()
    db.load_all_projects()
    print(db.projects)
