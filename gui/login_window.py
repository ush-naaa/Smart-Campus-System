# gui/login_window.py
import tkinter as tk
from tkinter import messagebox
from database.db_manager import verify_user

class LoginWindow(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Green theme background
        self.configure(bg="#E9F7EF")  # light green background
        
        # Center Frame
        login_frame = tk.Frame(
            self, bg="#D5F5E3", padx=40, pady=40, 
            highlightbackground="#145A32", highlightthickness=2
        )
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title (big emoji)
        tk.Label(login_frame, text="🎓", font=("Arial", 26), bg="#D5F5E3").pack()
        tk.Label(
            login_frame, text="Smart Campus Login", font=("Arial", 18, "bold"),
            fg="#145A32", bg="#D5F5E3"
        ).pack(pady=(0, 20))

        # Username Label
        row1 = tk.Frame(login_frame, bg="#D5F5E3")
        row1.pack(anchor="w")
        tk.Label(row1, text="👤", font=("Arial", 16), bg="#D5F5E3").pack(side="left")
        tk.Label(row1, text="Username", font=("Arial", 10), bg="#D5F5E3", fg="#145A32").pack(side="left")

        self.username_entry = tk.Entry(
            login_frame, width=30, fg="#145A32", bg="#ECF9F1",
            insertbackground="#145A32"
        )
        self.username_entry.pack(pady=(0, 15))

        # Password Label
        row2 = tk.Frame(login_frame, bg="#D5F5E3")
        row2.pack(anchor="w")
        tk.Label(row2, text="🔐", font=("Arial", 16), bg="#D5F5E3").pack(side="left")
        tk.Label(row2, text="Password", font=("Arial", 10), bg="#D5F5E3", fg="#145A32").pack(side="left")

        self.password_entry = tk.Entry(
            login_frame, show="*", width=30, fg="#145A32", bg="#ECF9F1",
            insertbackground="#145A32"
        )
        self.password_entry.pack(pady=(0, 5))

        # Show Password
        self.var_show_pass = tk.IntVar()
        tk.Checkbutton(
            login_frame, text="Show Password", font=("Arial", 11),
            variable=self.var_show_pass, onvalue=1, offvalue=0,
            command=self.toggle_password,
            bg="#D5F5E3", fg="#145A32", selectcolor="#D5F5E3"
        ).pack(anchor="w", pady=(0, 20))

        # Login Button
        tk.Button(
            login_frame, text="➡️ Login", font=("Arial", 12),
            bg="#145A32", fg="white", width=25,
            activebackground="#1E8449", activeforeground="white",
            command=self.handle_login, cursor="hand2"
        ).pack()

    def toggle_password(self):
        if self.var_show_pass.get() == 1:
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def handle_login(self):
        user = self.username_entry.get()
        pw = self.password_entry.get()
        
        if not user or not pw:
            messagebox.showwarning("⚠️ Input Error", "Please fill in all fields")
            return

        role = verify_user(user, pw)
        
        if role:
            self.controller.show_dashboard(user, role)
        else:
            messagebox.showerror("❌ Error", "Invalid credentials")