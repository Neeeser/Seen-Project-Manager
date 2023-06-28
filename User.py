import pandas as pd


class User:

    def __init__(self, name: str, user_name: str, password: str):
        self.name = name
        self.projects = set()
        self.user_name = user_name
        self.password = password

    # Format user_name, name, projects {}, password
    def save_user(self, file="users.csv"):
        df = pd.read_csv(file)


def create_user_file():
    file = open("users.csv", "rw")
    df = pd.read_csv(file)
    df["user_name"] = ''
    df['name'] = ''
