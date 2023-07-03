import PySimpleGUI as sg
from Database import Database
from Project import Project
import json
from User import User


class ComboPopUp(sg.Window):

    def __init__(self, name: str, options: []):
        self.layout = [[sg.Listbox(values=options, size=(20, 5), key="listboxpopup",
                                   enable_events=True, select_mode=sg.SELECT_MODE_MULTIPLE)],
                       [sg.Button("Accept"), sg.Button("Cancel")]]
        super().__init__(name, self.layout, disable_close=False, return_keyboard_events=True)

    def get(self) -> []:
        while True:
            self.event, self.com_values = self.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == 'Cancel':
                break

            if self.event == 'Accept' or self.event == '\r':
                projects = self.com_values["listboxpopup"]
                if projects is None:
                    projects = []
                self.close()

                return projects

        self.close()
        return []


class DesktopGui:

    def __init__(self):
        # Fields
        self.max_reports = 6
        self.reports_row = 1
        self.displayed_project = None
        sg.theme('DarkBlue')  # Add a touch of color
        self.text_background_color = "gray"
        self.loggedIn = False
        self.user = None
        self.name = ""
        # Creating Database and loading the projects into it
        self.db = Database()
        self.db.load_all_projects()
        self.db.load_all_users()

        # Checks on Start up if logged in already
        self.check_if_logged_in()

        # User Login Window
        self.login_popup_layout = [
            [sg.Text("Username:", size=10), sg.Input(default_text="", do_not_clear=True, key="username", size=15)],
            [sg.Text("Password:", size=10), sg.Input(default_text="", key="password", size=15, password_char='*')],
            [sg.Button("Login"), sg.Button("Cancel"), sg.Checkbox("Stay Logged In?", default=True, key="staylogin")]]

        self.choice = sg.Window('Login', self.login_popup_layout,
                                disable_close=False, return_keyboard_events=True)

        self.run_login()

        # Reports Tab
        self.reports_tab_layout = [
            [sg.Button('Submit'), sg.Combo(values=tuple(self.user.projects), default_value='None', readonly=False,
                                           k='-COMBO-', enable_events=True, size=30)
                , sg.Text("Owner:", visible=False), sg.Button('Load Latest', key="loadlatest", visible=False)]]
        self.setup_reports()

        # Dashboard tab layout
        self.dashboard_tab_layout = [[sg.Text("Your Projects")],
                                     [sg.Listbox(values=self.user.projects, size=(20, 5), key="projectslist",
                                                 enable_events=True, select_mode=sg),
                                      sg.Text("", visible=False)],
                                     [sg.Text("Add yourself to projects:"), sg.Button("Projects", key="addprojects")]]

        # Tab Layout
        self.tabs_layout = [[sg.Text(self.name, background_color=self.text_background_color), sg.Button('Exit'),
                             sg.Button("Logout")],
                            [sg.TabGroup([[sg.Tab("Dashboard", self.dashboard_tab_layout),
                                           sg.Tab("Reports", self.reports_tab_layout)]])]]

        # Main Page
        self.window = sg.Window('Seen', self.tabs_layout)

        self.run()

    def run_login(self):

        while not self.loggedIn:
            self.login_event, self.login_values = self.choice.read()
            if self.login_event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.login_event == 'Cancel':
                break

            if self.login_event == 'Login' or self.login_event == '\r':
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

            if self.event == "loadlatest":
                self.load_latest_reports()

            if self.event == "projectslist":
                self.load_project_due_date()

            if self.event == "addprojects":
                value = ComboPopUp("projects", list(self.db.projects.keys())).get()

        self.window.close()

    def load_project_due_date(self):
        due_date = self.db.projects[self.values["projectslist"][0]].due_date
        self.dashboard_tab_layout[1][1].update(value="Next report due:\n" + due_date, visible=True)

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
            temp_layout[0].append(
                sg.Text("NOT DEFINED", visible=False, pad=(1, 0), background_color=self.text_background_color,
                        expand_x=True,
                        justification="center", auto_size_text=False, size=10))
            temp_layout[1].append(
                sg.Multiline('', size=(30, 10), expand_x=True, expand_y=True, k='report' + str(i),
                             visible=False))
        self.reports_tab_layout.insert(self.reports_row, temp_layout[0])
        self.reports_tab_layout.insert(self.reports_row + 1, temp_layout[1])

    def submit_report(self):
        if self.displayed_project is None:
            return False

        last_reports = self.displayed_project.load_last_report(self.user)
        for i in range(len(self.displayed_project.reports_to)):
            last_report_no_time = ""
            if self.displayed_project.reports_to[i] in last_reports:
                last_report_no_time = last_reports[self.displayed_project.reports_to[i]].split('=')[1]

            if self.values['report' + str(i)] != '' and self.values['report' + str(i)] != last_report_no_time:
                self.displayed_project.add_report(self.user.user_name, self.displayed_project.reports_to[i],
                                                  self.values['report' + str(i)])
                self.db.load_all_projects()

    def load_project_into_layout(self, project: Project):
        self.reports_tab_layout[0][2].update(value="Owner: " + project.owner, visible=True,
                                             background_color=self.text_background_color)

        self.reports_tab_layout[0][3].update(visible=True)

        for i in range(len(project.reports_to)):
            self.reports_tab_layout[self.reports_row][i].update(visible=True, value=project.reports_to[i])
            self.reports_tab_layout[self.reports_row + 1][i].update(visible=True, value="")

        for i in range(len(project.reports_to), self.max_reports):
            self.reports_tab_layout[self.reports_row][i].update(visible=False)
            self.reports_tab_layout[self.reports_row + 1][i].update(visible=False, value="")

    def load_latest_reports(self):
        latest_reports = self.displayed_project.load_last_report(self.user)
        for group in latest_reports:
            multi_line_box_index = self.displayed_project.reports_to.index(group)
            last_report_no_time = latest_reports[group].split('=')[1]
            self.reports_tab_layout[self.reports_row + 1][multi_line_box_index].update(value=last_report_no_time)

    def add_user_to_projects(self, user: User, projects: []):
        if isinstance(projects, str):
            projects = [projects]

        for project in projects:
            if project not in self.user.projects:
                self.user.projects.append(project)


DesktopGui()
