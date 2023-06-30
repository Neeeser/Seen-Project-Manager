import PySimpleGUI as sg
from Database import Database

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
                                 k='-COMBO-', enable_events=True)
                           , sg.Text("project.owner"), sg.Text("project.project_name")]]
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
                self.button_go()
                # self.layout[3][2].update(visible=not self.layout[3][2].visible)

            if self.event == '-COMBO-':
                self.displayed_project = self.db.projects[self.values['-COMBO-']]

        self.window.close()

    def setup_reports(self):
        temp_layout = [[], []]
        for i in range(self.max_reports):
            temp_layout[0].append(sg.Text("NOT DEFINED", visible=False, pad=(50, 0)))
            temp_layout[1].append(
                sg.Multiline('Insert report here', size=(10, 5), expand_x=True, expand_y=True, k='report' + str(i),
                             visible=True))
        self.layout.insert(self.reports_row, temp_layout)

    def button_go(self):
        sg.popup('Go button clicked', 'Input value:', self.values['report0'])

    def load_project_into_layout(self):
        for project in self.db.projects:
            project = self.db.projects[project]
            

DesktopGui().run()
