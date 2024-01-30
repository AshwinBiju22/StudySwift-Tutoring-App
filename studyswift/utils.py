from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mysite.settings import GOOGLE_CALENDAR_API_CREDENTIALS_FILE,GOOGLE_CALENDAR_API_SCOPES,GOOGLE_CALENDAR_API_TOKEN_FILE

def get_calendar_service():
    credentials = Credentials.from_authorized_user_file(
        GOOGLE_CALENDAR_API_CREDENTIALS_FILE,
        GOOGLE_CALENDAR_API_SCOPES,
    )

    if credentials.expired:
        flow = InstalledAppFlow.from_client_secrets_file(
            GOOGLE_CALENDAR_API_CREDENTIALS_FILE,
            GOOGLE_CALENDAR_API_SCOPES,
        )
        credentials = flow.run_local_server(port=0)

    with open(GOOGLE_CALENDAR_API_TOKEN_FILE, 'w') as token_file:
        token_file.write(credentials.to_json())

    return build('calendar', 'v3', credentials=credentials)
