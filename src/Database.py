import hashlib
import os
import sys

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from Group import Group
from Project import Project
from User import User


class Database:

    def __init__(self, firebase_key=None):
        self.users = {}
        self.projects = {}
        self.groups = {}
        if firebase_key is None:
            self.firebase_address = "private_key.json"
            if getattr(sys, 'frozen', False):
                self.firebase_address = os.path.join(sys._MEIPASS, self.firebase_address)
        else:
            self.firebase_address = firebase_key

        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)

        self.cred = credentials.Certificate(self.firebase_address)
        self.app = firebase_admin.initialize_app(self.cred,
                                                 {'databaseURL': "https://seenworkflow-default-rtdb.firebaseio.com/"})
        self.root_path = db.reference('root')
        self.users_path = db.reference('root/users')
        self.projects_path = db.reference('root/projects')
        self.groups_path = db.reference('root/groups')

    def load_all(self):
        self.load_all_projects()
        self.load_all_users()
        self.load_all_groups()
        self.check_due_dates()

    def load_all_users(self):
        users_db = self.users_path.get()

        for user in users_db:
            projects = []
            if "projects" in users_db[user]:
                projects = users_db[user]["projects"]
            self.users[user] = User(users_db[user]["name"], user, password=users_db[user]["password"],
                                    date_joined=users_db[user]["date_joined"], projects=projects)

    def load_all_projects(self):
        projects_db = self.projects_path.get()
        if projects_db:
            for project in projects_db:
                project_dict = projects_db[project]
                self.projects[project] = Project(project, project_dict["owner"], project_dict["reports_to"],
                                                 project_dict["date_created"],
                                                 project_dict["due_date"],
                                                 project_dict["people"], project_dict["interval"])

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

    def check_user_name(self, username: str):
        if username in self.users:
            return False
        return True

    def add_group(self, group: Group):
        self.groups[group.name] = group
        group.save_group()

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

    def get_due_dates(self):
        due_dates = {}
        for project in self.projects:
            due_dates[project] = self.projects[project].due_date
        return due_dates

    def check_due_dates(self):
        for project in self.projects:
            self.projects[project].update_due_date()

    def remove_project(self, project: Project):
        # Step 1 remove project from people:
        for people in project.people:
            self.users[people].remove_from_project(project.project_name)
        # Step 2 Remove project from firebase
        db.reference(project.firebase_path).delete()
        # Step 3 remove project from database
        self.projects.pop(project.project_name)

    def update_project(self, project: Project, project_dict: {}):
        # Clear all people from old project name
        if project.project_name != project_dict["Name"]:
            old_people = project.people
            for people in old_people:
                self.users[people].remove_from_project(project.project_name)

            for people in project_dict["People"]:
                self.users[people].add_to_projects(project_dict["Name"])

        # Update All project values
        project.reports_to = project_dict["Groups"]
        project.people = project_dict["People"]
        project.interval = project_dict["Interval"]
        project.change_owner(project_dict["Owners"])

        project.save_project()
        if project.project_name != project_dict["Name"]:
            p_child = db.reference('root/projects/').child(project.project_name).get()

            self.projects_path.update({project_dict["Name"]: p_child})

            db.reference('root/projects/' + project.project_name).delete()
            self.projects.pop(project.project_name)

            project.project_name = project_dict["Name"]
            self.load_all_projects()

    def get_projects_for_group(self, group: str):
        projects_toreturn = []
        for projects in self.projects:
            if group in self.projects[projects].reports_to:
                projects_toreturn.append(self.projects[projects].project_name)
        return projects_toreturn

    def create_user(self, name, username, password):
        u = User(name, username, un_hashed_password=password)
        u.save_user()
        self.users[username] = u


if __name__ == '__main__':
    db = Database()
    db.load_all_projects()
    print(db.projects["Bond Fund"].get_over_due_dates())
