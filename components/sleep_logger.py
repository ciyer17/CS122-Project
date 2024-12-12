import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import os
import sqlite3

class SleepLogger:
    def __init__(self, root):
        self.root = root
        self.root['background'] = '#ffedd0'
        self.root.minsize(width=1280, height=950)

        # Initialize database
        self.conn = None
        self.cursor = None
        self.open_db_conn()

        self.create_sleep_logger_ui()

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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sleep_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                hours_slept REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def create_sleep_logger_ui(self):

        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#ffedd0')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        home_button = ttk.Button(self.root, text='Home', style='Custom.TButton', command=self.return_to_home).pack(anchor=tk.NW, padx=30, pady=30)

        # Split UI into left and right frames
        self.left_frame = ttk.Frame(self.root, style='Custom.TFrame', padding=10)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.right_frame = ttk.Frame(self.root, style='Custom.TFrame', padding=10)
        self.right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        log_frame = ttk.Frame(self.left_frame, style='Custom.TFrame')
        log_frame.pack(expand=True, fill='both')

        # Left Frame: Input Form
        ttk.Label(log_frame, background='#ffedd0', text="Log Sleep Data", font=("Arial", 16)).pack(pady=10)

        self.date_vars = self.create_date_incrementer(log_frame)

        # Hours Slept
        ttk.Label(log_frame, background='#ffedd0', text="Hours Slept:").pack(anchor="w", pady=5)
        self.hours_slept_var = tk.StringVar()
        ttk.Entry(log_frame, textvariable=self.hours_slept_var).pack(fill="x", pady=5)

        # Buttons
        ttk.Button(log_frame, style='Custom.TButton', text="Add Log", command=self.add_log).pack(pady=10)
        ttk.Button(log_frame, style='Custom.TButton', text="Update Log", command=self.update_log).pack(pady=10)

        # Right Frame: Display Logs
        self.logs_label = ttk.Label(self.right_frame, background='#ffedd0', text="Sleep Logs", font=("Arial", 16))
        self.logs_label.pack(pady=10)

        self.logs_tree = ttk.Treeview(self.right_frame, columns=("Date", "Hours"), show="headings")
        self.logs_tree.heading("Date", text="Date")
        self.logs_tree.heading("Hours", text="Hours Slept")
        self.logs_tree.pack(expand=True, fill="both", pady=10)

        self.logs_tree.bind("<Double-1>", self.on_log_select)

        # Delete Button
        ttk.Button(self.right_frame, style='Custom.TButton', text="Delete Log", command=self.delete_log).pack(pady=10)

        self.load_logs()

    def create_date_incrementer(self, frame):
        '''Create a date incrementer with spinboxes for month, day, and year'''
        ttk.Label(frame, anchor='center', background='#ffedd0', text="Date (MM-DD-YYYY):").pack(anchor="w", pady=5)

        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#ffedd0')

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

    def add_log(self):
        date = f"{self.date_vars[2].get()}-{self.date_vars[0].get()}-{self.date_vars[1].get()}"
        hours_slept = self.hours_slept_var.get().strip()

        if not date or not hours_slept:
            messagebox.showerror("Error", "All fields are required.")
            return

        if datetime.strptime(date, "%Y-%m-%d") > datetime.now():
            messagebox.showerror("Error", "Date cannot be in the future.")
            return

        try:
            hours_slept = round(float(hours_slept), 1)
            if hours_slept < 0 or hours_slept > 24:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Hours slept must be a number and must be between 0 and 24 inclusive.")
            return

        try:
            self.cursor.execute(
                "INSERT INTO sleep_logs (date, hours_slept) VALUES (?, ?)",
                (date, hours_slept)
            )
            self.conn.commit()
            self.load_logs()
            self.clear_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "A log for this date already exists.")

    def load_logs(self):
        # Clear the treeview
        for row in self.logs_tree.get_children():
            self.logs_tree.delete(row)

        # Fetch and populate logs
        self.cursor.execute("SELECT id, date, hours_slept FROM sleep_logs")
        for log in self.cursor.fetchall():
            self.logs_tree.insert("", "end", iid=log[0], values=(log[1], log[2]))

    def on_log_select(self, event):
        selected_item = self.logs_tree.selection()
        if not selected_item:
            return

        log_id = selected_item[0]
        self.cursor.execute("SELECT date, hours_slept FROM sleep_logs WHERE id = ?", (log_id,))
        log = self.cursor.fetchone()

        if log:
            date_parts = log[0].split("-")
            self.date_vars[0].set(date_parts[1])  # Month
            self.date_vars[1].set(date_parts[2])  # Day
            self.date_vars[2].set(date_parts[0])  # Year
            self.hours_slept_var.set(log[1])

    def update_log(self):
        selected_item = self.logs_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a log to update.")
            return

        log_id = selected_item[0]
        date = f"{self.date_vars[2].get()}-{self.date_vars[0].get()}-{self.date_vars[1].get()}"
        hours_slept = self.hours_slept_var.get().strip()

        if not date or not hours_slept:
            messagebox.showerror("Error", "All fields are required.")
            return

        if datetime.strptime(date, "%Y-%m-%d") > datetime.now():
            messagebox.showerror("Error", "Date cannot be in the future.")
            return

        try:
            hours_slept = round(float(hours_slept), 1)
        except ValueError:
            messagebox.showerror("Error", "Hours slept must be a number.")
            return

        self.cursor.execute(
            "UPDATE sleep_logs SET date = ?, hours_slept = ? WHERE id = ?",
            (date, hours_slept, log_id)
        )
        self.conn.commit()
        self.load_logs()
        self.clear_form()

    def delete_log(self):
        selected_item = self.logs_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a log to delete.")
            return

        log_id = selected_item[0]
        self.cursor.execute("DELETE FROM sleep_logs WHERE id = ?", (log_id,))
        self.conn.commit()
        self.load_logs()

    def clear_form(self):
        self.date_vars[0].set(str(datetime.now().month))  # Month
        self.date_vars[1].set(str(datetime.now().day))    # Day
        self.date_vars[2].set(str(datetime.now().year))   # Year
        self.hours_slept_var.set("")

    def return_home(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.go_home()