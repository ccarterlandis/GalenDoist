import logging
import pprint
import requests

pp = pprint.PrettyPrinter(indent=4)

# logging = logging.logger()

class TodoistMetadata():
    """Holds all Todoist API data, such as projects, tasks, and labels"""

    _api_token = '7681246d1735eb4a1b85d3d23ca50d5ba9c2ac0a'
    projects = requests.get("https://beta.todoist.com/API/v8/projects", headers={"Authorization": "Bearer %s" % '7681246d1735eb4a1b85d3d23ca50d5ba9c2ac0a'}).json()
    labels = requests.get("https://beta.todoist.com/API/v8/labels", headers={"Authorization": "Bearer %s" % _api_token}).json()

class Task(TodoistMetadata):
    """Represents a Todoist task"""
    def __init__(self, task_data):
        self.content = task_data['content']
        self.project_id = task_data['project_id']
        self.project = next((project['name'] for project in self.projects if project['id'] == self.project_id), None)
        self.label_ids = task_data['label_ids']
        self.labels = [label['name'] for label in self.labels if label['id'] in self.label_ids]
        try:
            self.due = task_data['due']
        except KeyError:
            self.due = None

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
                "Authorization": "Bearer %s" % self._api_token
            }).json()

        self.tasks = [Task(task) for task in self.raw_tasks]

META = TodoistMetadata()

ALL_PROJECTS = []

for project in META.projects:
    ALL_PROJECTS.append(Project(project['id'], project['name']))

# ALL_PROJECTS.append(Project(META.projects[15]['id'], META.projects[15]['name']))

for project in ALL_PROJECTS:
    for task in project.tasks:
        print(f"Task: {task.content}\nProject: {task.project}\nLabels: {task.labels}\nDue: {task.due}\n----------------------------------")
