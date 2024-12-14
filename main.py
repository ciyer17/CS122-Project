import tkinter as tk
from tkinter import ttk
from time import strftime
from components import TaskManager
from components import PomodoroTimer
from components import SimpleTimers
from components import SleepLogger
from components import HabitTracker
from components import GoogleCalendarIntegration
import threading
import time
from plyer import notification
import sqlite3
import os
import webbrowser


class SmartClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity & Wellness Clock")
        self.root.geometry("1280x720")
        self.root['background'] = '#5cffa5'
        self.setup_background_tasks()

        self.root.minsize(width=1280, height=550)
        self.show_home()

    def clear_window(self):
        '''Clear all widgets in the window'''
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_home(self):
        '''Show the home screen'''
        self.clear_window()
        ttk.Label(self.root, text="Select what you would like to do", background='#5cffa5', font=("Arial", 24)).pack(pady=20)

        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#5cffa5')

        main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        # When window is expanded, expand the frame to fill the window on both sides, and center the frame
        main_frame.pack(anchor=tk.CENTER, expand=True, fill='both')

        clock_label = ttk.Label(main_frame, background='#5cffa5', font=("Arial", 48))
        clock_label.pack(pady=20)
        self.update_clock(clock_label)

        # Set up the button_frame using grid layout instead of pack
        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(pady=100, anchor=tk.CENTER, expand=True)

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        # Add buttons to the grid layout
        ttk.Button(button_frame, text="Pomodoro Timer", style='Custom.TButton', command=self.show_pomodoro).grid(row=0, column=0, padx=20, pady=10)
        ttk.Button(button_frame, text="Simple Timers", style='Custom.TButton', command=self.show_timer).grid(row=0, column=1, padx=20, pady=10)
        ttk.Button(button_frame, text="Sleep Logger", style='Custom.TButton', command=self.show_sleep_logger).grid(row=0, column=2, padx=20, pady=10)
        ttk.Button(button_frame, text="Tasks", style='Custom.TButton', command=self.show_task_addition).grid(row=1, column=0, padx=20, pady=10)
        ttk.Button(button_frame, text="Google Calendar", style='Custom.TButton', command=self.show_google_calendar).grid(row=1, column=1, padx=20, pady=10)
        ttk.Button(button_frame, text="Habit Tracker", style='Custom.TButton', command=self.show_habit_tracker).grid(row=1, column=2, padx=20, pady=10, columnspan=3)

        survey = ttk.Button(self.root, text="Survey", style='Custom.TButton', command=self.open_survey)
        survey.place(relx=0, rely=1, anchor='sw')

        # Create and place the second button in the lower-right corner
        bugs = ttk.Button(self.root, text="Report Issues", style='Custom.TButton', command=self.open_bugs)
        bugs.place(relx=1, rely=1, anchor='se')

        # Center the main_frame widget by aligning it to 50% of the width and height.
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def open_survey(self):
        webbrowser.open("https://forms.gle/GKMX5ZhE7xJ8c1y99")

    def open_bugs(self):
        webbrowser.open("https://github.com/ciyer17/CS122-Project/issues")
        
    def update_clock(self, clock_label):
        '''Update the clock every second'''

        if clock_label.winfo_exists():
            current_time = strftime("%I:%M:%S %p") # 12-hour format
            clock_label.config(text=current_time)
            self.root.after(1000, lambda: self.update_clock(clock_label))

    def show_pomodoro(self):
        '''Show the pomodoro screen'''

        self.clear_window()
        PomodoroTimer(self.root)

    def show_timer(self):
        '''Show the simple timers screen'''

        self.clear_window()
        SimpleTimers(self.root)

    def show_sleep_logger(self):
        '''Show the sleep logger screen'''

        self.clear_window()
        SleepLogger(self.root)

    def show_task_addition(self):
        '''Show the task management screen'''

        self.clear_window()
        TaskManager(self.root)

    def show_google_calendar(self):
         '''Show the Google Calendar screen'''

         self.clear_window()
         GoogleCalendarIntegration(self.root)

    def show_habit_tracker(self):
        '''Show the habit tracker screen'''
        self.clear_window()
        HabitTracker(self.root)

    def setup_background_tasks(self):
        '''Set up background tasks for notifications'''
        threading.Thread(target=self.water_reminder, daemon=True).start()
        threading.Thread(target=self.stretch_reminder, daemon=True).start()
        threading.Thread(target=self.sleep_checker, daemon=True).start()

    def water_reminder(self):
        '''Notify the user every hour to drink water'''
        while True:
            time.sleep(3600)  # Wait for 1 hour
            notification.notify(
                title="Hydration Reminder",
                message="Time to drink some water!",
                timeout=10
            )

    def stretch_reminder(self):
        '''Notify the user every 30 minutes to stretch'''
        while True:
            time.sleep(1800)  # Wait for 30 minutes
            notification.notify(
                title="Stretch Reminder",
                message="Time to stretch!",
                timeout=10
            )

    def sleep_checker(self):
        '''Check the latest sleep log and notify if less than 8 hours'''
        db_path = "data/sleep_logger.db"
        while True:
            time.sleep(86400)  # Check once a day
            try:
                db_dir = os.path.join(os.getcwd(), "data")
                conn = sqlite3.connect(f"{db_dir}/tasks.db")
                cursor = conn.cursor()
                cursor.execute("SELECT hours_slept FROM sleep_logs ORDER BY date DESC LIMIT 1")
                result = cursor.fetchone()
                conn.close()
                if result and result[0] < 8:
                    notification.notify(
                        title="Sleep Reminder",
                        message="You slept less than 8 hours last night. Aim for at least 8 hours of sleep!",
                        timeout=10
                    )
            except Exception as e:
                print(f"Error checking sleep data: {e}")
                return

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartClockApp(root)
    root.mainloop()
