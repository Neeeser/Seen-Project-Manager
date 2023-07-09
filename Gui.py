import PySimpleGUI as sg
from Database import Database
from Project import Project
import json
from User import User
from datetime import datetime
import sys, os

theme = {"BACKGROUND": "#34384b", "TEXT": "#fafafa", "INPUT": "#ffffff", "TEXT_INPUT": "#000000",
         "SCROLL": "#e9dcbe",
         "BUTTON": ("#ffffff", "#00a758"), "PROGRESS": ('#000000', '#000000'), "BORDER": 1,
         "TAB": "00a758",
         "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0,
         "COLOR_LIST": ["#ffffff", "#ffffff", "#ffffff", "#ffffff"], "DESCRIPTION": ["Grey", "Brown"]}


class PopUp(sg.Window):

    def __init__(self, text: str):
        self.layout = [[sg.Text(text, background_color="#ececec", text_color="#34384b", font=("Segoe UI", 15, "bold"))],
                       [sg.Button("Ok", size=10)]]

        super().__init__("", self.layout, disable_close=False, keep_on_top=True, auto_close=True,
                         auto_close_duration=10, background_color="#ececec", font=("Segoe UI", 15, "bold"),
                         element_justification="c", resizable=False)

        while True:
            self.event, self.com_values = self.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == "Ok":
                break
        self.close()


class ComboPopUp(sg.Window):

    def __init__(self, name: str, options: [], default_values: [] = None, icon: str = None):
        self.options = options
        self.layout = [[sg.Input(size=(20, 1), enable_events=True, key='-INPUT-', expand_x=True, pad=(0, 0),
                                 background_color="#ececec", text_color="#34384b", border_width=0)],
                       [sg.Listbox(values=options, size=(20, 5), key="listboxpopup",
                                   enable_events=True, select_mode=sg.SELECT_MODE_MULTIPLE,
                                   default_values=default_values, no_scrollbar=True,
                                   background_color="#00a758", text_color="#ffffff",
                                   highlight_background_color="#c6c6c6", highlight_text_color="#ffffff", pad=(0, 0),
                                   expand_x=True)],
                       [sg.Button("Accept", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                                  font=("Segoe UI", 15, "bold")),
                        sg.Button("Cancel", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                                  font=("Segoe UI", 15, "bold"))]]
        super().__init__(name, self.layout, disable_close=False, return_keyboard_events=True, keep_on_top=True,
                         font=("Segoe UI", 15, ""), margins=(0, 0), background_color="#ececec", icon=icon)
        self.selected = []

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

            if self.event == "listboxpopup":
                self.selected = self.com_values["listboxpopup"]

            elif self.event == "-INPUT-":
                if self.com_values['-INPUT-'] != '':  # if a keystroke entered in search field
                    search = self.com_values['-INPUT-'].lower()
                    new_values = [x for x in self.options if search in x.lower()]  # do the filtering
                    selected = [x for x in self.selected if x in new_values]
                    self['listboxpopup'].update(new_values)  # display in the listbox
                    self["listboxpopup"].set_value(selected)

                else:
                    # display original unfiltered list
                    self['listboxpopup'].update(self.options)
                    self["listboxpopup"].set_value(self.selected)

        self.close()
        return []


class SubmitPopUp(sg.Window):
    def __init__(self, project: Project, icon=None):
        self.project = project
        self.due_dates = self.project.due_date

        self.layout = [
            [sg.Text("Which due dates?", expand_x=True, pad=(0, 0), font=("Segoe UI", 20, "bold"))],
            [sg.Text("Upcoming Due Dates", expand_x=True, size=(12, 3), pad=(0, 0),
                     background_color="#ececec", text_color="#34384b"),
             sg.Push(background_color="#ececec"),
             sg.Listbox(values=self.project.get_upcoming_due_dates(),
                        size=(25, 3), key="upcoming",
                        enable_events=True,
                        expand_x=False,
                        select_mode=sg.SELECT_MODE_MULTIPLE,
                        no_scrollbar=True,
                        background_color="#00a758",
                        text_color="#ffffff",
                        highlight_background_color="#c6c6c6",
                        highlight_text_color="#ffffff", pad=(0, 0),
                        font=("Segoe UI", 13, ""), expand_y=True)],
            [sg.Text("Overdue Dates", expand_x=True, size=(12, 3), pad=(0, 0), background_color="#ececec",
                     text_color="#34384b"),
             sg.Push(background_color="#ececec"),
             sg.Listbox(values=self.project.get_over_due_dates(),
                        size=(25, 3), key="overdue",

                        enable_events=True,
                        select_mode=sg.SELECT_MODE_MULTIPLE,
                        no_scrollbar=True,
                        background_color="#00a758",
                        text_color="#ffffff",
                        highlight_background_color="#c6c6c6",
                        highlight_text_color="#ffffff", pad=(0, 0),
                        font=("Segoe UI", 13, ""), expand_y=True)],
            [sg.Button("Accept", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                       font=("Segoe UI", 15, "bold")),
             sg.Button("Cancel", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                       font=("Segoe UI", 15, "bold"))]
        ]

        super().__init__("Submit Project?", self.layout, disable_close=False, return_keyboard_events=True,
                         keep_on_top=True,
                         font=("Segoe UI", 15, ""), margins=(0, 0), background_color="#ececec", icon=icon)

    def get(self):
        while True:
            self.event, self.com_values = self.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == "Cancel":
                break

            if self.event == "Accept":
                to_return = []
                to_return.extend(self["overdue"].get())
                to_return.extend(self["upcoming"].get())

                self.close()
                return to_return

        self.close()
        return None


class CreateProjectPopup(sg.Window):
    def __init__(self, database: Database):
        self.layout = [[sg.Text("Project Name:", background_color="#ececec", text_color="#34384b"),
                        sg.Input(size=15, expand_x=True, key="projectname", expand_y=True)],
                       [sg.Button("Owners", expand_x=True, key="owners", expand_y=True),
                        sg.Button("Groups", expand_x=True, key="groups", expand_y=True)],
                       [sg.Button("People", expand_x=True, key="people", expand_y=True)],
                       [sg.Button("Due Date", expand_x=True, key="date", expand_y=True),
                        sg.Push(background_color="#ececec"),
                        sg.Text("Interval:", background_color="#ececec", text_color="#34384b"),
                        sg.Input(size=5, key="interval", enable_events=True, expand_y=True, expand_x=True)],
                       [sg.Text("", key="error", visible=False, expand_y=True, background_color="#ececec")],
                       [sg.Button("Create Project", key="create", expand_x=True, expand_y=True)]]
        super().__init__("Create Project", self.layout, disable_close=False, return_keyboard_events=True,
                         resizable=False, keep_on_top=True, font=("Segoe UI", 15, ""), background_color="#ececec")
        self.db = database
        self.owners = []
        self.people = []
        self.project_name = ""
        self.due_date = ""
        self.interval = 30
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

        self.userfile = "users.json"
        # if getattr(sys, 'frozen', False):
        #     self.userfile = os.path.join(sys._MEIPASS, self.userfile)

        self.icon = "manulife.ico"
        if getattr(sys, 'frozen', False):
            self.icon = os.path.join(sys._MEIPASS, self.icon)

        # sg.theme('DarkGrey4')  # Add a touch of color
        sg.theme_add_new("Seen Theme", theme)
        sg.theme("Seen Theme")
        self.text_background_color = "#00a758"
        self.loggedIn = False
        self.user = None
        self.name = ""
        # Creating Database and loading the projects into it
        self.db = Database()
        self.db.load_all()
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

        self.manage_project_preface = "manageproject"
        self.project_edit_layout = [[sg.Text("Project Name:", background_color="#ececec", text_color="#34384b"),
                                     sg.Input(size=15, expand_x=True, key=self.manage_project_preface + "projectname",
                                              expand_y=False)],
                                    [sg.Button("Owners", expand_x=True, key=self.manage_project_preface + "owners",
                                               expand_y=False),
                                     sg.Button("Groups", expand_x=True, key=self.manage_project_preface + "groups",
                                               expand_y=False)],
                                    [sg.Button("People", expand_x=True, key=self.manage_project_preface + "people",
                                               expand_y=False)],
                                    [sg.Button("Due Date", expand_x=True, key=self.manage_project_preface + "date",
                                               expand_y=False),
                                     sg.Push(background_color="#ececec"),
                                     sg.Text("Interval:", background_color="#ececec", text_color="#34384b"),
                                     sg.Input(size=5, key=self.manage_project_preface + "interval", enable_events=True,
                                              expand_y=False,
                                              expand_x=True)],
                                    [sg.Text("", key=self.manage_project_preface + "error", visible=False,
                                             expand_y=False,
                                             background_color="#ececec")],
                                    [sg.Button("Apply Edits", key=self.manage_project_preface + "create",
                                               expand_x=True,
                                               expand_y=False),
                                     sg.Button("Remove Project", key=self.manage_project_preface + "remove",
                                               expand_x=False,
                                               expand_y=False, size=16, button_color="#d03a39")]]

        # Project Tab
        self.project_tab_layout = [
            [sg.Text("Manage Projects", font=("Segoe UI", 18, "bold"), text_color="#34384b",
                     background_color="#ececec"), sg.Push(background_color="#ececec"),
             sg.Button("New Project", key="createproject", font=("Segoe UI", 13, "bold"), size=(10, 1),
                       pad=((0, 5), 3),
                       border_width=1)],
            [sg.Listbox(values=list(self.user.projects), size=(25, 8), key="projectstablist",
                        enable_events=True, select_mode=sg, no_scrollbar=True,
                        background_color="#00a758", text_color="#ffffff",
                        highlight_background_color="#c6c6c6", highlight_text_color="#ffffff", pad=(0, 0),
                        font=("Segoe UI", 13, ""), expand_y=True),
             sg.Frame(layout=self.project_edit_layout, title="", size=(400, 300), pad=(0, 0),
                      background_color="#ececec",
                      border_width=0, expand_y=True, expand_x=False)]]

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
             sg.Button("Add Projects", key="addprojects", font=("Segoe UI", 13, "bold"), size=(10, 1), pad=((0, 5), 3),
                       border_width=1)],

            [sg.Listbox(values=list(self.user.projects), size=(25, 8), key="projectslist",
                        enable_events=True, select_mode=sg, no_scrollbar=True,
                        background_color="#00a758", text_color="#ffffff",
                        highlight_background_color="#c6c6c6", highlight_text_color="#ffffff", pad=(0, 0),
                        font=("Segoe UI", 13, ""), expand_y=True),
             sg.Text("", visible=True, key="duedate", pad=(0, 0), background_color="#ececec", text_color="#34384b",
                     font=("Segoe UI", 13, "bold"), expand_y=True, size=18),
             sg.Text("", visible=True, key="overduedate", pad=((0, 0), 0), background_color="#ececec",
                     text_color="#34384b",
                     font=("Segoe UI", 13, "bold"), expand_y=True, size=18)
             ]]

        # Tab Layout
        self.tabs_layout = [[sg.Text(self.name, font=("Segoe UI", 20, "bold")), sg.Push(),
                             sg.Button("Logout", expand_y=False, size=(7, 1),
                                       font=("Segoe UI", 12, "bold")),
                             sg.Button('Exit', expand_y=False, size=(7, 1),
                                       font=("Segoe UI", 12, "bold"))
                             ],
                            [sg.TabGroup([[sg.Tab("Dashboard", self.dashboard_tab_layout, background_color="#ececec",
                                                  border_width=0, key="dashboardtab"),
                                           sg.Tab("Reports", self.reports_tab_layout, border_width=0,
                                                  background_color="#ececec", key="reporttab"),
                                           sg.Tab("Projects", self.project_tab_layout, border_width=0,
                                                  background_color="#ececec", key="projecttab")]], enable_events=True,
                                         key="tabs",
                                         border_width=0,
                                         focus_color="clear", background_color="#ececec",
                                         tab_background_color="#ececec", selected_background_color="#c6c6c6",
                                         selected_title_color="black", tab_border_width=0,
                                         pad=(0, 0), expand_y=True, expand_x=True)]]

        # Main Page
        # self.window = sg.Window('Seen', self.tabs_layout, background_color="grey20", titlebar_text_color="black")
        self.window = sg.Window('Seen', self.tabs_layout, font=("Segoe UI", 15, ""), no_titlebar=False,
                                margins=(0, 0), icon=self.icon, resizable=True, finalize=True)
        self.window.set_min_size((627, 400))
        self.run()

    def run_login(self):

        while not self.loggedIn:
            self.login_event, self.login_values = self.choice.read()
            if self.login_event in (sg.WIN_CLOSED, 'Exit'):
                sys.exit(0)

            if self.login_event == 'Cancel':
                sys.exit(0)

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

            if self.event == 'Submit':
                self.submit_report()

            if self.event == '-COMBO-':
                self.displayed_project = self.db.projects[self.values['-COMBO-']]
                self.load_project_into_layout(self.displayed_project)

            if self.event == "projectstablist":
                self.displayed_project = self.db.projects[self.values['projectstablist'][0]]
                self.update_manage_projects()

            if self.event == 'Logout':
                self.window.close()
                self.logout()

            if self.values["tabs"] == "projecttab":
                if self.displayed_project is not None:
                    self.update_manage_projects()

            if self.values["tabs"] == "reporttab":
                if self.displayed_project is not None:
                    self.load_project_into_layout(self.displayed_project)

            if self.event == self.manage_project_preface + "remove":
                if self.displayed_project is not None:
                    sg.popup_yes_no(title="Remove" + self.displayed_project.project_name)
                    self.remove_project(self.displayed_project)

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
                        self.db.users[people].save_user()
                    self.db.load_all_projects()
                    self.update_project_lists()
            if self.event == "addprojects":
                value = ComboPopUp("Projects", list(self.db.projects.keys()), icon=self.icon).get()
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
        self.window["projectstablist"].update(values=tuple(self.user.projects))

    def load_project_due_date(self):
        if self.values["projectslist"]:
            if self.values["projectslist"][0] is not None:
                due_date = self.db.projects[self.values["projectslist"][0]].due_date[-1]
                overdue_dates = self.db.projects[self.values["projectslist"][0]].get_over_due_dates_as_string()

                self.window["duedate"].update(value="Next report due:\n" + due_date, visible=True)
                if overdue_dates != "":
                    self.window["overduedate"].update(value="Overdue reports:\n" + overdue_dates, visible=True)
                else:
                    self.window["overduedate"].update(value="Overdue reports:\nNone", visible=True)

            else:
                self.window["duedate"].update(value="Next report due:\n", visible=True)
                self.window["overduedate"].update(value="Overdue reports:\n None", visible=True)

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

            f = open(self.userfile)
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
            f = open(self.userfile, 'w+')
            data = {"username": self.user.user_name, "password": self.user.password}
            json.dump(data, f)
            f.close()
        except IOError:
            print("Can't access Logout File")
            return False

    def logout(self):
        try:
            f = open(self.userfile, 'w+')
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
                sg.Text("NOT DEFINED", visible=False, pad=(0, 0), background_color=self.text_background_color,
                        expand_x=True,
                        justification="center", auto_size_text=False, size=10, key="report_to" + str(i)))
            temp_layout[1].append(
                sg.Multiline('', size=(25, 10), expand_x=True, expand_y=True, k='report' + str(i),
                             visible=False, no_scrollbar=True, pad=(0, 0)))
            temp_layout[2].append(
                sg.Combo(values=tuple(), default_value='None', k='lastedit' + str(i), enable_events=True,
                         visible=False, expand_x=True, pad=(0, 0), button_arrow_color="#34384b",
                         button_background_color="#ececec", tooltip="Show Previous Saves"))
        self.reports_tab_layout.insert(self.reports_row, temp_layout[0])
        self.reports_tab_layout.insert(self.reports_row + 1, temp_layout[1])
        self.reports_tab_layout.insert(self.reports_row + 2, temp_layout[2])

    def update_manage_projects(self):
        if self.displayed_project is not None or self.db.projects[self.values['projectstablist'][0]] is not None:
            self.window["projectstablist"].set_value([self.displayed_project.project_name])
            self.window[self.manage_project_preface + "projectname"].update(value=self.displayed_project.project_name)
            self.window[self.manage_project_preface + "interval"].update(value=self.displayed_project.interval)

    def submit_report(self):
        if self.displayed_project:
            for i in range(len(self.displayed_project.reports_to)):
                if self.values['report' + str(i)] == '':
                    PopUp("Please fill in all boxes")
                    return

            due_dates = SubmitPopUp(self.displayed_project).get()
            if due_dates:
                report = {}
                for i in range(len(self.displayed_project.reports_to)):
                    report[self.displayed_project.reports_to[i]] = self.values['report' + str(i)]

                for due_date in due_dates:
                    self.displayed_project.submit_report(report, due_date)
                self.save_report()

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

        self.load_project_into_layout(self.displayed_project)

    def load_project_into_layout(self, project: Project):
        owner = True if self.user.user_name in project.owner else False
        self.window["-COMBO-"].update(value=self.displayed_project.project_name)

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
            self.window["report" + str(i)].update(visible=True, value=text, disabled=not owner,
                                                  background_color="#ececec" if not owner else "#ffffff")
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

    def clear_manage_project(self):
        self.window["projectstablist"].set_value(None)
        self.window[self.manage_project_preface + "projectname"].update(value="")
        self.window[self.manage_project_preface + "interval"].update(value="")

    def remove_project(self, project: Project):
        self.clear_manage_project()
        self.setup_reports()
        self.displayed_project = None
        self.db.remove_project(project)
        self.update_project_lists()


DesktopGui()
