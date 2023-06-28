from User import User


class Project:

    def __init__(self, owner: User, date_created):
        self.owner = owner
        self.people = {self.owner}
        self.due_date = None
        self.date_created = None

    def report_to(self, user: User, report: str):
        return
