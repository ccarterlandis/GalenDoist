from __future__ import print_function
# import datetime
import re
from dateutil import parser
import datetime as dt
import pickle
import os.path
import googleapiclient.errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from todoist import ALL_PROJECTS, META

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDS = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        CREDS = pickle.load(token)
if not CREDS or not CREDS.valid:
    if CREDS and CREDS.expired and CREDS.refresh_token:
        CREDS.refresh(Request())
    else:
        FLOW = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        CREDS = FLOW.run_local_server()
    with open('token.pickle', 'wb') as token:
        pickle.dump(CREDS, token)

API_SERVICE = build('calendar', 'v3', credentials=CREDS)

class GCalAPIHelper(object):
    """docstring for GCalAPIHelper"""
    def __init__(self, _api_service):
        self._api_service = _api_service
        self.PAGE_TOKEN = None
        self.MIN_ACCES_ROLE = "owner"
        self.CALENDAR_IDS = {}

        while True:
            self.CALENDAR_LIST = self._api_service.calendarList().list(pageToken=self.PAGE_TOKEN, minAccessRole=self.MIN_ACCES_ROLE).execute()
            for calendar in self.CALENDAR_LIST['items']:
                if calendar['summary'] in [project.name for project in ALL_PROJECTS]:
                    project = next((project for project in ALL_PROJECTS if project.name == calendar['summary']), None)
                    project.calendar = calendar
                    # print(calendar['id'], calendar['summary'])
                    self.CALENDAR_IDS[calendar['summary']] = calendar['id']

                    project.events = self.get_events_for_calendar(calendar['id'])
                    self.set_events(project)
                    project.events = self.get_events_for_calendar(calendar['id'])

            self.PAGE_TOKEN = self.CALENDAR_LIST.get('nextPageToken')
            if not self.PAGE_TOKEN:
                break

    def get_events_for_calendar(self, calendar_id):
        self.PAGE_TOKEN = None
        while True:
            events = self._api_service.events().list(calendarId=calendar_id, pageToken=self.PAGE_TOKEN).execute()
            self.PAGE_TOKEN = events.get('nextPageToken')
            if not self.PAGE_TOKEN:
                break
        return events

    def delete_events_for_completed_tasks(self, project):
        calendar_id = project.calendar['id']
        task_ids = [(task.task_id, task.labels, task.completed) for task in project.tasks]
        event_ids = [int(event['id']) for event in project.events['items'] if "(TD)" in event['summary']]
        for event_id in event_ids:
            event = next((task_id for task_id in task_ids if event_id == task_id[0]), None)
            if event is None:
                self._api_service.events().move(calendarId=calendar_id, eventId=event_id, destination='sb5qfi0odh2afrf2jf9rkng52g@group.calendar.google.com').execute()

    def create_event(self, task):
        event = {
            'id': f'{task.task_id}',
            'summary': f'{task.display_content}',
            'description': f'Auto-added by GalenDoist\nID: {task.task_id}\nProject: {task.project}\nPriority: {task.priority}\n'
        }

        # if task.due_time is not None:
        #     end_time = str(task.due['datetime'])
        #     start_time = re.sub(" ", "T", re.sub("\+.*", "Z", str(task.due_time - dt.timedelta(minutes=15))))

        #     event['start'] = {
        #         'dateTime': start_time,
        #         'timeZone': 'America/Los_Angeles',
        #     }
        #     event['end'] = {
        #         'dateTime': end_time,
        #         'timeZone': 'America/Los_Angeles',
        #     }
        if False:
            pass

        else: 
            event['start'] = {
                'date': task.due['date'],
                'timeZone': 'America/Los_Angeles',
            }
            event['end'] = {
                'date': task.due['date'],
                'timeZone': 'America/Los_Angeles',
            }

        return event


    def set_events(self, project):
        for task in [task for task in project.tasks if task.due is not None]:
            event = self.create_event(task)
            try:
                result = self._api_service.events().update(eventId=task.task_id, calendarId=f'{self.CALENDAR_IDS[task.project]}', body=event).execute()
                print(f'Updated event {task.task_id}: {task.display_content} in {task.project}')
            except googleapiclient.errors.HttpError as err:
                if err.resp.status in [404]:
                    result = self._api_service.events().insert(calendarId=f'{self.CALENDAR_IDS[task.project]}', body=event).execute()
                    print(f'Created event {task.task_id}: {task.display_content} in {task.project}')
                else:
                    print(err)

        self.delete_events_for_completed_tasks(project)

GCalAPIHelper(API_SERVICE)
