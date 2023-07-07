from User import User
import datetime
from firebase_admin import db
from datetime import timedelta


class Project:

    def __init__(self, project_name: str, owner: [], reports_to: [], date_created=None, due_date=None, people=None,
                 interval=30):
        self.project_name = project_name
        if isinstance(owner, str):
            owner = [owner]
        self.owner = set(owner)
        if people is None or people == []:
            people = self.owner
        self.people = set(people)
        self.people.discard(None)
        if date_created is None:
            date_created = datetime.date.today().strftime("%B-%d-%Y")
        self.interval = interval
        if due_date is None:
            due_date = [self.get_date_future(interval)]
        self.due_date = due_date
        if not isinstance(due_date, list):
            self.due_date = [self.due_date]
        self.date_created = date_created
        self.firebase_path = "root/projects/" + self.project_name
        if isinstance(reports_to, str):
            reports_to = [reports_to]
        self.reports_to = reports_to
        self.report_history = {}
        # self.save_project()

    def __contains__(self, item):
        return isinstance(item, User) and item.user_name in self.people

    def get_date_future(self, days: int):
        return (datetime.datetime.now() + timedelta(days)).strftime("%B-%d-%Y")

    def asdict(self):
        return {"owner": list(self.owner), "people": list(self.people), "due_date": self.due_date,
                "date_created": self.date_created, "reports_to": self.reports_to}

    def save_project(self):
        project_path = db.reference(self.firebase_path)
        project_path.update(self.asdict())

    def add_report(self, user: str, report_to: str, report: str, date: str = None):
        if date is None:
            date = datetime.datetime.now().strftime("%I:%M%p:%B-%d-%Y")
        reports_path = db.reference(
            self.firebase_path + "/reports/" + "/" + report_to + "/" + user)
        print(reports_path.path.__str__())
        reports_path.update({len(reports_path.get()) if reports_path.get() is not None else 0: date + "=" + report})

    def add_user(self, user: str):
        if user not in self.people:
            self.people.add(user)
            self.people.discard(None)
            self.save_project()
            return True
        return False

    def get_over_due_dates(self):
        return [x for x in self.due_date if datetime.datetime.strptime(x, "%B-%d-%Y") < datetime.datetime.today()]

    def get_upcoming_due_dates(self):
        return [x for x in self.due_date if datetime.datetime.strptime(x, "%B-%d-%Y") >= datetime.datetime.today()]

    def remove_user(self, user: str):
        if user in self.people and user is not self.owner:
            self.people.remove(user)
            self.save_project()
            return True
        return False

    def change_owner(self, user: str):
        self.owner = user

    def load_last_report(self, user: User) -> {}:
        reports_path = db.reference(self.firebase_path + "/reports").get()

        return_dict = {}
        if reports_path is not None:
            for group in reports_path:
                if user.user_name in reports_path[group]:
                    return_dict[group] = list(reports_path[group][user.user_name])[-1]

        return return_dict

    def get_sorted_reports(self):
        reports_path = db.reference(self.firebase_path + "/reports").get()
        sorted_dict_list = {}
        if reports_path is not None:
            for group in reports_path:
                sorted_dict_list[group] = []
                for user in reports_path[group]:
                    for value in reports_path[group][user]:
                        date, report = value.split('=')
                        sorted_dict_list[group].append((date, user, report))
                sorted_dict_list[group] = sorted(sorted_dict_list[group],
                                                 key=lambda t: datetime.datetime.strptime(t[0].split('=')[0],
                                                                                          '%I:%M%p:%B-%d-%Y'),
                                                 reverse=True)
        self.report_history = sorted_dict_list
        return sorted_dict_list

    def submit_report(self, report: {}, due_date: str):
        if due_date in self.due_date:
            self.due_date.remove(due_date)
            db.reference(self.firebase_path + "/submissions").update({due_date: report})
            self.save_project()
