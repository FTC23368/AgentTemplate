from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR
import re
from zoneinfo import ZoneInfo

class AppointmentScheduler:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.creds = None
        self.TIMEZONE = 'America/Los_Angeles'
        self.service = self.setup_google_calendar()
        self.available_slots = []
        
    def setup_google_calendar(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
                
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
                
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
                
        return build('calendar', 'v3', credentials=self.creds)

    def get_available_slots(self):
        # Get next 5 business days
        start_date = datetime.now()
        business_days = list(rrule(
            DAILY, 
            count=5, 
            byweekday=(MO, TU, WE, TH, FR),
            dtstart=start_date
        ))
        
        self.available_slots = []
        
        for day in business_days:
            # Set working hours (9 AM to 5 PM)
            day_start = day.replace(hour=9, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=17, minute=0, second=0, microsecond=0)
            
            # Add timezone info to the datetime objects
            day_start = day_start.astimezone(ZoneInfo(self.TIMEZONE))
            day_end = day_end.astimezone(ZoneInfo(self.TIMEZONE))
            
            # Get existing events
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=day_start.isoformat(),  # Removed 'Z' suffix
                timeMax=day_end.isoformat(),    # Removed 'Z' suffix
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
            # Create 1-hour slots and check availability
            current_slot = day_start
            while current_slot < day_end:
                slot_end = current_slot + timedelta(hours=1)
                is_available = True
                
                for event in events:
                    event_start = parse(event['start'].get('dateTime', event['start'].get('date'))).astimezone(ZoneInfo(self.TIMEZONE))
                    event_end = parse(event['end'].get('dateTime', event['end'].get('date'))).astimezone(ZoneInfo(self.TIMEZONE))
                    
                    if (current_slot < event_end and slot_end > event_start):
                        is_available = False
                        break
                
                if is_available:
                    self.available_slots.append(current_slot)
                    
                current_slot = slot_end
                
        return self.available_slots

    def schedule_appointment(self, slot_datetime, user_email):
        event = {
            'summary': 'Appointment',
            'start': {
                'dateTime': slot_datetime.isoformat(),
                'timeZone': self.TIMEZONE,
            },
            'end': {
                'dateTime': (slot_datetime + timedelta(hours=1)).isoformat(),
                'timeZone': self.TIMEZONE,
            },
            'attendees': [
                {'email': user_email},
            ],
        }

        event = self.service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'
        ).execute()
        
        return event

def handle_appointment_request():
    scheduler = AppointmentScheduler()
    
    # Get available slots
    available_slots = scheduler.get_available_slots()
    
    if not available_slots:
        return "Sorry, there are no available slots in the next 5 business days."
    
    # Format slots for display
    formatted_slots = []
    for slot in available_slots:
        formatted_slots.append(slot.strftime("%A, %B %d %Y at %I:%M %p"))
    
    return formatted_slots

def book_appointment(selected_slot, user_email):
    # Validate email
    print(f"{user_email=}, {selected_slot}")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
        return "Invalid email address"

    scheduler = AppointmentScheduler()
    try:
        # Add current year to the datetime parsing
        current_year = datetime.now().year
        slot_datetime = datetime.strptime(f"{selected_slot}", "%Y-%m-%d %H:%M:%S")
        
        # If the parsed date is in the past, it's probably for next year
        if slot_datetime < datetime.now():
            slot_datetime = slot_datetime.replace(year=current_year + 1)
            
        event = scheduler.schedule_appointment(slot_datetime, user_email)
        return f"Your appointment is confirmed for {selected_slot}. A calendar invite has been sent to {user_email}. Curious to know the next steps?"
    except Exception as e:
        return f"Error scheduling appointment: {str(e)}"

