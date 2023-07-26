import PySimpleGUI as sg
from Database import Database
from Project import Project
import json
from User import User
from datetime import datetime
import sys, os
from sys import platform
from Group import Group
import csv

# Theme used in the program. Many windows manually override this
theme = {"BACKGROUND": "#34384b", "TEXT": "#fafafa", "INPUT": "#ffffff", "TEXT_INPUT": "#000000",
         "SCROLL": "#e9dcbe",
         "BUTTON": ("#ffffff", "#00a758"), "PROGRESS": ('#000000', '#000000'), "BORDER": 1,
         "TAB": "00a758",
         "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0,
         "COLOR_LIST": ["#ffffff", "#ffffff", "#ffffff", "#ffffff"], "DESCRIPTION": ["Grey", "Brown"]}


# Window to create new users
class CreateNewUser(sg.Window):
    # Pass in database so the window can create it's own users
    def __init__(self, db: Database):
        self.db = db
        # Layout
        self.layout = [
            [sg.Text("Full Name:", background_color="#ececec", text_color="#34384b", size=8),
             sg.In(size=15, key="name", enable_events=True)],
            [sg.Text("Username:", background_color="#ececec", text_color="#34384b", size=8),
             sg.In(size=15, key="username")],
            [sg.pin(elem=sg.Text(background_color="#ececec", text_color="Red", visible=False, key="error", pad=(0, 0)),
                    shrink=True)],
            [sg.Text("Password:", background_color="#ececec", text_color="#34384b", size=8),
             sg.In(size=15, password_char='*', key="pass", enable_events=True)],
            [sg.Text("Retype:", background_color="#ececec", text_color="#34384b", size=8),
             sg.In(size=15, password_char='*', key="retype", enable_events=True)],
            [sg.pin(
                elem=sg.Text(background_color="#ececec", text_color="Red", visible=False, key="passerror", pad=(0, 0)),
                shrink=True)],
            [sg.Button("Create", expand_x=True),
             sg.Button("Cancel", expand_x=True)],
            [sg.pin(elem=sg.Text(background_color="#ececec", text_color="Red", visible=False, key="createerror",
                                 pad=(0, 0)),
                    shrink=True)]]

        super().__init__("New User", self.layout, keep_on_top=True, font=("Segoe UI", 15, ""),
                         background_color="#ececec", element_justification="left")

    # Call this when creating a new window to trigger to window to start and return data
    def get(self):
        while True:
            self.event, self.com_values = self.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == "Cancel":
                break

            elif self.event == "name":
                name = self["name"].get()
                name = name.lower().replace(" ", "_")
                self["username"].update(value=name)
                if not self.db.check_user_name(name):
                    self["error"].update(value="User name taken", visible=True)
                else:
                    self["error"].update(visible=False)

            elif self.event == "pass":
                self["retype"].update(value="")

            elif self.event == "retype":
                retype = self["retype"].get()
                password = self["pass"].get()
                if password != "":
                    if retype == password or retype == "":
                        self["passerror"].update(visible=False)
                    else:
                        self["passerror"].update(visible=True, value="Passwords do not match")

            elif self.event == "Create":
                name = self["name"].get()
                if name == "":
                    self["createerror"].update(value="Please Enter a Name", visible=True)
                    continue
                username = self["username"].get()
                if username == "":
                    self["createerror"].update(value="Please Enter a Username", visible=True)
                    continue
                password = self["pass"].get()
                retype = self["retype"].get()
                if password == "" or retype == "":
                    self["createerror"].update(value="Please Enter a password", visible=True)
                    continue
                if password != retype:
                    continue

                self.db.create_user(name, username, password)
                self.close()
                return

        self.close()
        return None


# Window to export data lets you export data as different types
# To add more types change export_types variable to reflect the name and supply a method to export
class ExportPopUp(sg.Window):

    def __init__(self, name: str, report_dict: {}, icon: str = None):
        self.report_dict = report_dict
        export_types = (("Comma separated value", ".csv"), ("Plain Text", ".txt"))
        self.layout = [[sg.In(key="save_as", size=15, disabled=True, expand_x=True),
                        sg.SaveAs("Browse", pad=(3, 3), button_color=("#34384b", "#ececec"),
                                  font=("Segoe UI", 15, "bold"), key="save_as",
                                  enable_events=False, default_extension=".csv",
                                  file_types=export_types)],
                       [sg.Button("Accept", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                                  font=("Segoe UI", 15, "bold")),
                        sg.Button("Cancel", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                                  font=("Segoe UI", 15, "bold"))]]

        super().__init__(name, self.layout, disable_close=False, return_keyboard_events=True, keep_on_top=False,
                         font=("Segoe UI", 15, ""), margins=(0, 0), background_color="#ececec", icon=icon)
        self.selected = []

    # Call this to start window
    def get(self) -> []:
        while True:
            self.event, self.com_values = self.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == 'Cancel':
                break

            if self.event == 'Accept':
                if self["save_as"].get():
                    file_extension = os.path.splitext(self["save_as"].get())[-1]
                    if file_extension == ".csv":
                        self.save_as_csv(self["save_as"].get())
                    elif file_extension == ".txt":
                        self.save_as_txt(self["save_as"].get())
                    self.close()

        self.close()
        return

    # Saves in csv format
    def save_as_csv(self, path):
        with open(path, 'w+', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(self.report_dict)

    # Saves in plain text format
    def save_as_txt(self, path):
        with open(path, 'w+', newline='') as txtfile:
            for i in range(len(self.report_dict)):
                txtfile.write(self.report_dict[0][i] + ":\n")
                if i != len(self.report_dict) - 1:
                    txtfile.write(self.report_dict[1][i] + "\n\n")
                else:
                    txtfile.write(self.report_dict[1][i])


# Create groups only needs group name for now
class NewGroupPopUP(sg.Window):

    # Pass in database to allow for window to create group
    def __init__(self, db: Database):
        self.db = db
        self.button_pad = (2, 2)
        self.layout = [[sg.Text("Group Name:", background_color="#ececec", text_color="#34384b"),
                        sg.Input(size=10, pad=self.button_pad, key="groupname")],
                       [
                           # sg.Button(button_text="Users", expand_x=True, pad=self.button_pad),
                           sg.Button(button_text="Create", expand_x=True, pad=self.button_pad),
                           sg.Button(button_text="Cancel", expand_x=True, pad=self.button_pad, button_color="#d03a39")],
                       [sg.pin(
                           sg.Text("", key="error", background_color="#ececec", text_color="#d03a39", visible=False),
                           shrink=True)]
                       ]

        super().__init__("New Group", self.layout, disable_close=False, return_keyboard_events=True,
                         resizable=False, keep_on_top=True, font=("Segoe UI", 15, ""), background_color="#ececec")

    def get(self):
        while True:
            self.event, self.com_values = self.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == "Cancel":
                break

            if self.event == "Create":
                group_text = self["groupname"].get().strip()
                if group_text not in self.db.groups:
                    group = Group(group_text, [""])
                    self.db.add_group(group)

                    self.close()
                    return group
                else:
                    self["error"].update(visible=True, value="Group name taken")
        self.close()
        return None


class GroupsPage(sg.Tab):

    def __init__(self, db: Database):
        self.groups = db.groups

        report_viewer_frame = sg.Frame("",
                                       [[
                                           sg.Text("Submitted Reports", font=("Segoe UI", 15, ""),
                                                   background_color="#ececec", text_color="#34384b"),
                                           sg.Push(background_color="#ececec"),
                                           sg.Text("", key="submittedbytext", background_color="#ececec",
                                                   text_color="#34384b")],
                                           [sg.Combo([], expand_x=True, key="submittedproject",
                                                     enable_events=True, visible=False)],
                                           [sg.Multiline(size=33, expand_x=True, expand_y=True, key="submittedtext",
                                                         visible=False)],
                                           [sg.Combo(values=[], expand_x=True, key="submittedreports",
                                                     enable_events=True, visible=False)]],
                                       background_color="#ececec",
                                       border_width=0, expand_y=True, expand_x=False, font=("Segoe UI", 15, ""),
                                       title_color="#34384b", element_justification="left")

        self.layout = [[sg.Text("Manage Groups", font=("Segoe UI", 18, "bold"), text_color="#34384b",
                                background_color="#ececec"), sg.Push(background_color="#ececec"),
                        sg.Button("New Group", key="creategroup", font=("Segoe UI", 13, "bold"), size=(10, 1),
                                  pad=((0, 5), 3),
                                  border_width=1)],
                       [sg.Listbox(values=list(self.groups), size=(25, 8), key="grouplist",
                                   enable_events=True, select_mode=sg, no_scrollbar=True,
                                   background_color="#00a758", text_color="#ffffff",
                                   highlight_background_color="#c6c6c6", highlight_text_color="#ffffff", pad=(0, 0),
                                   font=("Segoe UI", 13, ""), expand_y=True), report_viewer_frame

                        ]]

        super().__init__("Groups", self.layout, background_color="#ececec",
                         border_width=0, key="groupstab", element_justification="left")


class DueDateEditor(sg.Window):

    def __init__(self, project: Project, icon=None):
        self.project = project
        self.top_button_size = 8
        self.top_expand = True
        self.top_pad = (3, 5)

        self.temp_project = Project("NULL", [], [], due_date=project.due_date.copy())

        self.layout = [
            [sg.Text("Which due dates?", expand_x=True, pad=(0, 0), font=("Segoe UI", 20, "bold"),
                     background_color="#34384b")],
            [sg.Text("Upcoming Due Dates", expand_x=True, size=(12, 3), pad=(0, 0),
                     background_color="#ececec", text_color="#34384b"),
             sg.Push(background_color="#ececec"),
             sg.Listbox(values=self.project.get_upcoming_due_dates(),
                        size=(25, 3), key="upcoming",
                        enable_events=True,
                        expand_x=False,
                        select_mode=sg.SELECT_MODE_SINGLE,
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
                        select_mode=sg.SELECT_MODE_SINGLE,
                        no_scrollbar=True,
                        background_color="#00a758",
                        text_color="#ffffff",
                        highlight_background_color="#c6c6c6",
                        highlight_text_color="#ffffff", pad=(0, 0),
                        font=("Segoe UI", 13, ""), expand_y=True)],

            [sg.Button("New", size=self.top_button_size, expand_x=self.top_expand, pad=self.top_pad),
             sg.Button("Edit", size=self.top_button_size, expand_x=self.top_expand, pad=self.top_pad),
             sg.Button("Remove", size=self.top_button_size, expand_x=self.top_expand, pad=self.top_pad,
                       button_color="#d03a39")],
            [sg.Button("Accept", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                       font=("Segoe UI", 15, "bold")),
             sg.Button("Cancel", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                       font=("Segoe UI", 15, "bold"))]
        ]

        super().__init__("Edit Due Dates?", self.layout, disable_close=False, return_keyboard_events=True,
                         keep_on_top=True,
                         font=("Segoe UI", 15, ""), margins=(0, 0), background_color="#ececec", icon=icon)

    def run(self):
        while True:
            self.event, self.com_values = self.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == "upcoming":
                self["overdue"].set_value("")

            elif self.event == "overdue":
                self["upcoming"].set_value("")

            if self.event == "New":
                date = sg.popup_get_date()
                if date:
                    date = datetime.strptime(str(date[0]) + "/" + str(date[1]) + "/" + str(date[2]),
                                             "%m/%d/%Y").date()
                    self.temp_project.add_new_due_date(date)
                    self.update_boxes_temp_project()

            if self.event == "Remove":
                if self.get_selected():
                    self.temp_project.due_date.remove(self.get_selected()[0])
                    self.update_boxes_temp_project()

            elif self.event == "Edit":
                if self.get_selected():
                    date = sg.popup_get_date()
                    if date:
                        new_date = datetime.strptime(str(date[0]) + "/" + str(date[1]) + "/" + str(date[2]),
                                                     "%m/%d/%Y")
                        self.temp_project.due_date.remove(self.get_selected()[0])
                        self.temp_project.add_new_due_date(new_date)
                        self.update_boxes_temp_project()

            elif self.event == "Accept":
                if YesNoPopup("Apply to " + self.project.project_name + "?").get():
                    self.project.due_date = self.temp_project.due_date.copy()
                    self.project.save_project()
                self.close()

            elif self.event == "Cancel":
                self.close()
                return None

        self.close()
        return

    def get_selected(self):
        upcoming = self["upcoming"].get()
        overdue = self["overdue"].get()

        if upcoming:
            return upcoming
        elif overdue:
            return overdue
        else:
            return None

    def update_boxes_temp_project(self):
        self["upcoming"].update(values=self.temp_project.get_upcoming_due_dates())
        self["overdue"].update(values=self.temp_project.get_over_due_dates())


class YesNoPopup(sg.Window):
    def __init__(self, text):
        self.layout = [[sg.Text(text, background_color="#ececec", text_color="#34384b", font=("Segoe UI", 15, "bold"),
                                justification="c")],
                       [sg.Button("Yes", size=10), sg.Button("No", size=10)]]

        super().__init__("", self.layout, disable_close=False, keep_on_top=True, background_color="#ececec",
                         font=("Segoe UI", 15, "bold"),
                         element_justification="c", resizable=False)

    def get(self):
        while True:
            self.event, self.com_values = self.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == "Yes":
                self.close()
                return True

            if self.event == "No":
                self.close()
                return False

        self.close()


class ProjectEditFrame(sg.Frame):

    def __init__(self):
        self.manage_project_preface = "manageproject"

        self.project_edit_layout = [[sg.Text("Project Name:", background_color="#ececec", text_color="#34384b"),
                                     sg.Input(size=15, expand_x=True, key=self.manage_project_preface + "projectname",
                                              expand_y=False)],
                                    [sg.Button("Owners", expand_x=False, size=10,
                                               key=self.manage_project_preface + "owners",
                                               expand_y=False), sg.Text("", background_color="#ececec",
                                                                        key=self.manage_project_preface + "ownerstext")],
                                    [sg.Button("Groups", expand_x=False, size=10,
                                               key=self.manage_project_preface + "groups",
                                               expand_y=False), sg.Text("", background_color="#ececec",
                                                                        key=self.manage_project_preface + "groupstext")],
                                    [sg.Button("People", expand_x=False, size=10,
                                               key=self.manage_project_preface + "people",
                                               expand_y=False), sg.Text("", background_color="#ececec",
                                                                        key=self.manage_project_preface + "peopletext")],
                                    [sg.Button("Due Date", expand_x=False, size=10,
                                               key=self.manage_project_preface + "date",
                                               expand_y=False),
                                     sg.Text("", key=self.manage_project_preface + "duedatetext",
                                             background_color="#ececec"),
                                     sg.Push(background_color="#ececec"),
                                     sg.Text("Interval:", background_color="#ececec", text_color="#34384b"),
                                     sg.Input(size=2, key=self.manage_project_preface + "interval", enable_events=True,
                                              expand_y=False,
                                              expand_x=True)],

                                    [sg.Button("Apply Edits", key=self.manage_project_preface + "create",
                                               expand_x=True,
                                               expand_y=False),
                                     sg.Button("Remove Project", key=self.manage_project_preface + "remove",
                                               expand_x=False,
                                               expand_y=False, size=16, button_color="#d03a39")],
                                    [sg.Text("", key=self.manage_project_preface + "error", visible=False,
                                             expand_y=False,
                                             background_color="#ececec", text_color="Red")]]

        super().__init__(layout=self.project_edit_layout, title="", size=(400, 300), pad=(0, 0),
                         background_color="#ececec",
                         border_width=0, expand_y=True, expand_x=False)


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

    def __init__(self, name: str, options: [], default_values: [] = None, icon: str = None, fit_size=False,
                 search_bar=True):
        size = (20, 5)
        expand_y = False
        if fit_size:
            size = (None, None)
            expand_y = True

        self.options = options
        self.layout = [[sg.Input(size=(20, 1), enable_events=True, key='-INPUT-', expand_x=True, pad=(0, 0),
                                 background_color="#ececec", text_color="#34384b", border_width=0)],
                       [sg.Listbox(values=options, size=size, key="listboxpopup",
                                   enable_events=True, select_mode=sg.SELECT_MODE_MULTIPLE,
                                   default_values=default_values, no_scrollbar=True,
                                   background_color="#00a758", text_color="#ffffff",
                                   highlight_background_color="#c6c6c6", highlight_text_color="#ffffff", pad=(0, 0),
                                   expand_x=True, expand_y=expand_y)],
                       [sg.Button("Accept", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                                  font=("Segoe UI", 15, "bold")),
                        sg.Button("Cancel", expand_x=True, pad=(3, 3), button_color=("#34384b", "#ececec"),
                                  font=("Segoe UI", 15, "bold"))]]
        if not search_bar:
            self.layout.pop(0)

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
                       [sg.Text("", key="error", visible=False, expand_y=True, background_color="#ececec",
                                text_color="Red")],
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
                if not valid_interval_text(text):
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
                        p = Project(self.values["projectname"].strip(), self.owners, self.groups,
                                    due_date=self.due_date,
                                    people=self.people, interval=self.interval)
                        self.close()
                        return p
        self.close()
        return None


def valid_interval_text(text):
    if len(text) == 1 and text in '+':
        return True
    else:
        try:
            number = float(text)
            return True
        except:
            return False


class DesktopGui:

    def __init__(self, firebase_key=None):
        # Fields
        self.max_reports = 6
        self.reports_row = 2
        self.displayed_project = None
        self.displayed_group = None
        # Temporary project edit values
        self.temp_owners = set()
        self.temp_people = set()
        self.temp_groups = set()
        self.temp_duedate_text = ""
        self.temp_duedates = []
        self.userfile = "users.json"
        self.export_file_types = ["CSV"]
        # if getattr(sys, 'frozen', False):
        #     self.userfile = os.path.join(sys._MEIPASS, self.userfile)

        self.icon = "img/manulife.ico"

        if platform == "darwin":
            self.icon = "img/manulife.icns"
        if getattr(sys, 'frozen', False):
            self.icon = os.path.join(sys._MEIPASS, self.icon)
        sg.set_options(icon=self.icon)

        # sg.theme('DarkGrey4')  # Add a touch of color
        sg.theme_add_new("Seen Theme", theme)
        sg.theme("Seen Theme")
        self.text_background_color = "#00a758"
        self.loggedIn = False
        self.user = None
        self.name = ""
        # Creating Database and loading the projects into it
        self.db = Database(firebase_key=firebase_key)
        self.db.load_all()
        # Checks on Start up if logged in already
        self.check_if_logged_in()

        # User Login Window
        self.login_popup_layout = [
            [sg.Text("Username:", size=8, background_color="#ececec", text_color="#34384b"),
             sg.Input(default_text="", do_not_clear=True, key="username", size=15, expand_x=True)],
            [sg.Text("Password:", size=8, background_color="#ececec", text_color="#34384b"),
             sg.Input(default_text="", key="password", size=15, password_char='*', expand_x=True)],
            [sg.Button("Login", size=6), sg.Button("Cancel", size=6), sg.Button("Create", size=6),
             sg.Checkbox("Stay Logged In?", default=True, key="staylogin", background_color="#ececec",
                         text_color="#34384b")]]

        self.choice = sg.Window('Login', self.login_popup_layout,
                                disable_close=False, return_keyboard_events=True, font=("Segoe UI", 13, ""),
                                background_color="#ececec")

        self.run_login()

        self.manage_project_preface = "manageproject"

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
             ProjectEditFrame()]]

        reports_button_padding = (1, 1)
        # Reports Tab
        self.reports_tab_layout = [
            [sg.Button('Save', size=6, pad=reports_button_padding),
             sg.Button("Submit", size=6, pad=reports_button_padding),
             sg.Combo(values=tuple(self.user.projects), default_value='None', readonly=False,
                      k='-COMBO-', enable_events=True, size=30),
             sg.Button('Latest', key="loadlatest", visible=False, size=6, pad=reports_button_padding),
             sg.Button("Export", key="export", visible=False, size=6, pad=reports_button_padding), ]
            , [

                sg.Text("Owner:", visible=False, key="owner", background_color="#ececec",
                        text_color="#34384b")

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
        self.tabs_layout = [
            [sg.Text(self.name, font=("Segoe UI", 20, "bold"), background_color="#34384b"),
             sg.Push(background_color="#34384b"),
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
                                  background_color="#ececec", key="projecttab"), GroupsPage(self.db)]],
                         enable_events=True,
                         key="tabs",
                         border_width=0,
                         focus_color="clear", background_color="#ececec",
                         tab_background_color="#ececec", selected_background_color="#c6c6c6",
                         selected_title_color="black", tab_border_width=0,
                         pad=(0, 0), expand_y=True, expand_x=True)]]

        # Main Page
        # self.window = sg.Window('Seen', self.tabs_layout, background_color="grey20", titlebar_text_color="black")
        self.window = sg.Window('Seen', self.tabs_layout, font=("Segoe UI", 15, ""), no_titlebar=False,
                                margins=(0, 0), icon=self.icon, resizable=True, finalize=True,
                                background_color="#34384b")
        self.window.set_min_size((627, 470))
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

            elif self.login_event == "Create":
                CreateNewUser(self.db).get()
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
                if self.displayed_project and self.values['projectstablist'][0] != self.displayed_project.project_name:
                    self.reset_temp_values()

                self.displayed_project = self.db.projects[self.values['projectstablist'][0]]

                self.set_temp_values()
                self.update_manage_projects()

            if self.event == 'Logout':
                self.window.close()
                self.logout()

            if self.event == "tabs":
                if self.values["tabs"] == "projecttab":
                    if self.displayed_project is not None:
                        self.set_temp_values()
                        self.update_manage_projects()
                if self.values["tabs"] == "reporttab":
                    if self.displayed_project is not None:
                        self.load_project_into_layout(self.displayed_project)

            # Reset temp values
            if self.values["tabs"] != "projecttab":
                self.reset_temp_values()

            if self.event == self.manage_project_preface + "remove":
                if self.displayed_project is not None:
                    if self.user.user_name in self.displayed_project.owner:
                        if YesNoPopup("Are you sure you want to remove:\n" + self.displayed_project.project_name).get():
                            self.remove_project(self.displayed_project)
                    else:
                        self.window[self.manage_project_preface + "error"].update(visible=True,
                                                                                  value="User is not owner",
                                                                                  text_color="red")

            elif self.event == self.manage_project_preface + "owners":
                if self.displayed_project:
                    self.temp_owners = set(ComboPopUp("Owners", list(self.db.users), list(self.temp_owners)).get())
                    if self.temp_owners:
                        self.window[self.manage_project_preface + "ownerstext"].update(
                            self.temp_owners.__str__().replace("{", "").replace("}", "").replace("'", ""),
                            text_color="#34384b")

            elif self.event == self.manage_project_preface + "people":
                if self.displayed_project:
                    self.temp_people = set(ComboPopUp("People", list(set(self.db.users) - self.displayed_project.owner),
                                                      list(set(self.temp_people) - self.displayed_project.owner)).get())

                    if self.temp_people:
                        self.window[self.manage_project_preface + "peopletext"].update(
                            self.temp_people.__str__().replace("{", "").replace("}", "").replace("'", ""),
                            text_color="#34384b")

            elif self.event == self.manage_project_preface + "groups":
                if self.displayed_project:
                    self.temp_groups = set(ComboPopUp("Groups", list(self.db.groups), list(self.temp_groups)).get())
                    if self.temp_groups:
                        self.window[self.manage_project_preface + "groupstext"].update(
                            self.temp_groups.__str__().replace("{", "").replace("}", "").replace("'", ""),
                            text_color="#34384b")

            elif self.event == self.manage_project_preface + 'interval':
                text = self.values[self.manage_project_preface + 'interval']
                if not valid_interval_text(text) or not self.displayed_project:
                    self.window[self.manage_project_preface + 'interval'].update(value=text[:-1])

            elif self.event == self.manage_project_preface + "date":
                if self.displayed_project:
                    DueDateEditor(self.displayed_project).run()
                    self.set_temp_values()
                    self.update_manage_projects()

            elif self.event == self.manage_project_preface + "create":
                if self.displayed_project:
                    self.apply_project_edits()

            elif self.event == "grouplist":
                self.update_group_page()

            elif self.event == "submittedproject":
                if self.window["grouplist"].get():
                    self.update_group_combos()

            elif self.event == "submittedreports":
                self.update_group_report_text()

            elif self.event == "creategroup":
                group = NewGroupPopUP(self.db).get()
                self.update_group_list()

            elif self.event == "export":
                file = ExportPopUp("Export as?", self.get_reports_as_csv(), icon=self.icon).get()

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
            text_background_color = "#ffffff"
            button_color = ("#ffffff", "#00a758")
            disabled = False
            if self.user.user_name not in self.displayed_project.owner:
                button_color = ("#34384b", "#b9b9b9")
                text_background_color = "#858585"
                disabled = True
            self.window["projectstablist"].set_value([self.displayed_project.project_name])
            self.window[self.manage_project_preface + "projectname"].update(value=self.displayed_project.project_name,
                                                                            disabled=disabled,
                                                                            background_color=text_background_color)
            self.window[self.manage_project_preface + "interval"].update(value=self.displayed_project.interval,
                                                                         disabled=disabled,
                                                                         background_color=text_background_color)
            self.window[self.manage_project_preface + "owners"].update(disabled=disabled,
                                                                       button_color=button_color,
                                                                       disabled_button_color=("#34384b", "#34384b"))
            self.window[self.manage_project_preface + "groups"].update(disabled=disabled,
                                                                       button_color=button_color,
                                                                       disabled_button_color=("#34384b", "#34384b"))
            self.window[self.manage_project_preface + "people"].update(disabled=disabled,
                                                                       button_color=button_color,
                                                                       disabled_button_color=("#34384b", "#34384b"))
            self.window[self.manage_project_preface + "date"].update(disabled=disabled,
                                                                     button_color=button_color,
                                                                     disabled_button_color=("#34384b", "#34384b"))
            # self.window[self.manage_project_preface + "create"].update(disabled=disabled,
            #                                                            button_color=button_color,
            #                                                            disabled_button_color=("#34384b", "#34384b"))

            self.window[self.manage_project_preface + "ownerstext"].update(
                self.temp_owners.__str__().replace("{", "").replace("}", "").replace("'", ""),
                text_color="#34384b")

            self.window[self.manage_project_preface + "groupstext"].update(
                self.temp_groups.__str__().replace("[", "").replace("]", "").replace("'", ""),
                text_color="#34384b")

            self.window[self.manage_project_preface + "peopletext"].update(
                self.temp_people.__str__().replace("{", "").replace("}", "").replace("'", ""),
                text_color="#34384b")

            self.window[self.manage_project_preface + "duedatetext"].update(
                self.temp_duedate_text.__str__().replace("{", "").replace("}", "").replace("'", ""),
                text_color="#34384b")

            self.window[self.manage_project_preface + "error"].update(visible=False)

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

        self.window["loadlatest"].update(visible=True)
        self.window["export"].update(visible=True)

        self.window["owner"].update(
            value="Owner: " + list(project.owner).__str__().replace("[", "").replace("]", "").replace("'", ""),
            visible=True)

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
        self.window[self.manage_project_preface + "error"].update(visible=False)
        self.window[self.manage_project_preface + "ownerstext"].update(value="")
        self.window[self.manage_project_preface + "groupstext"].update(value="")
        self.window[self.manage_project_preface + "peopletext"].update(value="")
        self.window[self.manage_project_preface + "duedatetext"].update(value="")
        self.reset_temp_values()

    def remove_project(self, project: Project):
        self.clear_manage_project()
        self.setup_reports()
        self.displayed_project = None
        self.db.remove_project(project)
        self.update_project_lists()

    def reset_temp_values(self):
        self.temp_groups = set()
        self.temp_people = set()
        self.temp_owners = set()
        self.temp_duedate_text = ""

    def set_temp_values(self):
        self.temp_people = self.displayed_project.people
        self.temp_owners = self.displayed_project.owner
        self.temp_groups = self.displayed_project.reports_to
        duedate = datetime.strptime(self.displayed_project.due_date[0], "%B-%d-%Y").strftime("%m/%d/%y")
        self.temp_duedate_text = duedate

    def get_updated_project_values(self):
        new_project_name = self.window[self.manage_project_preface + "projectname"].get().strip()
        new_owners = self.temp_owners
        new_groups = self.temp_groups
        new_people = self.temp_people
        new_interval = self.window[self.manage_project_preface + "interval"].get()
        new_project_dict = {"Name": new_project_name, "Owners": new_owners, "Groups": new_groups, "People": new_people,
                            "Interval": new_interval}
        return new_project_dict

    def apply_project_edits(self):
        updated_vals = self.get_updated_project_values()

        new = set(set(self.db.projects))
        new.remove(self.displayed_project.project_name)
        if updated_vals["Name"] == "" or updated_vals["Name"] in new:
            self.window[self.manage_project_preface + "error"].update(value="Project Name already exists", visible=True)
            return
        elif not updated_vals["Owners"]:
            self.window[self.manage_project_preface + "error"].update(value="Provide at least one owner", visible=True)
            return
        elif not updated_vals["Groups"]:
            self.window[self.manage_project_preface + "error"].update(value="Provide at least one group", visible=True)
            return
        elif updated_vals["Interval"] == "0":
            self.window[self.manage_project_preface + "error"].update(value="Interval cannot be 0", visible=True)
            return

        if YesNoPopup("Apply changes to:\n" + self.displayed_project.project_name).get():
            self.db.update_project(self.displayed_project, updated_vals)
            self.update_project_lists()

    def update_group_page(self):
        self.displayed_group = self.window["grouplist"].get()[0]
        if self.displayed_group:
            self.window["submittedproject"].update(visible=True,
                                                   values=self.db.get_projects_for_group(self.displayed_group))

            self.window["submittedreports"].update(visible=True)
            self.window["submittedtext"].update(visible=True)
            if self.window["submittedproject"].get():
                self.update_group_combos()

    def update_group_combos(self):
        group = self.displayed_group

        project = self.window["submittedproject"].get()
        reports = self.db.projects[project].get_sorted_reports()
        if group in reports:
            reports = [r[0] for r in reports[group]]

            self.window["submittedreports"].update(values=reports)
        else:
            self.window["submittedreports"].update(values=[])

        self.window["submittedtext"].update(value="")
        self.window["submittedbytext"].update(value="")

    def update_group_report_text(self):
        if self.window["submittedreports"].get():
            project = self.window["submittedproject"].get()
            report = self.db.projects[project].get_sorted_reports()
            index = self.window["submittedreports"].widget.current()
            self.window["submittedtext"].update(value=report[self.displayed_group][index][2])
            self.window["submittedbytext"].update(value=report[self.displayed_group][index][1])

    def update_group_list(self):
        self.window["grouplist"].update(list(self.db.groups))

    def get_reports_as_dict(self):
        report = {}
        for i in range(len(self.displayed_project.reports_to)):
            report[self.displayed_project.reports_to[i]] = self.values['report' + str(i)]
        return report

    def get_reports_as_csv(self):
        report = [[], []]
        report[0].extend(self.displayed_project.reports_to)
        for i in range(len(self.displayed_project.reports_to)):
            report[1].append(self.values['report' + str(i)])
        return report

# DesktopGui()
