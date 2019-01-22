import requests
import pprint

pp = pprint.PrettyPrinter(indent=4)

class TodoistMetadata():
    """Holds all Todoist API data, such as projects, tasks, and labels"""

    _api_token = '7681246d1735eb4a1b85d3d23ca50d5ba9c2ac0a'
    projects = requests.get("https://beta.todoist.com/API/v8/projects", headers={"Authorization": "Bearer %s" % '7681246d1735eb4a1b85d3d23ca50d5ba9c2ac0a'}).json()
    labels = requests.get("https://beta.todoist.com/API/v8/labels", headers={"Authorization": "Bearer %s" % _api_token}).json()

class Task(TodoistMetadata):
    """Represents a Todoist task"""
    def __init__(self, task):
        # super(Task, self).__init__()
        self.content = task['content']
        self.project_id = task['project_id']
        self.project = next((project['name'] for project in self.projects if project['id'] == self.project_id), None)
        self.label_ids = task['label_ids']
        self.labels = [label['name'] for label in self.labels if label['id'] in self.label_ids]

        try:
            self.due = task['due']
        except KeyError as error:
            self.due = None

class Project(TodoistMetadata):
    """Represents a Todoist project"""
    def __init__(self, ID, name):
        # super(Project, self).__init__()
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

meta = TodoistMetadata()

all_projects = []

for project in meta.projects:
    all_projects.append(Project(project['id'], project['name']))

# all_projects.append(Project(meta.projects[15]['id'], meta.projects[15]['name']))

for project in all_projects:
    for task in project.tasks:
        print(f"Task: {task.content}\nProject: {task.project}\nLabels: {task.labels}\nDue: {task.due}\n----------------------------------")
