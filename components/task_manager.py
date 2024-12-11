import tkinter as tk
import os
from tkinter import ttk
import sqlite3
from datetime import datetime

class TaskManager:
    def __init__(self, root, go_home):
        self.root = root
        self.go_home = go_home
        self.conn = None
        self.cursor = None
        self.root['background'] = '#ff9f2a'

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
                title TEXT NOT NULL,
                due_date TEXT NOT NULL,
                due_time TEXT NOT NULL,
                description TEXT,
                tag_id INTEGER,
                FOREIGN KEY (tag_id) REFERENCES tags (id)
            )
        ''')

        # Ensure 'misc' tag exists, and only create it if it doesn't. Ignore otherwise
        self.cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES ('misc')")
        self.conn.commit() # Commit changes to the database

    def create_task_manager_ui(self):
        '''Create the task manager UI'''
        
        image_dir = os.path.join(os.getcwd(), "images")
        home_img = tk.PhotoImage(file=f"{image_dir}/home.png")
        home_button = ttk.Button(self.root, image=home_img, command=self.return_to_home)
        home_button.place(x=0, y=0, anchor="nw")

        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#ff9f2a')

        # Split UI into left and right frames
        self.left_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.right_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # New task interface
        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        self.new_task_button = ttk.Button(self.left_frame, style='Custom.TButton', text="Create New Task", command=self.render_task_form)
        self.new_task_button.pack(pady=20)

        # Task list on the right
        self.task_list_label = ttk.Label(self.right_frame, text="Tasks", font=("Arial", 16))
        self.task_list_label.pack(pady=10)

        self.task_list = tk.Listbox(self.right_frame, height=20, width=50)
        self.task_list.pack(pady=10)

        # Load tasks into the list
        self.load_tasks()

    def render_task_form(self):
        '''Renders the task creation form'''
        # Clear left frame and create task form
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.left_frame, text="New Task", font=("Arial", 16)).pack(pady=10)

        # Task fields
        self.title_entry = self.create_form_field("Title:")
        self.date_entry = self.create_form_field("Date (YYYY-MM-DD):")
        self.time_entry = self.create_form_field("Time (HH:MM AM/PM or leave blank for all-day):")
        self.description_entry = self.create_form_field("Description:", True)

        # Tag dropdown
        ttk.Label(self.left_frame, text="Tag:").pack(anchor="w", pady=5)
        self.tag_var = tk.StringVar()
        self.tag_dropdown = ttk.Combobox(self.left_frame, textvariable=self.tag_var, state="readonly")
        self.tag_dropdown.pack(fill="x", pady=5)
        self.load_tags()

        # Save button
        ttk.Button(self.left_frame, text="Save Task", command=self.save_task).pack(pady=10)

        # Back button
        ttk.Button(self.left_frame, text="Back", command=self.create_task_manager_ui).pack(pady=10)

    def create_form_field(self, label_text, is_multiline=False):
        '''Create a form field with a label'''
        ttk.Label(self.left_frame, text=label_text).pack(anchor="w", pady=5)
        if is_multiline:
            entry = tk.Text(self.left_frame, height=4)
        else:
            entry = ttk.Entry(self.left_frame)
        entry.pack(fill="x", pady=5)
        return entry
    
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

    def load_tags(self):
        '''Load tags from the database and populate the dropdown'''
        self.cursor.execute("SELECT name FROM tags")
        tags = [tag[0] for tag in self.cursor.fetchall()]
        self.tag_dropdown["values"] = tags
        self.tag_var.set("misc")

    def load_tasks(self):
        '''Load tasks from the database and display them in the listbox'''
        # Clear current list
        self.task_list.delete(0, tk.END)

        # Fetch and display tasks
        self.cursor.execute('''
            SELECT tasks.title, tasks.due_date, tasks.due_time, tasks.description, tags.name
            FROM tasks
            LEFT JOIN tags ON tasks.tag_id = tags.id
        ''')
        tasks = self.cursor.fetchall()

        for task in tasks:
            task_time = self.convert_time_to_ampm(task[2]) if task[2] else 'All-Day'
            task_display = f"{task[0]} | {task[1]} {task_time} | {task[4]}"
            self.task_list.insert(tk.END, task_display)

    def save_task(self):
        '''Save a new task to the database'''
        # Save new task to the database
        title = self.title_entry.get()
        due_date = self.date_entry.get()
        due_time = self.convert_time_to_24hour(self.time_entry.get().strip()) or None

        # Select the entire text from the textbox from line 1 column 0 to the end
        description = self.description_entry.get("1.0", tk.END).strip()
        tag = self.tag_var.get()

        if not title or not due_date:
            tk.messagebox.showerror("Error", "Title and Date are required fields.")
            return

        # Get tag ID, or create if it doesn't exist
        self.cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        self.conn.commit()
        self.cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))

        # Fetches the tag id from the database. Returned as a tuple, so we get the first element
        tag_id = self.cursor.fetchone()[0]

        # Insert task into the database
        self.cursor.execute(
            "INSERT INTO tasks (title, due_date, due_time, description, tag_id) VALUES (?, ?, ?, ?, ?)",
            (title, due_date, due_time, description, tag_id)
        )
        self.conn.commit()

        # Reload task list and reset UI
        self.create_task_manager_ui()