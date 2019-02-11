import time
import uuid
import json
from dateutil import parser
import datetime as dt
import requests
from todoist.api import TodoistAPI

import pprint
pp = pprint.PrettyPrinter()

class TodoistMetadata():
    """Holds all Todoist API data, such as projects, tasks, and labels"""
    _API_TOKEN = '7681246d1735eb4a1b85d3d23ca50d5ba9c2ac0a'
    PROJECTS = requests.get("https://beta.todoist.com/API/v8/projects", headers={"Authorization": "Bearer %s" % _API_TOKEN}).json()
    TASKS = requests.get("https://beta.todoist.com/API/v8/tasks", headers={"Authorization": "Bearer %s" % _API_TOKEN}).json()
    LABELS = requests.get("https://beta.todoist.com/API/v8/labels", headers={"Authorization": "Bearer %s" % _API_TOKEN}).json()
    PLANNING_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "planning"), None)
    PLANNED_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "planned"), None)
    ASSIGNMENT_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "assignment"), None)
    DUE_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "due"), None)
    DONT_SYNC_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "ds"), None)

    API = TodoistAPI(_API_TOKEN)
    # print(API.sync_token)
    UPDATED_TASKS = API.sync()['items']
    # print(API.sync_token)
    pp.pprint(UPDATED_TASKS)

    time.sleep(1.5)

    print(API.sync_token)
    pp.pprint(API.sync()['items'])
    print(API.sync_token)

class Task(TodoistMetadata):
    """Represents a Todoist task"""
    def __init__(self, task_data):
        # self.raw_task_data = requests.get(
        # f"https://beta.todoist.com/API/v8/tasks/{task_id}",
        # headers={
        #     "Authorization": "Bearer %s" % self._API_TOKEN
        # }).json()

        self.task_id = task_data['id']
        self.display_content = task_data['content']
        self.content = task_data['content']
        self.project_id = task_data['project_id']
        self.project = next((project['name'] for project in self.PROJECTS if project['id'] == self.project_id), None)
        self.label_ids = task_data['labels']
        self.labels = [label['name'] for label in self.LABELS if label['id'] in self.label_ids]
        self.priority = task_data['priority']

        if task_data['checked'] == 1:
            self.completed = True
        else:
            self.completed = False

        if task_data['is_deleted'] == 1:
            self.deleted = True
        else:
            self.deleted = False

        if task_data['is_archived'] == 1:
            self.archived = True
        else:
            self.archived = False

        if task_data['is_deleted'] == 1:
            self.deleted = True
        else:
            self.deleted = False

        if task_data['due'] is not None:
            self.due = task_data['due']
            self.due_string = parser.parse(task_data['due']['date'])
            self.due_date = f'{self.due_string.year}-{self.due_string.month}-{self.due_string.day}'
            if "planning" in self.labels:
                print("Removing planning label from task " + str(self.task_id) + ": " + self.content)
                self.labels.remove("planning")
                self.label_ids.remove(self.PLANNING_LABEL_ID)

        else:
            self.due = None
            if self.project not in ("Wish List", "Shopping List"):
                print("Adding planning label to task " + str(self.task_id) + ": " + self.content)
                self.label_ids.append(self.PLANNING_LABEL_ID)

        if 'assignment' in self.labels and 'planned' not in self.labels:
            if not self.deleted and not self.archived and not self.completed:
                self.create_assignment_task(1)
                self.create_assignment_task(2)
                self.create_assignment_task(3)
                self.label_ids.append(self.PLANNED_LABEL_ID)

        self.format_for_display()
        self.update_task()

    def convert_to_section(self):
        if self.content[len(self.content)-1] != ':':
            self.content += ':'
            self.update_task()

    def convert_to_task(self):
        if self.content[len(self.content)-1] == ':':
            self.content = self.content[0:len(self.content)-1]

    def format_for_display(self):
        if self.content[len(self.content)-1] == ':':
            self.display_content = self.content[0:len(self.content)-1]
        self.display_content += " (TD)"

    def update_task(self):
        requests.post(
            f"https://beta.todoist.com/API/v8/tasks/{self.task_id}",
            data=json.dumps({
                "content": self.content,
                "label_ids": self.label_ids
            }),
            headers={
                "Content-Type": "application/json",
                "X-Request-Id": str(uuid.uuid4()),
                "Authorization": "Bearer %s" % self._API_TOKEN
            })

    def create_assignment_task(self, offset):
        new_date = str((dt.datetime.strptime(self.due_date, "%Y-%m-%d") - dt.timedelta(days=offset)).date())
        self.label_ids.remove(self.ASSIGNMENT_LABEL_ID)
        print(requests.post(
            "https://beta.todoist.com/API/v8/tasks",
            data=json.dumps({
                "content": "Work on " + self.content,
                "project_id": self.project_id,
                "label_ids": self.label_ids,
                "due_string": new_date
            }),
            headers={
                "Content-Type": "application/json",
                "X-Request-Id": str(uuid.uuid4()),
                "Authorization": "Bearer %s" % self._API_TOKEN
            }))
        self.label_ids.append(self.ASSIGNMENT_LABEL_ID)

class Project(TodoistMetadata):
    """Represents a Todoist project"""
    def __init__(self, project_id, project_name):
        self.project_id = project_id
        self.project_name = project_name
        self.updated_tasks = [Task(updated_task) for updated_task in self.UPDATED_TASKS if int(updated_task['project_id']) == int(self.project_id)]
        self.calendar = []
        self.events = []
