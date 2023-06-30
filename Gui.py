import PySimpleGUI as sg
from Database import Database
from Project import Project

# All the stuff inside your window.
alayout = [[sg.Text('Some text on Row 1')],
           [sg.Text('Enter something on Row 2'), sg.InputText()],
           [sg.Button('Ok'), sg.Button('Cancel')]]

menu_def = [['&Application', ['E&xit']],
            ['&Help', ['&About']]]
layout = [[sg.MenubarCustom(menu_def, key='-MENU-', font='Courier 15', tearoff=True)],
          [sg.Text('Demo Of (Almost) All Elements', size=(38, 1), justification='center', font=("Helvetica", 16),
                   relief=sg.RELIEF_RIDGE, k='-TEXT HEADING-', enable_events=True)]]

layout += [[sg.TabGroup([[sg.Tab('Input Elements', alayout),
                          sg.Tab('Asthetic Elements', [])]], key='-TAB GROUP-', expand_x=True, expand_y=True),

            ]]


class DesktopGui:

    def __init__(self):
        ### Fields
        self.max_reports = 6
        self.reports_row = 2
        self.displayed_project = None

        ### Creating Database and loading the projects into it
        self.db = Database()
        self.db.load_all_projects()

        ### Sets up the layout of the page
        self.layout = [[sg.Button('Submit'), sg.Button('Exit')],
                       [sg.Combo(values=tuple(self.db.projects.keys()), default_value='None', readonly=False,
                                 k='-COMBO-', enable_events=True, size=30)
                           , sg.Text("Project:", visible=False), sg.Text("Owner:", visible=False)]]
        self.setup_reports()

        sg.theme('BlueMono')  # Add a touch of color
        # self.load_projects_into_layout()
        self.window = sg.Window('My new window', self.layout)

    def run(self):
        while True:  # Event Loop
            self.event, self.values = self.window.read()

            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self.event == 'Submit':
                self.submit_report()

            if self.event == '-COMBO-':
                self.displayed_project = self.db.projects[self.values['-COMBO-']]
                self.load_project_into_layout(self.displayed_project)
        self.window.close()

    def setup_reports(self):
        temp_layout = [[], []]
        for i in range(self.max_reports):
            temp_layout[0].append(sg.Text("NOT DEFINED", visible=False, pad=(1, 0), expand_x=True))
            temp_layout[1].append(
                sg.Multiline('', size=(10, 10), expand_x=True, expand_y=True, k='report' + str(i),
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
