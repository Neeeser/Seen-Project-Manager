import PySimpleGUI as sg
from Database import Database
from Project import Project
import json


class DesktopGui:

    def __init__(self):
        ### Fields
        self.max_reports = 6
        self.reports_row = 2
        self.displayed_project = None
        sg.theme('BlueMono')  # Add a touch of color

        self.loggedIn = False
        self.user = None
        self.name = ""
        # Creating Database and loading the projects into it
        self.db = Database()
        self.db.load_all_projects()
        self.db.load_all_users()

        self.check_if_logged_in()

        # User Login Window
        self.login_popup_layout = [
            [sg.Text("Username:", size=10), sg.Input(default_text="", do_not_clear=True, key="username", size=15)],
            [sg.Text("Password:", size=10), sg.Input(default_text="", key="password", size=15, password_char='*')],
            [sg.Button("Login"), sg.Button("Cancel"), sg.Checkbox("Stay Logged In?", default=True, key="staylogin")]]

        self.choice = sg.Window('Login', self.login_popup_layout,
                                disable_close=False, return_keyboard_events=True)

        self.run_login()

        # Main Report Page
        self.layout = [
            [sg.Button('Submit'), sg.Button('Exit'), sg.Text(self.name),
             sg.Button("Logout")],
            [sg.Combo(values=tuple(self.db.projects.keys()), default_value='None', readonly=False,
                      k='-COMBO-', enable_events=True, size=30)
                , sg.Text("Project:", visible=False), sg.Text("Owner:", visible=False)]]
        self.setup_reports()

        # text = sg.popup_get_text("Login")
        # print(text)
        # self.load_projects_into_layout()
        self.window = sg.Window('Seen', self.layout)

    def run_login(self):
        while self.loggedIn != True:
            self.login_event, self.login_values = self.choice.read()
            if self.login_event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.login_event == 'Cancel':
                break

            if self.login_event == 'Login':
                username = self.login_values["username"]
                password = self.login_values["password"]
                if username != "" and password != "":
                    if self.login(username, password):
                        if self.login_values["staylogin"] is True:
                            self.save_login_info()
                        break

        self.choice.close()

    def run(self):

        while self.loggedIn:  # Event Loop

            self.event, self.values = self.window.read()

            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == 'Submit':
                self.submit_report()

            if self.event == '-COMBO-':
                self.displayed_project = self.db.projects[self.values['-COMBO-']]
                self.load_project_into_layout(self.displayed_project)

            if self.event == 'Logout':
                self.window.close()
                self.logout()

        self.window.close()

    def login(self, username, password):
        if self.db.validate_user(username, password):
            self.user = self.db.users[username]
            self.loggedIn = True
            self.name = self.user.name
            return True
        return False

    def check_if_logged_in(self):
        try:
            f = open("users.json")
            data = json.load(f)
            username = data["username"]
            password = data["password"]
            self.login(username, password)
            f.close()

        except IOError:
            return False

    def save_login_info(self):
        try:
            f = open("users.json", 'w+')
            data = {"username": self.user.user_name, "password": self.user.password}
            json.dump(data, f)
            f.close()
        except IOError:
            return False

    def logout(self):
        try:
            f = open("users.json", 'w+')
            data = {"username": "", "password": ""}
            json.dump(data, f)
            self.db.close()
            f.close()
            self.__init__()

        except IOError:
            return False

    def setup_reports(self):
        temp_layout = [[], []]
        for i in range(self.max_reports):
            temp_layout[0].append(sg.Text("NOT DEFINED", visible=False, pad=(1, 0), expand_x=True))
            temp_layout[1].append(
                sg.Multiline('', size=(30, 10), expand_x=True, expand_y=True, k='report' + str(i),
                             visible=False))
        self.layout.insert(self.reports_row, temp_layout)

    def submit_report(self):
        if self.displayed_project is None:
            return False
        for i in range(len(self.displayed_project.reports_to)):
            if self.values['report' + str(i)] != '':
                self.displayed_project.add_report(self.displayed_project.owner, self.displayed_project.reports_to[i],
                                                  self.values['report' + str(i)])

    def load_project_into_layout(self, project: Project):
        self.layout[1][1].update(value="Project: " + project.project_name, visible=True)
        self.layout[1][2].update(value="Owner: " + project.owner, visible=True)

        for i in range(len(project.reports_to)):
            self.layout[self.reports_row][0][i].update(visible=True, value=project.reports_to[i])
            self.layout[self.reports_row][1][i].update(visible=True)

        for i in range(len(project.reports_to), self.max_reports):
            self.layout[self.reports_row][0][i].update(visible=False)
            self.layout[self.reports_row][1][i].update(visible=False)


DesktopGui().run()
