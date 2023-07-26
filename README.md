# Seen

Seen is a firebase project management tool that allows you to create and manage projects using firebase as a
backend.

## Features:

- Create and manage projects with firebase authentication and database
- Edit project information such as due dates, owners, members, name, and groups
- Submit reports on due dates and track progress
- Automatic due date updating based on report submissions
- Set up recurring due dates for reports with custom intervals

## How to run the project

1. Clone or download the repository from Github
2. Get a firebase private key
    1. [Generate Database Key](https://firebase.google.com/docs/admin/setup#:~:text=To%20generate%20a%20private%20key%20file%20for%20your,Securely%20store%20the%20JSON%20file%20containing%20the%20key.)
    2. Rename firebase json to ```private_key.json``` and place in root directory
    3. Or enter the key in the window upon application start
3. Install requirements
    1. ```pip install -r requirements.txt```
4. Run the project from ```main.py```

## How to compile to executable

1. Install requirements
    1. ```pip install -r requirements.txt```
2. Put the firebase key json in ```/```
3. Run ```compiler.py```
4. Open executable in ```dist/Seen```