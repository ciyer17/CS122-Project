import tkinter as tk
from tkinter import ttk
import os
from tkinter import messagebox
from datetime import datetime
import sqlite3
from plyer import notification # For notifications

class PomodoroTimer:
    def __init__(self, root):
        self.root = root

        self.timer_running = False
        self.work_duration = 25  # Default work duration in minutes
        self.break_duration = 5  # Default break duration in minutes
        self.remaining_time = None
        self.is_work_interval = True
        self.root['background'] = '#0385ff'
        self.root.minsize(width=1280, height=720)
        self.conn = None
        self.cursor = None

        # Initialize database
        self.open_db_conn()
        
        self.create_pomodoro_ui()

    def open_db_conn(self):
        '''Open and intitialize the database'''
        if self.conn is None:
          db_dir = os.path.join(os.getcwd(), "data")
          self.conn = sqlite3.connect(f"{db_dir}/tasks.db")
          self.cursor = self.conn.cursor()

    def close_db_conn(self):
        '''Close the connection to the SQLite database.'''
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def create_pomodoro_ui(self):
        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#0385ff')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        # Split UI into left and right frames
        self.left_frame = ttk.Frame(self.root, style='Custom.TFrame', padding=10)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.right_frame = ttk.Frame(self.root, style='Custom.TFrame', padding=10)
        self.right_frame.pack(side="right", anchor="center", expand=True, fill="both", padx=10, pady=10)

        # Left Frame: Pomodoro Timer
        self.timer_label = ttk.Label(self.left_frame, background='#0385ff', text="25:00", font=("Arial", 40))
        self.timer_label.pack(pady=20)

        ttk.Label(self.left_frame, background='#0385ff', text="Work Duration (minutes):", font=("Arial", 18)).pack(anchor="w", pady=5)
        self.work_spinbox = ttk.Spinbox(self.left_frame, from_=1, to=60, width=5, validate="key")
        self.work_spinbox.set(self.work_duration)
        self.work_spinbox.pack(anchor="w", pady=5)

        ttk.Label(self.left_frame, background='#0385ff', text="Break Duration (minutes):", font=("Arial", 18)).pack(anchor="w", pady=5)
        self.break_spinbox = ttk.Spinbox(self.left_frame, from_=1, to=30, width=5, validate="key")
        self.break_spinbox.set(self.break_duration)
        self.break_spinbox.pack(anchor="w", pady=5)

        self.start_button = ttk.Button(self.left_frame, style='Custom.TButton', text="Start", command=self.start_pomodoro)
        self.start_button.pack(pady=10)

        self.end_button = ttk.Button(self.left_frame, style='Custom.TButton', text="End Session", command=self.end_pomodoro)
        self.end_button.pack(pady=10)

        self.reset_button = ttk.Button(self.left_frame, style='Custom.TButton', text="Reset Timer", command=self.reset_pomodoro)
        self.reset_button.pack(pady=10)

        # Right Frame: Task List
        self.task_list_label = ttk.Label(self.right_frame, background='#0385ff', text="Tasks", font=("Arial", 22))
        self.task_list_label.pack(pady=10)

        self.task_list = ttk.Treeview(self.right_frame, columns=("Title", "Status", "Date", "Time", "Tag"), show="headings")
        self.task_list.heading("Title", text="Title")
        self.task_list.heading("Status", text="Status")
        self.task_list.heading("Date", text="Date")
        self.task_list.heading("Time", text="Time")
        self.task_list.heading("Tag", text="Tag")
        self.task_list.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.right_frame, style='Custom.TFrame', padding=10)
        button_frame.pack(anchor="center", expand=True, fill='none')

        # Task Buttons
        self.mark_complete_button = ttk.Button(button_frame, style='Custom.TButton', text="Mark as Complete", command=self.mark_task_complete)
        self.mark_complete_button.pack(side="left", padx=10)

        self.add_task_button = ttk.Button(button_frame, style='Custom.TButton', text="Add Task", command=self.open_task_form)
        self.add_task_button.pack(side="left", padx=10)

        self.view_description_button = ttk.Button(button_frame, style='Custom.TButton', text="View Description", command=self.show_task_description)
        self.view_description_button.pack(pady=10)

        self.load_tasks()

    def start_pomodoro(self):
        if self.timer_running:
            return

        try:
            self.work_duration = int(self.work_spinbox.get())
            self.break_duration = int(self.break_spinbox.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid durations for work and break intervals.")
            return

        self.is_work_interval = True
        self.remaining_time = self.work_duration * 60
        self.update_timer()

    def update_timer(self):
        if self.remaining_time is not None and self.timer_label.winfo_exists():
            minutes, seconds = divmod(self.remaining_time, 60)
            self.timer_label.config(text=f"{minutes:02}:{seconds:02}")

            if self.remaining_time > 0:
                self.timer_running = True
                self.remaining_time -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.timer_running = False
                self.handle_interval_end()

    def handle_interval_end(self):
        if self.is_work_interval:
            notification.notify(
              title="Pomodoro Timer",
              message="Work interval complete! Time for a break.",
              app_name="Pomodoro Timer",
              timeout=5
            )
            self.remaining_time = self.break_duration * 60
        else:
            notification.notify(
              title="Pomodoro Timer",
              message="Break interval complete! Back to work.",
              app_name="Pomodoro Timer",
              timeout=5
            )            
            self.remaining_time = self.work_duration * 60

        self.is_work_interval = not self.is_work_interval
        self.update_timer()

    def reset_pomodoro(self):
        self.timer_running = False
        self.remaining_time = None
        self.is_work_interval = False
        self.work_duration = 25
        self.break_duration = 5
        self.work_spinbox.set(self.work_duration)
        self.break_spinbox.set(self.break_duration)
        self.timer_label.config(text="25:00")

    def end_pomodoro(self):
        self.timer_running = False
        self.timer_label.config(text="25:00")
        self.close_db_conn()
        self.return_to_home()

    def load_tasks(self):
        # Clear current list
        for row in self.task_list.get_children():
            self.task_list.delete(row)

        # Fetch overdue and upcoming tasks
        self.cursor.execute('''
            SELECT tasks.id, tasks.title, tasks.due_date, tasks.due_time, tags.name, tasks.status
            FROM tasks
            LEFT JOIN tags ON tasks.tag_id = tags.id
            WHERE tasks.status IN ('overdue', 'upcoming')
        ''')
        tasks = self.cursor.fetchall()

        for task in tasks:
            task_time = self.convert_time_to_ampm(task[3]) if task[3] else "All-Day"
            self.task_list.insert("", "end", iid=task[0], values=(task[1], task[5], task[2], task_time, task[4]))

    def show_task_description(self):
        selected_item = self.task_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a task to view its description.")
            return

        task_id = selected_item[0]
        self.cursor.execute("SELECT description FROM tasks WHERE id = ?", (task_id,))
        description = self.cursor.fetchone()[0]
        messagebox.showinfo("Task Description", description)


    def mark_task_complete(self):
        selected_item = self.task_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a task to mark as complete.")
            return

        task_id = selected_item[0]
        self.cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
        self.conn.commit()
        self.load_tasks()

    def convert_time_to_ampm(self, time_str):
        try:
            return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
        except ValueError:
            return time_str

    def open_task_form(self):
        from components import task_manager
        self.close_db_conn()
        task_manager.TaskManager(self.root)

    def return_to_home(self):
        from main import SmartClockApp
        '''Return to the home screen'''
        
        self.close_db_conn()
        SmartClockApp(self.root) 
