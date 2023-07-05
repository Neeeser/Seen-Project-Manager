import time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
from User import User
from Project import Project
from Group import Group


def load_json_info(root, filename):
    with open(filename, "r") as file:
        file_contents = json.load(file)
    root.set(file_contents)


firebase_address = "seenworkflow_private_key.json"

cred = credentials.Certificate(firebase_address)
firebase_admin.initialize_app(cred, {'databaseURL': "https://seenworkflow-default-rtdb.firebaseio.com/"})
root = db.reference('root')
users = db.reference('root/users')

# u = User("Parag Mehta", "parag", un_hashed_password="123", projects=["Seen Workflow", "Muni SMA"]).save_user()
# p = Project("Seen WorkFlow", ["Andrew", "Parag"], ["Parag", "GWAM"]).save_project()
Group("GWAM", ["parag"]).save_group()
