import tkinter as tk
import os
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from datetime import datetime

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.conn = None
        self.cursor = None
        self.root['background'] = '#ff9f2a'
        self.root.minsize(width=1280, height=950)
        self.task_list_tasks = []

        self.open_db_conn()

        # Setup UI
        self.create_task_manager_ui()
  
    def open_db_conn(self):
        '''Open and intitialize the database'''
        if self.conn is None:
          db_dir = os.path.join(os.getcwd(), "data")
          self.conn = sqlite3.connect(f"{db_dir}/tasks.db")
          self.cursor = self.conn.cursor()
          self.setup_database()

    def close_db_conn(self):
        '''Close the connection to the SQLite database.'''
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def return_to_home(self):
        from main import SmartClockApp
        '''Return to the home screen'''
        
        self.close_db_conn()
        SmartClockApp(self.root)        

    def setup_database(self):
        '''Create the database tables if they don't exist'''
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                due_date TEXT NOT NULL,
                due_time TEXT,
                description TEXT,
                tag_id INTEGER,
                status TEXT CHECK(status IN ('completed', 'upcoming', 'overdue')) NOT NULL,
                FOREIGN KEY (tag_id) REFERENCES tags (id)
            )
        ''')

        # Ensure 'misc' tag exists, and only create it if it doesn't. Ignore otherwise
        self.cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES ('misc')")
        self.conn.commit() # Commit changes to the database

    def clear_window(self):
        '''Clear all widgets in the window'''
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_task_manager_ui(self):
        '''Create the task manager UI'''

        self.clear_window()

        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#ff9f2a')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        home_button = ttk.Button(self.root, text='Home', style='Custom.TButton', command=self.return_to_home).pack(anchor=tk.NW, padx=30, pady=30)

        # Split UI into left and right frames
        self.left_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.left_frame.pack(side="left", fill="y", padx=30, pady=30)

        self.right_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # New task interface
        self.new_task_button = ttk.Button(self.left_frame, style='Custom.TButton', text="Create New Task", command=self.render_task_form)
        self.new_task_button.pack(pady=20)

        # Task list on the right
        task_frame = ttk.Frame(self.right_frame, style='Custom.TFrame')
        task_frame.pack(expand=True, fill='both')

        self.task_list_label = ttk.Label(task_frame, background='#ff9f2a', text="Tasks", font=("Arial", 16))
        self.task_list_label.pack(pady=10)

        self.task_list = tk.Listbox(task_frame, height=20, width=50)
        self.task_list.pack(pady=10)

        # Buttons for updating and deleting tasks
        self.update_button = ttk.Button(task_frame, style='Custom.TButton', text="Update Task", command=self.render_update_task_form).pack(pady=10)
        self.delete_button = ttk.Button(task_frame, style='Custom.TButton', text="Delete Task", command=self.delete_task).pack(pady=10)

        # Load tasks into the list
        self.load_tasks()

    def render_task_form(self):
        '''Renders the task creation form'''
        # Clear left frame and create task form
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#ff9f2a')

        task_frame = ttk.Frame(self.left_frame, style='Custom.TFrame')
        task_frame.pack(expand=True, fill='both')

        ttk.Label(task_frame, anchor='center', background='#ff9f2a', text="New Task", font=("Arial", 16)).pack(pady=10)

        # Task fields
        self.title_entry = self.create_form_field(task_frame, "Title:")
        date_vars = self.create_date_incrementer(task_frame)
        self.date_entry = f"{date_vars[0].get()}-{date_vars[1].get()}-{date_vars[2].get()}"
        time_vars = self.create_time_selector(task_frame)
        self.time_entry = (time_vars[0], time_vars[1])  # hour_var, minute_var
        self.am_pm_var = time_vars[2]  # am_pm_var
        self.description_entry = self.create_form_field(task_frame, "Description:", True)

        # Tag management
        ttk.Label(task_frame, background='#ff9f2a', text="Tag:").pack(anchor="w", pady=5)
        self.tag_var = tk.StringVar()
        self.tag_entry = ttk.Entry(task_frame, textvariable=self.tag_var)
        self.tag_entry.pack(fill="x", pady=5)
        ttk.Button(task_frame, text="Add Tag", command=self.add_new_tag).pack(pady=5)
        self.tag_dropdown = ttk.Combobox(task_frame, textvariable=self.tag_var, state="readonly")
        self.tag_dropdown.pack(fill="x", pady=5)
        self.load_tags()

        button_frame = ttk.Frame(task_frame, style='Custom.TFrame', )
        button_frame.pack(pady=100, anchor=tk.CENTER, expand=True, fill='both')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        # Task Options
        ttk.Button(button_frame, style='Custom.TButton', text="Save Task", command=lambda: self.save_task(date_vars[2], date_vars[0], date_vars[1])).pack(side=tk.LEFT, padx=20)
        ttk.Button(button_frame, style='Custom.TButton', text="Back", command=self.create_task_manager_ui).pack(side=tk.LEFT, padx=20)

    def render_update_task_form(self):
      '''Renders the task update form'''
      selected_index = self.task_list.curselection()
      if not selected_index:
          messagebox.showerror("Error", "Please select a task to update.")
          return
      
      task = self.task_list_tasks[selected_index[0]]  # Get task metadata
      self.cursor.execute("SELECT id FROM tasks WHERE title = ?", (task[0],))
      task_id = self.cursor.fetchone()[0]

      # Clear left frame and create update form
      for widget in self.left_frame.winfo_children():
          widget.destroy()

      bg_style = ttk.Style()
      bg_style.configure('Custom.TFrame', background='#ff9f2a')

      update_frame = ttk.Frame(self.left_frame, style='Custom.TFrame')
      update_frame.pack(expand=True, fill='both')

      ttk.Label(update_frame, background='#ff9f2a', text="Update Task", font=("Arial", 16)).pack(pady=10)

      # Populate fields with task data
      self.title_entry = self.create_form_field(update_frame, "Title:")
      self.title_entry.insert(0, task[0])  # Pre-fill with current title

      date_vars = self.create_date_incrementer(update_frame)
      self.date_entry = f"{date_vars[0].get()}-{date_vars[1].get()}-{date_vars[2].get()}"

      time_vars = self.create_time_selector(update_frame)
      self.time_entry = (time_vars[0], time_vars[1])
      self.am_pm_var = time_vars[2]

      self.description_entry = self.create_form_field(update_frame, "Description:", True)
      self.description_entry.insert("1.0", task[3])  # Pre-fill with current description

      # Tag management
      ttk.Label(update_frame, background='#ff9f2a', text="Tag:").pack(anchor="w", pady=5)
      self.tag_var = tk.StringVar(value=task[4])
      self.tag_entry = ttk.Entry(update_frame, textvariable=self.tag_var)
      self.tag_entry.pack(fill="x", pady=5)
      ttk.Button(update_frame, text="Add Tag", command=self.add_new_tag).pack(pady=5)
      self.tag_dropdown = ttk.Combobox(update_frame, textvariable=self.tag_var, state="readonly")
      self.tag_dropdown.pack(fill="x", pady=5)
      self.load_tags()

      button_frame = ttk.Frame(update_frame, style='Custom.TFrame')
      button_frame.pack(pady=100, anchor=tk.CENTER, expand=True, fill='both')

      btn_style = ttk.Style()
      btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

      # Save updated task
      ttk.Button(button_frame, text="Save Changes", style='Custom.TButton', command=lambda: self.update_task(task_id, date_vars[2], date_vars[0], date_vars[1])).pack(side=tk.LEFT, padx=20)
      ttk.Button(button_frame, text="Back", style='Custom.TButton', command=self.create_task_manager_ui).pack(side=tk.LEFT, padx=20)

    def update_task(self, task_id, year_var, month_var, day_var):
      '''Update an existing task in the database'''
      title = self.title_entry.get()
      if title == "":
          messagebox.showerror("Error", "Title cannot be empty.")
          return

      due_date = f"{year_var.get()}-{int(month_var.get()):02}-{int(day_var.get()):02}"
      hour = self.time_entry[0].get()
      minute = self.time_entry[1].get()
      am_pm = self.am_pm_var.get()
      due_time = self.convert_time_to_24hour(f"{hour}:{minute} {am_pm}") if hour and minute else None
      description = self.description_entry.get("1.0", tk.END).strip()

      tag_name = self.tag_var.get().strip()
      if not tag_name:
          tag_name = "misc"
      self.cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
      self.conn.commit()
      self.cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
      tag_id = self.cursor.fetchone()[0]

      self.cursor.execute(
          "UPDATE tasks SET title = ?, due_date = ?, due_time = ?, description = ?, tag_id = ? WHERE id = ?",
          (title, due_date, due_time, description, tag_id, task_id)
      )
      self.conn.commit()
      self.load_tasks()

    def create_form_field(self, frame, label_text, is_multiline=False):
        '''Create a form field with a label'''
        ttk.Label(frame, anchor='center', background='#ff9f2a', text=label_text).pack(anchor="w", pady=5)
        if is_multiline:
            entry = tk.Text(frame, height=4)
        else:
            entry = ttk.Entry(frame)
        entry.pack(fill="x", pady=5)
        return entry
    
    def create_date_incrementer(self, frame):
        '''Create a date incrementer with spinboxes for month, day, and year'''
        ttk.Label(frame, anchor='center', background='#ff9f2a', text="Date (MM-DD-YYYY):").pack(anchor="w", pady=5)

        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#ff9f2a')

        date_frame = ttk.Frame(frame, style='Custom.TFrame')
        date_frame.pack(fill="x", pady=5)

        month_var = tk.StringVar(value=str(datetime.now().month))
        month_spinbox = ttk.Spinbox(date_frame, from_=1, to=12, width=3, textvariable=month_var, validate='key')
        month_spinbox.configure(validatecommand=(self.root.register(self.validate_month), '%P'))
        month_spinbox.grid(row=0, column=0, padx=5)

        date_var = tk.StringVar(value=str(datetime.now().day))
        date_spinbox = ttk.Spinbox(date_frame, from_=1, to=31, width=3, textvariable=date_var, validate='key')
        date_spinbox.configure(validatecommand=(self.root.register(lambda value: self.validate_day(value, year_var, month_var)), '%P'))
        date_spinbox.grid(row=0, column=1, padx=5)

        year_var = tk.StringVar(value=str(datetime.now().year))
        year_spinbox = ttk.Spinbox(date_frame, from_=2024, to=2040, width=6, textvariable=year_var, validate='key')
        year_spinbox.configure(validatecommand=(self.root.register(self.validate_year), '%P'))
        year_spinbox.grid(row=0, column=2, padx=5)

        return (month_var, date_var, year_var)

    def create_time_selector(self, frame):
        '''Create a time selector with spinboxes for hour, minute, and AM/PM'''
        ttk.Label(frame, anchor='center', background='#ff9f2a', text="Time (Leave Empty for All-Day):").pack(anchor="w", pady=5)

        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#ff9f2a')

        time_frame = ttk.Frame(frame, style='Custom.TFrame')
        time_frame.pack(fill="x", pady=5)

        hour_var = tk.StringVar()
        hour_spinbox = ttk.Spinbox(time_frame, background='#ff9f2a', from_=1, to=12, width=3, textvariable=hour_var, validate='key')
        hour_spinbox.configure(validatecommand=(self.root.register(self.validate_hour), '%P'))
        hour_spinbox.grid(row=0, column=0, padx=5)

        minute_var = tk.StringVar()
        minute_spinbox = ttk.Spinbox(time_frame, background='#ff9f2a', from_=0, to=59, width=3, textvariable=minute_var, format="%02.0f", validate='key')
        minute_spinbox.configure(validatecommand=(self.root.register(self.validate_minutes), '%P'))
        minute_spinbox.grid(row=0, column=1, padx=5)

        am_pm_var = tk.StringVar(value="AM")
        am_pm_dropdown = ttk.Combobox(time_frame, background='#ff9f2a', textvariable=am_pm_var, values=["AM", "PM"], state="readonly", width=5)
        am_pm_dropdown.grid(row=0, column=2, padx=5)

        return (hour_var, minute_var, am_pm_var)

    def convert_time_to_24hour(self, time_str):
        '''Converts a time string from 12-hour format to 24-hour format'''
        try:
            return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
        except ValueError:
            return None

    def convert_time_to_ampm(self, time_str):
        '''Converts a time string from 24-hour format to 12-hour format'''
        try:
            return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
        except ValueError:
            return None
        
    def validate_month(self, value):
        '''Validate the month spinbox'''
        if value.isdigit():
            month = int(value)
            return month >= 1 and month <= 12
        return False
    
    def validate_day(self, value, year_var, month_var):
        '''Validate the day spinbox'''
        if value.isdigit():
            day = int(value)
            month = int(month_var.get())
            year = int(year_var.get())
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

            if month == 2 and year % 4 == 0:
                days_in_month[1] = 29

            return 1 <= day <= days_in_month[month - 1]
        return False
        
    def validate_year(self, value):
        '''Validate the year spinbox'''
        if value.isdigit():
            year = int(value)
            return year >= 2024 and year <= 2040
        return False
    
    def validate_hour(self, value):
        '''Validate the hour spinbox'''
        if value.isdigit():
            hour = int(value)
            return hour >= 1 and hour <= 12
        return False
    
    def validate_minutes(self, value):
        '''Validate the minute spinbox'''
        if value.isdigit():
            minute = int(value)
            return minute >= 0 and minute <= 59
        return False

    def load_tags(self):
        '''Load tags from the database and populate the dropdown'''
        self.cursor.execute("SELECT name FROM tags")
        tags = [tag[0] for tag in self.cursor.fetchall()]
        self.tag_dropdown["values"] = tags
        if not self.tag_var.get():
            self.tag_var.set("misc")

    def add_new_tag(self):
        '''Add a new tag to the database'''
        new_tag = self.tag_var.get().strip()
        if new_tag:
            self.cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (new_tag,))
            self.conn.commit()
            self.load_tags()
        else:
            tk.messagebox.showerror("Error", "Tag name cannot be empty.")

    def load_tasks(self):
        '''Load tasks from the database and display them in the listbox'''
        # Clear current list
        self.task_list.delete(0, tk.END)
        self.task_list_tasks = []

        # Fetch and display tasks
        self.cursor.execute('''
            SELECT tasks.title, tasks.due_date, tasks.due_time, tasks.description, tags.name, tasks.status
            FROM tasks
            LEFT JOIN tags ON tasks.tag_id = tags.id
        ''')
        tasks = self.cursor.fetchall()

        for task in tasks:
            task_time = self.convert_time_to_ampm(task[2]) if task[2] else 'All-Day'
            task_display = f"{task[0]} | {task[1]} | {task_time} | {task[4]} | {task[5]} | {task[3]}"
            self.task_list.insert(tk.END, task_display)
            self.task_list_tasks.append(task)

    def save_task(self, year_var, month_var, day_var):
        '''Save a new task to the database'''
        # Save new task to the database
        title = self.title_entry.get()
        if title == "":
            messagebox.showerror("Error", "Title cannot be empty.")
            return
        
        due_date = f"{year_var.get()}-{int(month_var.get()):02}-{int(day_var.get()):02}"
        hour = self.time_entry[0].get()
        minute = self.time_entry[1].get()
        am_pm = self.am_pm_var.get()
        due_time = self.convert_time_to_24hour(f"{hour}:{minute} {am_pm}") if hour and minute else None
        description = self.description_entry.get("1.0", tk.END).strip()

        # Handle tag
        tag_name = self.tag_var.get().strip()
        if not tag_name:
            tag_name = "misc"
        self.cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        self.conn.commit()
        self.cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_id = self.cursor.fetchone()[0]

        # Determine task status based on date and time
        task_datetime_str = f"{due_date} {due_time}" if due_time else due_date
        task_datetime = datetime.strptime(task_datetime_str, "%Y-%m-%d %H:%M") if due_time else datetime.strptime(task_datetime_str, "%Y-%m-%d")
        current_datetime = datetime.now()

        if task_datetime < current_datetime:
            status = "overdue"
        else:
            status = "upcoming"

        # Insert task into the database
        self.cursor.execute(
            "INSERT INTO tasks (title, due_date, due_time, description, tag_id, status) VALUES (?, ?, ?, ?, ?, ?)",
            (title, due_date, due_time, description, tag_id, status)
        )
        self.conn.commit()

        # Reload task list and reset UI
        self.create_task_manager_ui()

    def delete_task(self):
      '''Delete the selected task from the database'''
      selected_index = self.task_list.curselection()
      if not selected_index:
          messagebox.showerror("Error", "Please select a task to delete.")
          return

      tup = self.task_list_tasks[selected_index[0]]
      self.cursor.execute("SELECT id FROM tasks WHERE title = ?", (tup[0],))
      task_id = self.cursor.fetchone()[0]
      # task_id = self.task_list_tasks[selected_index[0]][0]  # Get task ID
      self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
      self.conn.commit()
      self.load_tasks()