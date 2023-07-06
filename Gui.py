import PySimpleGUI as sg
from Database import Database
from Project import Project
import json
from User import User
from datetime import datetime

theme = {"BACKGROUND": "#34384b", "TEXT": "#fafafa", "INPUT": "#ffffff", "TEXT_INPUT": "#000000",
         "SCROLL": "#e9dcbe",
         "BUTTON": ("#ffffff", "#00a758"), "PROGRESS": ('#000000', '#000000'), "BORDER": 1,
         "TAB": "00a758",
         "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0,
         "COLOR_LIST": ["#ffffff", "#ffffff", "#ffffff", "#ffffff"], "DESCRIPTION": ["Grey", "Brown"]}


class ComboPopUp(sg.Window):

    def __init__(self, name: str, options: [], default_values: [] = None):
        self.options = options
        self.layout = [[sg.Input(size=(20, 1), enable_events=True, key='-INPUT-')],
                       [sg.Listbox(values=options, size=(20, 5), key="listboxpopup",
                                   enable_events=True, select_mode=sg.SELECT_MODE_MULTIPLE,
                                   default_values=default_values)],
                       [sg.Button("Accept"), sg.Button("Cancel")]]
        super().__init__(name, self.layout, disable_close=False, return_keyboard_events=True, keep_on_top=True)

    def get(self) -> []:
        self.input_length = 0
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
            elif self.event != "listboxpopup":
                if self.com_values['-INPUT-'] != '':  # if a keystroke entered in search field
                    search = self.com_values['-INPUT-'].lower()
                    new_values = [x for x in self.options if search in x.lower()]  # do the filtering
                    self['listboxpopup'].update(new_values)  # display in the listbox
                else:
                    # display original unfiltered list
                    self['listboxpopup'].update(self.options)

        self.close()
        return []


class CreateProjectPopup(sg.Window):
    def __init__(self, database: Database):
        self.layout = [[sg.Text("Project Name:"), sg.Input(size=15, expand_x=True, key="projectname")],
                       [sg.Button("Owners", expand_x=True, key="owners"),
                        sg.Button("Groups", expand_x=True, key="groups")],
                       [sg.Button("People", expand_x=True, key="people")],
                       [sg.Button("Due Date", expand_x=True, key="date"), sg.Text("Interval:"),
                        sg.Input(size=5, key="interval", enable_events=True)],
                       [sg.Text("", key="error", visible=False)],
                       [sg.Button("Create Project", key="create", expand_x=True)]]
        super().__init__("Create Project", self.layout, disable_close=False, return_keyboard_events=True,
                         resizable=True, keep_on_top=True)
        self.db = database
        self.owners = []
        self.people = []
        self.project_name = ""
        self.due_date = ""
        self.interval = None
        self.groups = []

    def get(self):
        while True:
            self.event, self.values = self.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            elif self.event == "owners":
                self.owners = ComboPopUp("Owners", list(self.db.users), list(self.owners)).get()

            elif self.event == "people":
                self.people = ComboPopUp("People", list(self.db.users), list(self.people)).get()

            elif self.event == "groups":
                self.groups = ComboPopUp("Groups", list(self.db.groups), list(self.groups)).get()

            elif self.event == "date":
                date = sg.popup_get_date()
                if date:
                    self.due_date = datetime.strptime(str(date[0]) + "/" + str(date[1]) + "/" + str(date[2]),
                                                      "%m/%d/%Y").strftime("%B-%d-%Y")
            elif self.event == 'interval':
                text = self.values['interval']
                if not self.valid(text):
                    self['interval'].update(value=text[:-1])
                else:
                    self.interval = text

            elif self.event == "create":
                if self.values["projectname"] == "":
                    self["error"].update("Please enter a project name", visible=True, text_color="Red")
                elif self.values["projectname"] in self.db.projects:
                    self["error"].update("Project Name already Taken", visible=True, text_color="Red")

                elif not self.owners:
                    self["error"].update("Please select owners", visible=True, text_color="Red")
                elif not self.groups:
                    self["error"].update("Please select groups", visible=True, text_color="Red")
                elif self.due_date == "":
                    self["error"].update("Please select first due date", visible=True, text_color="Red")
                else:
                    v = sg.popup_ok_cancel(
                        "Are you sure you want to create project: " + self.values["projectname"] + "?",
                        keep_on_top=True)
                    if v == "OK":
                        p = Project(self.values["projectname"], self.owners, self.groups, due_date=self.due_date,
                                    people=self.people, interval=self.interval)
                        self.close()
                        return p
        self.close()
        return None

    def valid(self, text):
        if len(text) == 1 and text in '+-':
            return True
        else:
            try:
                number = float(text)
                return True
            except:
                return False


class DesktopGui:

    def __init__(self):
        # Fields
        self.max_reports = 6
        self.reports_row = 1
        self.displayed_project = None
        # sg.theme('DarkGrey4')  # Add a touch of color
        sg.theme_add_new("Seen Theme", theme)
        sg.theme("Seen Theme")
        self.text_background_color = "#00a758"
        self.loggedIn = False
        self.user = None
        self.name = ""
        # Creating Database and loading the projects into it
        self.db = Database()
        self.db.load_all_projects()
        self.db.load_all_users()
        self.db.load_all_groups()
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

        # Project Tab
        self.project_tab_layout = [
            [sg.Text("Manage Projects", size=30, expand_x=True, background_color=self.text_background_color,
                     justification="center")], [sg.Button("Create Project", key="createproject")]]

        # Reports Tab
        self.reports_tab_layout = [
            [sg.Button('Save'), sg.Button("Submit"),
             sg.Combo(values=tuple(self.user.projects), default_value='None', readonly=False,
                      k='-COMBO-', enable_events=True, size=30)
                , sg.Text("Owner:", visible=False, key="owner", background_color="#ececec", text_color="#34384b"),
             sg.Button('Load Latest', key="loadlatest", visible=False)
             ]]
        self.setup_reports()

        # Dashboard tab layout
        self.dashboard_tab_layout = [
            [sg.Text("Your Projects", font=("Segoe UI", 18, "bold"), text_color="#34384b",
                     background_color="#ececec"), sg.Push(background_color="#ececec"),
             sg.Button("Add Projects", key="addprojects", font=("Segoe UI", 13, "bold"), size=(10, 1), pad=(20, 3),
                       border_width=1)],

            [sg.Listbox(values=list(self.user.projects), size=(25, 8), key="projectslist",
                        enable_events=True, select_mode=sg, no_scrollbar=True,
                        background_color="#00a758", text_color="#ffffff",
                        highlight_background_color="#c6c6c6", highlight_text_color="#ffffff", pad=(0, 0),
                        font=("Segoe UI", 13, ""), expand_y=True),
             sg.Text("", visible=False, key="duedate", pad=(0, 0), background_color="#ececec", text_color="#34384b",
                     font=("Segoe UI", 13, "bold"), expand_y=True)]]

        # Tab Layout
        self.tabs_layout = [
            [sg.Text(self.name, font=("Segoe UI", 20, "bold")), sg.Push(),
             sg.Button("Logout", expand_y=False, size=(7, 1), font=("Segoe UI", 12, "bold")),
             sg.Button('Exit', expand_y=False, size=(7, 1), font=("Segoe UI", 12, "bold"))
             ],
            [sg.TabGroup([[sg.Tab("Dashboard", self.dashboard_tab_layout, background_color="#ececec",
                                  border_width=0),
                           sg.Tab("Reports", self.reports_tab_layout, border_width=0, background_color="#ececec"),
                           sg.Tab("Projects", self.project_tab_layout, border_width=0, background_color="#ececec")]],
                         border_width=0,
                         focus_color="clear", background_color="#ececec",
                         tab_background_color="#ececec", selected_background_color="#c6c6c6",
                         selected_title_color="black", tab_border_width=0,
                         pad=(0, 0), expand_y=True)]]

        # Main Page
        # self.window = sg.Window('Seen', self.tabs_layout, background_color="grey20", titlebar_text_color="black")
        self.window = sg.Window('Seen', self.tabs_layout, font=("Segoe UI", 15, ""), no_titlebar=False,
                                margins=(0, 0))

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

            if self.event == 'Save':
                self.save_report()

            if self.event == '-COMBO-':
                self.displayed_project = self.db.projects[self.values['-COMBO-']]
                self.load_project_into_layout(self.displayed_project)

            if self.event == 'Logout':
                self.window.close()
                self.logout()

            if self.event == "loadlatest":
                self.load_latest_reports()
                self.displayed_project.get_sorted_reports()

            if self.event == "projectslist":
                self.load_project_due_date()

            if self.event == "createproject":
                p = CreateProjectPopup(self.db).get()
                if p:
                    p.save_project()
                    for people in p.people:
                        self.db.users[people].projects.add(p.project_name)
                    self.db.load_all_projects()
                    self.update_project_lists()
            if self.event == "addprojects":
                value = ComboPopUp("projects", list(self.db.projects.keys())).get()
                self.add_user_to_projects(self.user, value)

            if "lastedit" in self.event:
                index = self.window[self.event].widget.current()
                element_num = self.event.split("lastedit")[1]
                last_edit = self.values[self.event]
                value = \
                    self.displayed_project.report_history[self.displayed_project.reports_to[int(element_num)]][index][2]
                self.window["report" + str(element_num)].update(value=value)
        self.window.close()

    def update_project_lists(self):
        self.window["projectslist"].update(list(self.user.projects))
        self.window["-COMBO-"].update(values=tuple(self.user.projects))

    def load_project_due_date(self):
        if self.values["projectslist"][0] is not None:
            due_date = self.db.projects[self.values["projectslist"][0]].due_date
            self.window["duedate"].update(value="Next report due:\n" + due_date, visible=True)
        else:
            self.window["duedate"].update(value="Next report due:\n", visible=True)

    def login(self, username, password):
        if self.db.validate_user(username, password):
            self.user = self.db.users[username]
            self.loggedIn = True
            self.name = self.user.name
            return True
        return False

    def login_with_hash(self, username, pass_hash):
        if self.db.validate_user_hash(username, pass_hash):
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
            pass_hash = data["password"]
            # self.login(username, password)
            self.login_with_hash(username, pass_hash)
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
        temp_layout = [[], [], []]
        for i in range(self.max_reports):
            temp_layout[0].append(
                sg.Text("NOT DEFINED", visible=False, pad=(1, 0), background_color=self.text_background_color,
                        expand_x=True,
                        justification="center", auto_size_text=False, size=10, key="report_to" + str(i)))
            temp_layout[1].append(
                sg.Multiline('', size=(25, 10), expand_x=True, expand_y=True, k='report' + str(i),
                             visible=False))
            temp_layout[2].append(
                sg.Combo(values=tuple(), default_value='None', k='lastedit' + str(i), enable_events=True,
                         visible=False, expand_x=True))
        self.reports_tab_layout.insert(self.reports_row, temp_layout[0])
        self.reports_tab_layout.insert(self.reports_row + 1, temp_layout[1])
        self.reports_tab_layout.insert(self.reports_row + 2, temp_layout[2])

    def save_report(self):
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
        owner = True if self.user.user_name in project.owner else False
        self.window["owner"].update(
            value="Owner: " + list(project.owner).__str__().replace("[", "").replace("]", "").replace("'", ""),
            visible=True)

        self.window["loadlatest"].update(visible=True)

        for i in range(len(project.reports_to)):
            reports_history = project.get_sorted_reports()
            value = []
            if project.reports_to[i] in reports_history:
                value = [i[:2] for i in reports_history[project.reports_to[i]]]

            text = ""
            self.window["report_to" + str(i)].update(visible=True, value=project.reports_to[i])
            self.window["report" + str(i)].update(visible=True, value=text, disabled=not owner)
            self.window["lastedit" + str(i)].update(
                values=value,
                visible=True)

        for i in range(len(project.reports_to), self.max_reports):
            self.window["report_to" + str(i)].update(visible=False)
            self.window["report" + str(i)].update(visible=False, value="")
            self.window["lastedit" + str(i)].update(visible=False)

    def load_latest_reports(self):
        latest_reports = self.displayed_project.load_last_report(self.user)
        for group in latest_reports:
            multi_line_box_index = self.displayed_project.reports_to.index(group)
            last_report_no_time = latest_reports[group].split('=')[1]
            self.reports_tab_layout[self.reports_row + 1][multi_line_box_index].update(value=last_report_no_time)

    def add_user_to_projects(self, user: User, projects: []):
        self.db.add_user_to_projects(user, projects)
        self.update_project_lists()


DesktopGui()
