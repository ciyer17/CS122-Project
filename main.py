import tkinter as tk
from tkinter import ttk
from time import strftime
from components import TaskManager
from components import PomodoroTimer
from components import SimpleTimers
from components import SleepLogger
# from components import *

class SmartClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity & Wellness Clock")
        self.root.geometry("1280x720")
        self.root['background'] = '#5cffa5'

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

        button_frame = ttk.Frame(main_frame, style='Custom.TFrame', )
        button_frame.pack(pady=100, anchor=tk.CENTER, expand=True, fill='both')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        ttk.Button(button_frame, text="Pomodoro Timer", style='Custom.TButton', command=self.show_pomodoro).pack(side=tk.LEFT, padx=20)
        ttk.Button(button_frame, text="Simple Timers", style='Custom.TButton', command=self.show_timer).pack(side=tk.LEFT,padx=20)
        ttk.Button(button_frame, text="Sleep Logger", style='Custom.TButton', command=self.show_sleep_logger).pack(side=tk.LEFT,padx=20)
        ttk.Button(button_frame, text="Tasks", style='Custom.TButton', command=self.show_task_addition).pack(side=tk.LEFT,padx=20)
        ttk.Button(button_frame, text="Google Calendar", style='Custom.TButton', command=self.show_google_calendar).pack(side=tk.LEFT, padx=20)

        # Center the main_frame widget by aligning it to 50% of the width and height.
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
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
        google_calendar.GoogleCalendarUI(self.root, self.show_home)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartClockApp(root)
    root.mainloop()
