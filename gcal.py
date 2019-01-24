from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from todoist import ALL_PROJECTS

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server()
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

# Call the Calendar API

page_token = None
min_access_role = "owner"
calendar_ids = {}
while True:
    calendar_list = service.calendarList().list(pageToken=page_token, minAccessRole=min_access_role).execute()
    for calendar in calendar_list['items']:
        calendar_ids[calendar['summary']] = calendar['id']
        # print(calendar['id'])
    page_token = calendar_list.get('nextPageToken')
    if not page_token:
        break

for project in ALL_PROJECTS:
    for task in project.tasks:
        if task.due is not None:
            event = {
              'summary': f'{task.content}',
              'start': {
                'dateTime': '2019-01-23T16:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
              },
              'end': {
                'dateTime': '2019-01-23T17:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
              }
            }

            event = service.events().insert(calendarId=f'{calendar_ids[task.project]}', body=event).execute()


# now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
# print('Getting the upcoming 10 events')
# events_result = service.events().list(calendarId='primary', timeMin=now,
#                                     maxResults=10, singleEvents=True,
#                                     orderBy='startTime').execute()
# events = events_result.get('items', [])

# if not events:
#     print('No upcoming events found.')
# for event in events:
#     start = event['start'].get('dateTime', event['start'].get('date'))
#     print(start, event['summary'])
