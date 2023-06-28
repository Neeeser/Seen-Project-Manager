from User import User
import datetime
from firebase_admin import db
from datetime import timedelta


class Project:

    def __init__(self, project_name: str, owner: str, date_created=datetime.date.today().strftime("%B-%d-%Y")):
        self.project_name = project_name
        self.owner = owner
        self.people = [self.owner]
        self.due_date = self.get_date_future(30)
        self.date_created = date_created
        self.firebase_path = "root/projects/" + self.project_name
        self.save_project()

    def get_date_future(self, days: int):
        return (datetime.datetime.now() + timedelta(days)).strftime("%B-%d-%Y")

    def asdict(self):
        return {self.project_name: {"owner": self.owner, "people": self.people, "due_date": self.due_date,
                                    "date_created": self.date_created}}

    def save_project(self):
        user_path = db.reference("root/projects/")
        user_path.update(self.asdict())

    def add_report(self, user: str, report_to: str, report: str, date: str = None):
        if date is None:
            date = datetime.datetime.now().strftime("%I:%M%p:%B-%d-%Y")
        reports_path = db.reference(
            self.firebase_path + "/reports/" + "/" + report_to + "/" + user + "/" + date + "/" + "reports/")
        reports_path.update({"report": report})
