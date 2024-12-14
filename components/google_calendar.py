import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

class GoogleCalendarIntegration:
    def __init__(self, root):
        self.root = root
        self.root['background'] = '#ffdfba'
        self.root.minsize(width=1280, height=950)
        self.service = self.authenticate_google_calendar()
        self.create_ui()

    def authenticate_google_calendar(self):
        '''Authenticate and return the Google Calendar API service.'''
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return build('calendar', 'v3', credentials=creds)

    def create_ui(self):
        '''Create the Google Calendar integration UI.'''
        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#ffdfba')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffa07a', relief='solid', font=('Arial', 18), width=20)

        home_button = ttk.Button(self.root, text='Home', style='Custom.TButton', command=self.return_to_home).pack(anchor=tk.NW, padx=30, pady=30)

        # Split UI into left and right frames
        self.left_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.left_frame.pack(side="left", fill="y", padx=30, pady=30)

        self.right_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        ttk.Label(self.left_frame, text="Google Calendar Integration", background='#ffdfba', font=("Arial", 24)).pack(pady=20)

        ttk.Button(self.left_frame, text="Fetch Events", style='Custom.TButton', command=self.fetch_events).pack(pady=10)
        ttk.Button(self.left_frame, text="Add Event", style='Custom.TButton', command=self.add_event).pack(pady=10)
        ttk.Button(self.left_frame, text="Delete Event", style='Custom.TButton', command=self.delete_event).pack(pady=10)

        # Event List
        self.event_tree = ttk.Treeview(self.right_frame, columns=("ID", "Summary", "Start", "End"), show="headings")
        self.event_tree.heading("ID", text="ID")
        self.event_tree.heading("Summary", text="Summary")
        self.event_tree.heading("Start", text="Start Time")
        self.event_tree.heading("End", text="End Time")
        self.event_tree.column("ID", width=100, stretch=tk.NO)
        self.event_tree.pack(expand=True, fill="both", pady=10)

        self.load_events()

    def return_to_home(self):
        '''Return to the home screen.'''
        from main import SmartClockApp
        self.root.destroy()
        root = tk.Tk()
        SmartClockApp(root)
        root.mainloop()

    def load_events(self):
        '''Load events from Google Calendar.'''
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                       maxResults=10, singleEvents=True,
                                                       orderBy='startTime').execute()
            events = events_result.get('items', [])

            for event in self.event_tree.get_children():
                self.event_tree.delete(event)

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                self.event_tree.insert("", "end", values=(event['id'], event['summary'], start, end))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load events: {e}")

    def fetch_events(self):
        '''Fetch events from Google Calendar.'''
        self.load_events()
        messagebox.showinfo("Success", "Events fetched successfully!")

    def add_event(self):
        '''Add a new event to Google Calendar.'''
        def save_event():
            summary = summary_var.get()
            start_time = start_var.get()
            end_time = end_var.get()

            try:
                event = {
                    'summary': summary,
                    'start': {
                        'dateTime': start_time,
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'dateTime': end_time,
                        'timeZone': 'UTC',
                    },
                }
                self.service.events().insert(calendarId='primary', body=event).execute()
                add_event_window.destroy()
                self.load_events()
                messagebox.showinfo("Success", "Event added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add event: {e}")

        add_event_window = tk.Toplevel(self.root)
        add_event_window.title("Add Event")
        add_event_window.geometry("400x300")

        summary_var = tk.StringVar()
        start_var = tk.StringVar()
        end_var = tk.StringVar()

        ttk.Label(add_event_window, text="Summary:").pack(pady=5)
        ttk.Entry(add_event_window, textvariable=summary_var).pack(pady=5)

        ttk.Label(add_event_window, text="Start Time (YYYY-MM-DDTHH:MM:SS):").pack(pady=5)
        ttk.Entry(add_event_window, textvariable=start_var).pack(pady=5)

        ttk.Label(add_event_window, text="End Time (YYYY-MM-DDTHH:MM:SS):").pack(pady=5)
        ttk.Entry(add_event_window, textvariable=end_var).pack(pady=5)

        ttk.Button(add_event_window, text="Save", command=save_event).pack(pady=10)

    def delete_event(self):
        '''Delete an event from Google Calendar.'''
        selected_item = self.event_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an event to delete.")
            return

        event_id = self.event_tree.item(selected_item)['values'][0]

        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            self.load_events()
            messagebox.showinfo("Success", "Event deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete event: {e}")