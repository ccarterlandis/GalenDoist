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
    PLANNING_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "planning"), None)
    PLANNED_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "planned"), None)
    ASSIGNMENT_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "assignment"), None)
    DUE_LABEL_ID = next((label['id'] for label in LABELS if label['name'] == "due"), None)

class Task(TodoistMetadata):
    """Represents a Todoist task"""
    def __init__(self, task_data):
        self.task_id = task_data['id']
        self.display_content = task_data['content']
        self.content = task_data['content']
        self.project_id = task_data['project_id']
        self.project = next((project['name'] for project in self.PROJECTS if project['id'] == self.project_id), None)
        self.label_ids = task_data['label_ids']
        self.labels = [label['name'] for label in self.LABELS if label['id'] in self.label_ids]
        self.priority = task_data['priority']
        self.completed = task_data['completed']

        # if 'assignment' in self.labels:
        #     self.convert_to_section()
            # create work task 1
            # create work task 2
            # create work task 3

        try:
            self.due = task_data['due']
            if "planning" in self.labels:
                self.labels.remove("planning")
                self.label_ids.remove(self.PLANNING_LABEL_ID)

        except KeyError:
            self.due = None
            if self.project not in ("Wish List", "Shopping List", "Brussels Trip"):
                self.label_ids.append(self.PLANNING_LABEL_ID)

        try:
            self.due_time = parser.parse(task_data['due']['datetime'])
        except KeyError:
            self.due_time = None

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

class Project(TodoistMetadata):
    """Represents a Todoist project"""
    def __init__(self, project_id, name):
        self.project_id = project_id
        self.name = name
        self.raw_tasks = requests.get(
            "https://beta.todoist.com/API/v8/tasks",
            params={
                "project_id": self.project_id
            },
            headers={
                "Authorization": "Bearer %s" % self._API_TOKEN
            }).json()
        self.tasks = [Task(task) for task in self.raw_tasks]
        self.calendar = []
        self.events = []

META = TodoistMetadata()

ALL_PROJECTS = []

for project in META.PROJECTS:
    # if project['name'] != 'Honors Writing':
    ALL_PROJECTS.append(Project(project['id'], project['name']))

# ALL_PROJECTS.append(Project(META.PROJECTS[2]['id'], META.PROJECTS[2]['name'])) #brussels
# ALL_PROJECTS.append(Project(META.PROJECTS[9]['id'], META.PROJECTS[9]['name'])) #bio 1010
# ALL_PROJECTS.append(Project(META.PROJECTS[10]['id'], META.PROJECTS[10]['name'])) #bio 1020
# ALL_PROJECTS.append(Project(META.PROJECTS[17]['id'], META.PROJECTS[17]['name'])) #test project

# ALL_PROJECTS.append(Project(META.PROJECTS[11]['id'], META.PROJECTS[11]['name'])) #brussels
