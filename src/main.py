from Gui import DesktopGui
import PySimpleGUI as sg
import os


class GetKeyWindow(sg.Window):

    def __init__(self):
        self.layout = [
            [sg.Text("Select json file", background_color="#ececec", text_color="#34384b"),
             sg.Push(background_color="#ececec")],
            [sg.Input("", key="key", enable_events=True, expand_x=True, size=25),
             sg.FileBrowse(target="key", file_types=(("Json", ".json"),), button_color=("#ffffff", "#00a758"))],
            [sg.Button("Accept", button_color=("#ffffff", "#00a758"), expand_x=True),
             sg.Button("Cancel", button_color=("#ffffff", "#00a758"), expand_x=True)]]
        super().__init__("Select Firebase Key To Use", self.layout, font=("Segoe UI", 15, ""),
                         background_color="#ececec", element_justification="left")

    def run(self):
        while True:
            event, com_values = self.read()
            if event in (sg.WIN_CLOSED, 'Exit') or event == "Cancel":
                break

            elif event == "Accept":
                if self["key"].get() != "":
                    self.close()
                    return self["key"].get()
                else:
                    sg.PopupOK("Please Select a file", text_color="#34384b", font=("Segoe UI", 15, ""),
                               background_color="#ececec")

        self.close()
        return None


# Checks if there is a private key before launching the program
def check_for_key_in_directory() -> bool:
    if os.path.exists("private_key.json"):
        return True
    else:
        return False


def runner():
    val = None
    if not check_for_key_in_directory():
        val = GetKeyWindow().run()

    try:
        DesktopGui(val)
    except ValueError:
        sg.PopupError("Not a valid Firebase key", text_color="#34384b", font=("Segoe UI", 15, ""),
                      background_color="#ececec")
        runner()


if __name__ == '__main__':
    runner()
