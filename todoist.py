import pprint
import uuid
import json
from dateutil import parser
import requests

pp = pprint.PrettyPrinter(indent=4)

class TodoistMetadata():
    """Holds all Todoist API data, such as projects, tasks, and labels"""
    _API_TOKEN = '7681246d1735eb4a1b85d3d23ca50d5ba9c2ac0a'
    PROJECTS = requests.get("https://beta.todoist.com/API/v8/projects", headers={"Authorization": "Bearer %s" % '7681246d1735eb4a1b85d3d23ca50d5ba9c2ac0a'}).json()
    LABELS = requests.get("https://beta.todoist.com/API/v8/labels", headers={"Authorization": "Bearer %s" % _API_TOKEN}).json()
    PLANNING_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "planning"))

class Task(TodoistMetadata):
    """Represents a Todoist task"""
    def __init__(self, task_data):
        self.task_id = task_data['id']
        self.content = task_data['content']
        self.project_id = task_data['project_id']
        self.project = next((project['name'] for project in self.PROJECTS if project['id'] == self.project_id), None)
        self.label_ids = task_data['label_ids']
        self.labels = [label['name'] for label in self.LABELS if label['id'] in self.label_ids]

        try:
            self.due = task_data['due']
            if "planning" in self.labels:
                self.labels.remove("planning")
                self.label_ids.remove(self.PLANNING_LABEL_ID)
                self.update_task()

        except KeyError:
            self.due = None
            if self.project not in ("Wish List", "Shopping List", "Brussels Trip"):
                self.label_ids.append(self.PLANNING_LABEL_ID)
                self.update_task()

        try:
            self.due_time = parser.parse(task_data['due']['datetime'])
        except KeyError:
            self.due_time = None

    def update_task(self):
        requests.post(
            f"https://beta.todoist.com/API/v8/tasks/{self.task_id}",
            data=json.dumps({
                "label_ids": self.label_ids
            }),
            headers={
                "Content-Type": "application/json",
                "X-Request-Id": str(uuid.uuid4()),
                "Authorization": "Bearer %s" % self._API_TOKEN
            })

class Project(TodoistMetadata):
    """Represents a Todoist project"""
    def __init__(self, ID, name):
        self.ID = ID
        self.name = name
        self.raw_tasks = requests.get(
            "https://beta.todoist.com/API/v8/tasks",
            params={
                "project_id": self.ID
            },
            headers={
                "Authorization": "Bearer %s" % self._API_TOKEN
            }).json()
        self.tasks = [Task(task) for task in self.raw_tasks]

META = TodoistMetadata()

ALL_PROJECTS = []

# for project in META.PROJECTS:
#     ALL_PROJECTS.append(Project(project['id'], project['name']))

ALL_PROJECTS.append(Project(META.PROJECTS[9]['id'], META.PROJECTS[9]['name']))

# for project in ALL_PROJECTS:
#     for task in project.tasks:
#         if "planning" in task.labels:
#             print(f"Task: {task.content}\nProject: {task.project}\nLabels: {task.labels}\nDue: {task.due}\n----------------------------------")
