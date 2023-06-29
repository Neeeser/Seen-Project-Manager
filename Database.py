from firebase_admin import db
from firebase_admin import credentials
import firebase_admin
from User import User
from Project import Project


class Database:

    def __init__(self):
        self.users = {}
        self.projects = {}
        self.firebase_address = "seenworkflow_private_key.json"

        self.cred = credentials.Certificate(self.firebase_address)
        firebase_admin.initialize_app(self.cred, {'databaseURL': "https://seenworkflow-default-rtdb.firebaseio.com/"})
        self.root_path = db.reference('root')
        self.users_path = db.reference('root/users')
        self.projects_path = db.reference('root/projects')

    def load_all_users(self):
        users_db = self.users_path.get()
        for user in users_db:
            self.users[user] = User(users_db[user]["name"], user, users_db[user]["password"],
                                    users_db[user]["date_joined"])

    def load_all_projects(self):
        projects_db = self.projects_path.get()
        for project in projects_db:
            project_dict = projects_db[project]
            self.projects[project] = Project(project, project_dict["owner"], project_dict["date_created"],
                                             project_dict["due_date"],
                                             project_dict["people"])

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


if __name__ == '__main__':
    db = Database()
    db.load_all_projects()
    db.add_users_to_project("Muni Sma", ["buck", "l"])
