from User import User
import datetime
from firebase_admin import db
from datetime import timedelta


class Project:

    def __init__(self, project_name: str, owner: str, date_created=None, due_date=None, people=None):
        self.project_name = project_name
        self.owner = owner
        if people is None:
            people = [self.owner]
        self.people = people
        if date_created is None:
            date_created = datetime.date.today().strftime("%B-%d-%Y")
        if due_date is None:
            due_date = self.get_date_future(30)
        self.due_date = due_date
        self.date_created = date_created
        self.firebase_path = "root/projects/" + self.project_name
        # self.save_project()

    def get_date_future(self, days: int):
        return (datetime.datetime.now() + timedelta(days)).strftime("%B-%d-%Y")

    def asdict(self):
        return {"owner": self.owner, "people": self.people, "due_date": self.due_date,
                "date_created": self.date_created}

    def save_project(self):
        project_path = db.reference(self.firebase_path)
        project_path.update(self.asdict())

    def add_report(self, user: str, report_to: str, report: str, date: str = None):
        if date is None:
            date = datetime.datetime.now().strftime("%I:%M%p:%B-%d-%Y")
        reports_path = db.reference(
            self.firebase_path + "/reports/" + "/" + report_to + "/" + user)
        print(reports_path.path.__str__())
        reports_path.update({date: report})

    def add_user(self, user: str):
        if user not in self.people:
            self.people.append(user)
            self.save_project()
            return True
        return False

    def remove_user(self, user: str):
        if user in self.people and user is not self.owner:
            self.people.remove(user)
            self.save_project()
            return True
        return False

    def change_owner(self, user: str):
        self.owner = user
