import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import sqlite3

class HabitTracker:
    def __init__(self, root):
        self.root = root
        self.root['background'] = '#20ffc0'
        self.root.minsize(width=1280, height=950)

        # Initialize database
        self.conn = None
        self.cursor = None
        self.open_db_conn()

        self.create_habit_tracker_ui()

    def open_db_conn(self):
        '''Open and initialize the database'''
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
        '''Create tables if they do not exist'''
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                frequency TEXT CHECK(frequency IN ('daily', 'weekly', 'monthly', 'yearly')) NOT NULL,
                status TEXT CHECK(status IN ('incomplete', 'partially_completed', 'halfway_completed', 'mostly_completed', 'complete')) NOT NULL,
                start_date TEXT NOT NULL,
                progress INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES ('misc')")
        self.conn.commit()

    def clear_window(self):
        '''Clear all widgets in the window'''
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_habit_tracker_ui(self):
        '''Create the habit tracker UI'''

        self.clear_window()
        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#20ffc0')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        home_button = ttk.Button(self.root, text='Home', style='Custom.TButton', command=self.return_to_home).pack(anchor=tk.NW, padx=30, pady=30)

        # Split UI into left and right frames
        self.left_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.left_frame.pack(side="left", fill="y", padx=30, pady=30)

        self.right_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # New habit interface
        self.new_habit_button = ttk.Button(self.left_frame, style='Custom.TButton', text="Create New Habit", command=self.render_habit_form)
        self.new_habit_button.pack(pady=20)

        # Habit list on the right
        habit_frame = ttk.Frame(self.right_frame, style='Custom.TFrame')
        habit_frame.pack(expand=True, fill='both')

        self.habit_tree = ttk.Treeview(habit_frame, columns=("Name", "Frequency", "Status", "Start Date", "Category"), show="headings")
        self.habit_tree.heading("Name", text="Name")
        self.habit_tree.heading("Frequency", text="Frequency")
        self.habit_tree.heading("Status", text="Status")
        self.habit_tree.heading("Start Date", text="Start Date")
        self.habit_tree.heading("Category", text="Category")
        self.habit_tree.pack(expand=True, fill="both", pady=10)

        self.habit_tree.bind("<<TreeviewSelect>>", self.show_progress)

        self.progress_frame = ttk.Frame(self.right_frame, style='Custom.TFrame')
        self.progress_frame.pack(fill="x", pady=10)

        self.progress_label = ttk.Label(self.progress_frame, text="Progress: 0%", font=("Arial", 14), background='#20ffc0')
        self.progress_label.pack(side="left", padx=10)

        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(side="left", padx=10)

        button_frame = ttk.Frame(self.right_frame, style='Custom.TFrame', padding=5)
        button_frame.pack(anchor="center", expand=True, fill='none')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        ttk.Button(button_frame, text="View Description", style='Custom.TButton', command=self.view_description).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Update Habit", style='Custom.TButton', command=self.update_habit).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Delete Habit", style='Custom.TButton', command=self.delete_habit).pack(side="left", padx=10)

        # Load habits into the treeview
        self.load_habits()

    def render_habit_form(self, habit=None):
        '''Render the form for creating or updating a habit'''
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        if habit:
            ttk.Label(self.left_frame, background='#20ffc0', text="Update Habit", font=("Arial", 16)).pack(pady=10)
        else:
            ttk.Label(self.left_frame, background='#20ffc0', text="New Habit", font=("Arial", 16)).pack(pady=10)

        self.habit_name_var = tk.StringVar(value=habit[0] if habit else "")
        ttk.Label(self.left_frame, text="Habit Name:", background='#20ffc0').pack(anchor="w", pady=5)
        ttk.Entry(self.left_frame, textvariable=self.habit_name_var).pack(fill="x", pady=5)

        self.description_var = tk.StringVar(value=habit[1] if habit else "")
        ttk.Label(self.left_frame, text="Description:", background='#20ffc0').pack(anchor="w", pady=5)
        description_entry = ttk.Entry(self.left_frame, textvariable=self.description_var, width=50)
        description_entry.pack(fill="x", pady=5)

        ttk.Label(self.left_frame, text="Start Date:", background='#20ffc0').pack(anchor="w", pady=5)
        self.start_date_vars = self.create_date_incrementer(self.left_frame)

        ttk.Label(self.left_frame, text="Frequency:", background='#20ffc0').pack(anchor="w", pady=5)
        self.frequency_var = tk.StringVar(value=habit[2] if habit else 'daily')
        self.frequency_dropdown = ttk.Combobox(self.left_frame, textvariable=self.frequency_var, values=['daily', 'weekly', 'monthly', 'yearly'], state="readonly")
        self.frequency_dropdown.pack(fill="x", pady=5)

        ttk.Label(self.left_frame, text="Status:", background='#20ffc0').pack(anchor="w", pady=5)
        self.status_var = tk.StringVar(value=habit[3] if habit else 'incomplete')
        self.status_dropdown = ttk.Combobox(self.left_frame, textvariable=self.status_var, values=['incomplete', 'partially_completed', 'halfway_completed', 'mostly_completed', 'complete'], state="readonly")
        self.status_dropdown.pack(fill="x", pady=5)

        ttk.Label(self.left_frame, text="Category:", background='#20ffc0').pack(anchor="w", pady=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.left_frame, textvariable=self.category_var, state="readonly")
        self.load_categories()
        self.category_dropdown.pack(fill="x", pady=5)

        category_frame = ttk.Frame(self.left_frame)
        category_frame.pack(fill="x", pady=5)

        ttk.Entry(category_frame, textvariable=self.category_var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(category_frame, text="Add Category", command=self.add_category).pack(side="right", padx=5)

        button_frame = ttk.Frame(self.left_frame, style='Custom.TFrame', )
        button_frame.pack(pady=100, expand=True, fill='none')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        ttk.Button(button_frame, style='Custom.TButton', text="Save Habit", command=lambda: self.save_habit(habit)).pack(pady=10)
        ttk.Button(button_frame, style='Custom.TButton', text="Back", command=self.create_habit_tracker_ui).pack(side=tk.LEFT, padx=20)

    def create_date_incrementer(self, frame):
        '''Create a date incrementer with spinboxes for month, day, and year'''
        date_frame = ttk.Frame(frame)
        date_frame.pack(fill="x", pady=5)

        month_var = tk.StringVar(value=str(datetime.now().month))
        month_spinbox = ttk.Spinbox(date_frame, from_=1, to=12, width=3, textvariable=month_var)
        month_spinbox.grid(row=0, column=0, padx=5)

        day_var = tk.StringVar(value=str(datetime.now().day))
        day_spinbox = ttk.Spinbox(date_frame, from_=1, to=31, width=3, textvariable=day_var)
        day_spinbox.grid(row=0, column=1, padx=5)

        year_var = tk.StringVar(value=str(datetime.now().year))
        year_spinbox = ttk.Spinbox(date_frame, from_=2023, to=2040, width=5, textvariable=year_var)
        year_spinbox.grid(row=0, column=2, padx=5)

        return (month_var, day_var, year_var)

    def load_categories(self):
        '''Load categories into the dropdown'''
        self.cursor.execute("SELECT name FROM categories")
        categories = [row[0] for row in self.cursor.fetchall()]
        self.category_dropdown['values'] = categories

    def add_category(self):
        '''Add a new category to the database'''
        category_name = self.category_var.get().strip()
        if not category_name:
            messagebox.showerror("Error", "Category name cannot be empty.")
            return

        self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category_name,))
        self.conn.commit()
        messagebox.showinfo("Success", f"Category '{category_name}' added successfully.")
        self.load_categories()

    def save_habit(self, habit=None):
        '''Save a new habit or update an existing one in the database'''
        name = self.habit_name_var.get()
        description = self.description_var.get()
        frequency = self.frequency_var.get()
        status = self.status_var.get()
        category = self.category_var.get().strip()
        start_date = f"{self.start_date_vars[2].get()}-{self.start_date_vars[0].get()}-{self.start_date_vars[1].get()}"

        if not name or not frequency or not category:
            messagebox.showerror("Error", "All fields are required.")
            return

        # Map status to progress
        status_to_progress = {
            'incomplete': 0,
            'partially_completed': 25,
            'halfway_completed': 50,
            'mostly_completed': 75,
            'complete': 100
        }
        progress = status_to_progress.get(status, 0)

        # Handle category
        self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        self.conn.commit()
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        category_id = self.cursor.fetchone()[0]

        if habit:
            # Update existing habit
            self.cursor.execute('''
                UPDATE habits
                SET name = ?, description = ?, frequency = ?, status = ?, start_date = ?, progress = ?, category_id = ?
                WHERE name = ?
            ''', (name, description, frequency, status, start_date, progress, category_id, habit[0]))
        else:
            # Save new habit
            self.cursor.execute('''
                INSERT INTO habits (name, description, frequency, status, start_date, progress, category_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, frequency, status, start_date, progress, category_id))

        self.conn.commit()
        self.load_habits()

    def load_habits(self):
        '''Load habits into the treeview'''
        for row in self.habit_tree.get_children():
            self.habit_tree.delete(row)

        self.cursor.execute('''
            SELECT habits.name, habits.frequency, habits.status, habits.start_date, categories.name
            FROM habits
            LEFT JOIN categories ON habits.category_id = categories.id
        ''')
        for habit in self.cursor.fetchall():
            self.habit_tree.insert("", "end", values=habit)

    def view_description(self):
        '''View the description of the selected habit'''
        selected_item = self.habit_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a habit to view the description.")
            return

        habit_name = self.habit_tree.item(selected_item)['values'][0]
        self.cursor.execute("SELECT description FROM habits WHERE name = ?", (habit_name,))
        description = self.cursor.fetchone()[0]

        description_window = tk.Toplevel(self.root)
        description_window.title("Habit Description")
        description_window.geometry("400x200")

        ttk.Label(description_window, text=f"Description:", font=("Arial", 14)).pack(pady=10)
        description_label = ttk.Label(description_window, text=description, font=("Arial", 12), wraplength=350, justify="left")
        description_label.pack(pady=10)

    def show_progress(self, event):
        '''Show the progress of a selected habit'''
        selected_item = self.habit_tree.selection()
        if not selected_item:
            self.progress_label.config(text="Progress: 0%")
            self.progress_bar['value'] = 0
            return

        habit_name = self.habit_tree.item(selected_item)['values'][0]
        self.cursor.execute("SELECT progress FROM habits WHERE name = ?", (habit_name,))
        progress = self.cursor.fetchone()[0]

        self.progress_label.config(text=f"Progress: {progress}%")
        self.progress_bar['value'] = progress

    def update_habit(self):
        '''Update the selected habit'''
        selected_item = self.habit_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a habit to update.")
            return

        habit_values = self.habit_tree.item(selected_item)['values']
        self.render_habit_form(habit_values)

    def delete_habit(self):
        '''Delete the selected habit'''
        selected_item = self.habit_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a habit to delete.")
            return

        habit_name = self.habit_tree.item(selected_item)['values'][0]
        self.cursor.execute("DELETE FROM habits WHERE name = ?", (habit_name,))
        self.conn.commit()
        self.load_habits()