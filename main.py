#main.py
import tkinter as tk
from gui.login_window import LoginWindow
from gui.dashboard import Dashboard
from database.db_manager import initialize_db


class SmartCampusApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Smart Campus Resource Management System")
        self.geometry("1000x650")
        
        # This container will hold all the different pages
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        
        # Grid configuration to make frames overlap
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # Start by showing the Login Window
        self.show_login()

    def show_login(self):
        """Clears current frames and loads the Login screen."""
        frame = LoginWindow(parent=self.container, controller=self)
        self.frames["LoginWindow"] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def show_dashboard(self, username, role):
        """Transitions to the Dashboard and passes user data."""
        frame = Dashboard(parent=self.container, controller=self, username=username, role=role)
        self.frames["Dashboard"] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

if __name__ == "__main__":
    initialize_db()   # run DB setup ONCE
    app = SmartCampusApp()
    app.mainloop()
