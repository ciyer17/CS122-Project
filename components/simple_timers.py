import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from plyer import notification # pip install plyer

class SimpleTimers:
    def __init__(self, root):
        self.root = root
        self.timer_running = False
        self.remaining_time = None
        self.root['background'] = '#ff458c'
        self.root.minsize(width=1280, height=720)

        self.create_timer_ui()

    def create_timer_ui(self):
        
        bg_style = ttk.Style()
        bg_style.configure('Custom.TFrame', background='#ff458c')

        btn_style = ttk.Style()
        btn_style.configure('Custom.TButton', background='#ffef0a', relief='solid', font=('Arial', 18), width=15)

        home_button = ttk.Button(self.root, text='Home', style='Custom.TButton', command=self.return_home).pack(anchor=tk.NW, padx=30, pady=30)

        # Main frame
        main_frame = ttk.Frame(self.root, style='Custom.TFrame', padding=20)
        main_frame.pack(fill="both", expand=True)

        # Label
        ttk.Label(main_frame, text="Simple Timers", background='#ff458c', font=("Arial", 30)).pack(pady=10)

        # Preset Timer Buttons
        preset_frame = ttk.Frame(main_frame, style='Custom.TFrame', padding=10)
        preset_frame.pack(pady=20)

        ttk.Button(preset_frame, style='Custom.TButton', text="5 Minutes", command=lambda: self.start_timer(5 * 60)).pack(side="left", padx=10)
        ttk.Button(preset_frame, style='Custom.TButton', text="10 Minutes", command=lambda: self.start_timer(10 * 60)).pack(side="left", padx=10)
        ttk.Button(preset_frame, style='Custom.TButton', text="30 Minutes", command=lambda: self.start_timer(30 * 60)).pack(side="left", padx=10)

        # Custom Timer Input
        custom_frame = ttk.Frame(main_frame, style='Custom.TFrame', padding=10)
        custom_frame.pack(pady=20)

        ttk.Label(custom_frame, background='#ff458c', font=("Arial", 22), text="Custom Timer (H:M:S):").grid(row=0, column=0, padx=5, pady=5)

        self.hours_var = tk.StringVar(value="0")
        self.minutes_var = tk.StringVar(value="0")
        self.seconds_var = tk.StringVar(value="0")

        ttk.Entry(custom_frame, textvariable=self.hours_var, width=5).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(custom_frame, background='#ff458c', text=":").grid(row=0, column=2)
        ttk.Entry(custom_frame, textvariable=self.minutes_var, width=5).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(custom_frame, background='#ff458c', text=":").grid(row=0, column=4)
        ttk.Entry(custom_frame, textvariable=self.seconds_var, width=5).grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(custom_frame, style='Custom.TButton', text="Start Custom Timer", command=self.start_custom_timer).grid(row=0, column=8, padx=10, ipadx=10)

        # Timer Display
        self.timer_label = ttk.Label(main_frame, background='#ff458c', text="00:00:00", font=("Arial", 30))
        self.timer_label.pack(pady=20)

        # Control Buttons
        control_frame = ttk.Frame(main_frame, style='Custom.TFrame', padding=10)
        control_frame.pack(pady=20)

        self.pause_button = ttk.Button(control_frame, style='Custom.TButton', text="Pause", command=self.pause_timer, state="disabled")
        self.pause_button.pack(side="left", padx=10)

        self.resume_button = ttk.Button(control_frame, style='Custom.TButton', text="Resume", command=self.resume_timer, state="disabled")
        self.resume_button.pack(side="left", padx=10)

        self.reset_button = ttk.Button(control_frame, style='Custom.TButton', text="Reset", command=self.reset_timer, state="disabled")
        self.reset_button.pack(side="left", padx=10)

    def start_timer(self, seconds):
        if self.timer_running:
            return

        self.remaining_time = seconds
        self.timer_running = True
        self.pause_button["state"] = "normal"
        self.reset_button["state"] = "normal"
        self.update_timer()

    def start_custom_timer(self):
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            seconds = int(self.seconds_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hours, minutes, and seconds.")
            self.reset_timer()
            return

        total_seconds = hours * 3600 + minutes * 60 + seconds
        if total_seconds <= 0:
            messagebox.showerror("Invalid Input", "Please enter a positive time duration.")
            self.reset_timer()
            return

        self.start_timer(total_seconds)

    def update_timer(self):
        if self.remaining_time is None or not self.timer_running:
            return

        hours, remainder = divmod(self.remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        self.timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")

        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.timer_running = False
            self.pause_button["state"] = "disabled"
            notification.notify(
              title="Simple Timer",
              message="Time's Up! Your timer has ended.",
              app_name="Simple Timer",
              timeout=10
            )

    def pause_timer(self):
        self.timer_running = False
        self.pause_button["state"] = "disabled"
        self.resume_button["state"] = "normal"

    def resume_timer(self):
        if not self.timer_running and self.remaining_time is not None:
            self.timer_running = True
            self.resume_button["state"] = "disabled"
            self.pause_button["state"] = "normal"
            self.update_timer()

    def reset_timer(self):
        self.timer_running = False
        self.remaining_time = None
        self.timer_label.config(text="00:00:00")
        self.pause_button["state"] = "disabled"
        self.resume_button["state"] = "disabled"
        self.reset_button["state"] = "disabled"
        self.hours_var.set("0")
        self.minutes_var.set("0")
        self.seconds_var.set("0")

    def return_home(self):
        from main import SmartClockApp
        
        self.timer_running = False
        for widget in self.root.winfo_children():
            widget.destroy()

        SmartClockApp(self.root)