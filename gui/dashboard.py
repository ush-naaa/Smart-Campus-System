import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db_manager import (
    fetch_all_resources, delete_resource, 
    is_room_available, save_booking, fetch_all_equipment,
    search_resources, delete_booking, fetch_notices, add_notice,
    get_analytics_data, fetch_logs, add_log
)

class Dashboard(tk.Frame):
    def __init__(self, parent, controller, username, role):
        super().__init__(parent)
        self.controller = controller
        self.username = username
        self.role = role

        # --- Sidebar and Content Layout ---
        self.sidebar = tk.Frame(self, width=200, bg="#145A32")  # dark green
        self.sidebar.pack(side="left", fill="y")
        self.content_area = tk.Frame(self, bg="#E9F7EF")  # light green
        self.content_area.pack(side="right", fill="both", expand=True)

        # --- Sidebar Branding ---
        tk.Label(self.sidebar, text="SMART CAMPUS", fg="white", bg="#145A32", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Label(self.sidebar, text=f"👤 {self.username}\n🛡️{self.role}", fg="#D5F5E3", bg="#145A32", font=("Arial", 11, "bold"), justify="center").pack(pady=15)

        # --- Role-Based Navigation ---
        nav_items = [("🏠 Home", self.show_home)]
        if self.role == "Admin":
            nav_items.extend([
                ("🏢 Campus Management", self.show_rooms),
                ("📖 Book Room / Lab", self.show_booking),
                ("📦 Equipment", self.show_equipment),
                ("📊 Reports", self.show_reports)
            ])
        elif self.role == "Teacher":
            nav_items.extend([
                ("🏫 View Rooms", self.show_rooms),
                ("📖 Book Room / Lab", self.show_booking),
                ("🗓️ My Bookings", self.show_my_bookings),
                ("📅 My Timetable", self.show_timetable)
            ])
        elif self.role == "Student":
            nav_items.append(("📅 View Timetable", self.show_timetable))
        nav_items.append(("🔒 Logout", self.handle_logout))

        for text, command in nav_items:
            btn = tk.Button(self.sidebar, text=text, command=command, bg="#1E8449", fg="white", 
                            relief="flat", padx=20, pady=10, activebackground="#27AE60", cursor="hand2")
            btn.pack(fill="x", padx=10, pady=5)

        self.show_home()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # --- HOME & NOTICE BOARD ---
    def show_home(self):
        self.clear_content()
        header = tk.Frame(self.content_area, bg="#E9F7EF")
        header.pack(fill="x", pady=20, padx=30)
        tk.Label(header, text=f"Welcome, {self.username}! ", font=("Arial", 22, "bold"), bg="#E9F7EF", fg="#145A32").pack(side="left")
        tk.Label(header, text=f"📅 {date.today()}", font=("Arial", 10), bg="#E9F7EF", fg="#145A32").pack(side="right", pady=10)

        notice_container = tk.LabelFrame(self.content_area, text=" 📢 Campus Notice Board ", font=("Arial", 12, "bold"), bg="#E9F7EF", padx=15, pady=15, fg="#145A32")
        notice_container.pack(fill="both", expand=True, padx=30, pady=10)

        notices = fetch_notices()
        if not notices:
            tk.Label(notice_container, text="No announcements yet.", font=("Arial", 10, "italic"), bg="#E9F7EF").pack(pady=20)
        else:
            canvas = tk.Canvas(notice_container, bg="#E9F7EF", highlightthickness=0)
            scrollbar = ttk.Scrollbar(notice_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#E9F7EF")
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            for _, title, msg, dt in notices:
                n_box = tk.Frame(scrollable_frame, bg="#D5F5E3", bd=1, relief="solid", padx=10, pady=5)
                n_box.pack(fill="x", pady=5)
                tk.Label(n_box, text=f"📝 {title}", font=("Arial", 11, "bold"), bg="#D5F5E3", fg="#145A32").pack(anchor="w")
                tk.Label(n_box, text=msg, font=("Arial", 10), bg="#D5F5E3", wraplength=600, justify="left").pack(anchor="w")
                tk.Label(n_box, text=f"📆 {dt}", font=("Arial", 8), bg="#D5F5E3", fg="#1E8449").pack(anchor="e")

        if self.role in ["Admin", "Teacher"]:
            post_frame = tk.LabelFrame(self.content_area, text=" ✏️ Post New Notice ", bg="#E9F7EF", padx=10, pady=10, fg="#145A32")
            post_frame.pack(fill="x", padx=30, pady=20)
            tk.Label(post_frame, text="Title:", bg="#E9F7EF").grid(row=0, column=0, sticky="w")
            self.nt_title = tk.Entry(post_frame, width=50)
            self.nt_title.grid(row=0, column=1, padx=5, pady=5)
            tk.Label(post_frame, text="Notice:", bg="#E9F7EF").grid(row=1, column=0, sticky="nw")
            self.nt_msg = tk.Text(post_frame, width=50, height=3)
            self.nt_msg.grid(row=1, column=1, padx=5, pady=5)
            tk.Button(post_frame, text="📤 Post Update", bg="#1E8449", fg="white", command=self.handle_post_notice).grid(row=1, column=2, padx=10, sticky="s")

    def handle_post_notice(self):
        t, m = self.nt_title.get(), self.nt_msg.get("1.0", tk.END).strip()
        if t and m:
            add_notice(t, m, str(date.today()))
            add_log(self.username, f"Posted Notice: {t}")
            messagebox.showinfo("Success", "Notice Posted!")
            self.show_home()
        else:
            messagebox.showwarning("Incomplete", "Fill all fields! ⚠️")

    # --- REPORTS & ANALYTICS ---
    def show_reports(self):
        self.clear_content()
        header_frame = tk.Frame(self.content_area, bg="#E9F7EF")
        header_frame.pack(fill="x", padx=20, pady=15)
        tk.Label(header_frame, text="📊 Campus Analytics", font=("Arial", 20, "bold"), bg="#E9F7EF", fg="#145A32").pack(side="left")
        tk.Button(header_frame, text="📜 View Audit Logs", bg="#1E8449", fg="white", font=("Arial", 10), command=self.view_audit_logs, padx=10).pack(side="right")

        stats_frame = tk.Frame(self.content_area, bg="#E9F7EF")
        stats_frame.pack(fill="x", padx=20)
        room_data, eq_data = get_analytics_data()
        total_bookings = sum(row[1] for row in room_data)
        total_items = sum(row[1] for row in eq_data)

        for val, label in [(total_bookings, "Total Bookings"), (total_items, "Inventory Items")]:
            card = tk.Frame(stats_frame, bg="#D5F5E3", width=220, height=80)
            card.pack(side="left", padx=10, pady=10)
            card.pack_propagate(False)
            tk.Label(card, text=val, font=("Arial", 18, "bold"), fg="#145A32", bg="#D5F5E3").pack(pady=5)
            tk.Label(card, text=label, font=("Arial", 9), fg="#145A32", bg="#D5F5E3").pack()

        chart_frame = tk.Frame(self.content_area, bg="#E9F7EF", relief="groove", bd=1)
        chart_frame.pack(fill="both", expand=True, padx=30, pady=20)
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)
        fig.patch.set_facecolor('#E9F7EF')
        rooms = [r[0] for r in room_data]
        counts = [r[1] for r in room_data]
        ax.bar(rooms, counts, color='#1E8449')
        ax.set_title("Room Booking Frequency", fontsize=12, fontweight='bold')
        ax.set_ylabel("No. of Bookings")
        ax.set_xticks(range(len(rooms)))
        ax.set_xticklabels(rooms, rotation=45, ha='right', fontsize=9)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def view_audit_logs(self):
        self.clear_content()
        header = tk.Frame(self.content_area, bg="#E9F7EF")
        header.pack(fill="x", padx=20, pady=15)
        tk.Button(header, text="← Back to Charts", command=self.show_reports, bg="#27AE60", fg="white").pack(side="left")
        tk.Label(header, text="📜 System Audit Logs", font=("Arial", 18, "bold"), bg="#E9F7EF", fg="#145A32").pack(side="left", padx=20)

        log_frame = tk.Frame(self.content_area, bg="#E9F7EF")
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        cols = ("User", "Action", "Timestamp")
        tree = ttk.Treeview(log_frame, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        tree.column("User", width=120); tree.column("Action", width=450); tree.column("Timestamp", width=180)
        for log in fetch_logs(): tree.insert("", "end", values=log)
        tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(log_frame, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y"); tree.configure(yscrollcommand=sb.set)

    # --- ROOMS & BOOKINGS ---
    def show_rooms(self):
        self.clear_content()
        tk.Label(self.content_area, text="🏢 Campus Directory", font=("Arial", 18, "bold"), bg="#E9F7EF", fg="#145A32").pack(pady=10)
        search_frame = tk.Frame(self.content_area, bg="#E9F7EF")
        search_frame.pack(fill="x", padx=20, pady=5)
        self.search_entry = tk.Entry(search_frame, width=25); self.search_entry.pack(side="left", padx=10)
        tk.Button(search_frame, text="🔍 Search", command=self.handle_search, bg="#1E8449", fg="white").pack(side="left")
        tk.Button(search_frame, text="🔄 Refresh", command=self.refresh_room_list, bg="#27AE60", fg="white").pack(side="left", padx=5)

        room_container = tk.LabelFrame(self.content_area, text=" Rooms & Labs ", bg="#E9F7EF", fg="#145A32")
        room_container.pack(fill="both", expand=True, padx=20, pady=10)
        cols = ("id", "name", "type", "capacity", "location")
        self.room_tree = ttk.Treeview(room_container, columns=cols, show="headings", height=8)
        for c in cols: self.room_tree.heading(c, text=c.capitalize())
        self.room_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.refresh_room_list()

        if self.role == "Admin":
            book_frame = tk.LabelFrame(self.content_area, text=" Global Booking Management ", bg="#E9F7EF", fg="#145A32")
            book_frame.pack(fill="both", expand=True, padx=20, pady=10)
            b_cols = ("id", "room", "user", "date", "slot", "purpose")
            self.admin_book_tree = ttk.Treeview(book_frame, columns=b_cols, show="headings", height=6)
            for c in b_cols: self.admin_book_tree.heading(c, text=c.capitalize())
            self.admin_book_tree.pack(fill="both", expand=True, padx=5, pady=5)
            tk.Button(book_frame, text="🗑️ Cancel Booking", bg="#C0392B", fg="white", command=self.handle_admin_delete).pack(pady=5, anchor="e", padx=5)
            self.refresh_admin_bookings()

    def refresh_room_list(self):
        for i in self.room_tree.get_children(): self.room_tree.delete(i)
        for row in fetch_all_resources(): self.room_tree.insert("", "end", values=row)

    def handle_search(self):
        res = search_resources(self.search_entry.get())
        for i in self.room_tree.get_children(): self.room_tree.delete(i)
        for row in res: self.room_tree.insert("", "end", values=row)

    def refresh_admin_bookings(self):
        for i in self.admin_book_tree.get_children(): self.admin_book_tree.delete(i)
        conn = sqlite3.connect('smart_campus.db'); data = conn.execute("SELECT * FROM bookings").fetchall(); conn.close()
        for row in data: self.admin_book_tree.insert("", "end", values=row)

    def handle_admin_delete(self):
        sel = self.admin_book_tree.selection()
        if sel:
            bid = self.admin_book_tree.item(sel)['values'][0]
            if messagebox.askyesno("Confirm", f"Cancel booking ID #{bid}?"):
                delete_booking(bid)
                add_log(self.username, f"Admin Cancelled Booking ID: {bid}")
                self.refresh_admin_bookings()

    # --- BOOK ROOM ---
    def show_booking(self):
        self.clear_content()
        tk.Label(self.content_area, text="📖 Reserve a Room", font=("Arial", 18, "bold"), bg="#E9F7EF", fg="#145A32").pack(pady=20)
        room_list = [f"{r[0]} - {r[1]} ({r[2]})" for r in fetch_all_resources()]
        form = tk.Frame(self.content_area, bg="#D5F5E3", padx=40, pady=40, relief="groove", bd=1)
        form.pack()
        tk.Label(form, text="Room:", bg="#D5F5E3", font=("Arial", 10, "bold")).grid(row=0, column=0, pady=10, sticky="e")
        self.book_cb = ttk.Combobox(form, values=room_list, state="readonly", width=40); self.book_cb.grid(row=0, column=1, padx=10)
        tk.Label(form, text="Date:", bg="#D5F5E3", font=("Arial", 10, "bold")).grid(row=1, column=0, pady=10, sticky="e")
        self.date_ent = tk.Entry(form, width=43); self.date_ent.insert(0, str(date.today())); self.date_ent.grid(row=1, column=1, padx=10)
        tk.Label(form, text="Slot:", bg="#D5F5E3", font=("Arial", 10, "bold")).grid(row=2, column=0, pady=10, sticky="e")
        self.slot_cb = ttk.Combobox(form, values=["08:00-09:30", "09:30-11:00", "11:00-12:30","12:30-14:00", "14:00-15:30"], state="readonly", width=40); self.slot_cb.grid(row=2, column=1, padx=10)
        tk.Label(form, text="Purpose:", bg="#D5F5E3", font=("Arial", 10, "bold")).grid(row=3, column=0, pady=10, sticky="e")
        self.purpose_cb = ttk.Combobox(form, values=["Lecture", "Lab", "Meeting","Exam", "Study"], state="readonly", width=40); self.purpose_cb.grid(row=3, column=1, padx=10)
        tk.Button(form, text="✅ Confirm Reservation", bg="#1E8449", fg="white", font=("Arial", 11, "bold"), command=self.handle_book, width=25).grid(row=4, columnspan=2, pady=30)

    def handle_book(self):
        r_raw, d, s, p = self.book_cb.get(), self.date_ent.get(), self.slot_cb.get(), self.purpose_cb.get()
        if r_raw and s:
            rid = r_raw.split(" - ")[0]
            if is_room_available(rid, d, s):
                save_booking(rid, self.username, d, s, p)
                add_log(self.username, f"Booked Room ID: {rid} for {d}")
                messagebox.showinfo("Success", "Reserved! ✅")
                self.show_my_bookings()
            else:
                messagebox.showerror("Conflict", "Already Booked! ⚠️")
        else:
            messagebox.showwarning("Error", "Missing Info! ⚠️")

    # --- MY BOOKINGS ---
    def show_my_bookings(self):
        self.clear_content()
        tk.Label(self.content_area, text="🗓️ My Active Reservations", font=("Arial", 18, "bold"), bg="#E9F7EF", fg="#145A32").pack(pady=10)
        cols = ("id", "room", "user", "date", "slot", "purpose")
        self.my_book_tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: self.my_book_tree.heading(c, text=c.capitalize())
        self.my_book_tree.pack(fill="both", expand=True, padx=20, pady=10)
        conn = sqlite3.connect('smart_campus.db'); data = conn.execute("SELECT * FROM bookings WHERE username=?", (self.username,)).fetchall(); conn.close()
        for row in data: self.my_book_tree.insert("", "end", values=row)

        btn_frame = tk.Frame(self.content_area, bg="#E9F7EF"); btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔄 Refresh My Bookings", command=self.show_my_bookings, bg="#27AE60", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑️ Cancel Reservation", bg="#C0392B", fg="white", command=self.handle_teacher_delete).pack(side="left", padx=5)

    def handle_teacher_delete(self):
        sel = self.my_book_tree.selection()
        if sel:
            bid = self.my_book_tree.item(sel)['values'][0]
            if messagebox.askyesno("Confirm", "Cancel? ⚠️"):
                delete_booking(bid)
                add_log(self.username, f"Cancelled own Booking ID: {bid}")
                self.show_my_bookings()

    # --- TIMETABLE ---
    def show_timetable(self):
        self.clear_content()
        tk.Label(self.content_area, text="📅 Class Schedule", font=("Arial", 18, "bold"), bg="#E9F7EF", fg="#145A32").pack(pady=10)
        cols = ("id", "room", "booked_by", "date", "time", "purpose")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c.capitalize())
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        conn = sqlite3.connect('smart_campus.db')
        data = conn.execute("SELECT * FROM bookings").fetchall() if self.role == "Student" else conn.execute("SELECT * FROM bookings WHERE username=?", (self.username,)).fetchall()
        conn.close()
        for row in data: tree.insert("", "end", values=row)

    # --- EQUIPMENT ---
    def show_equipment(self):
        self.clear_content()
        tk.Label(self.content_area, text="📦 Inventory Management", font=("Arial", 18, "bold"), bg="#E9F7EF", fg="#145A32").pack(pady=10)
        
        if self.role == "Admin":
            mf = tk.LabelFrame(self.content_area, text=" Quick Add Item ", bg="#E9F7EF", padx=10, pady=10, font=("Arial", 9, "bold"), fg="#145A32")
            mf.pack(fill="x", padx=20, pady=5)
            tk.Label(mf, text="Item Name", bg="#E9F7EF", font=("Arial", 8)).grid(row=0, column=0, sticky="w", padx=5)
            tk.Label(mf, text="Qty", bg="#E9F7EF", font=("Arial", 8)).grid(row=0, column=1, sticky="w", padx=5)
            tk.Label(mf, text="Assigned Room", bg="#E9F7EF", font=("Arial", 8)).grid(row=0, column=2, sticky="w", padx=5)
            self.eq_n = tk.Entry(mf, width=20); self.eq_n.grid(row=1, column=0, padx=5, pady=2)
            self.eq_q = tk.Entry(mf, width=8); self.eq_q.grid(row=1, column=1, padx=5, pady=2)
            self.eq_r = tk.Entry(mf, width=20); self.eq_r.grid(row=1, column=2, padx=5, pady=2)
            tk.Button(mf, text="➕ Add Item", bg="#27AE60", fg="white", font=("Arial", 9, "bold"), command=self.handle_add_eq, padx=10).grid(row=1, column=3, padx=15)

        cols = ("id", "item", "qty", "room", "status")
        self.eq_tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: self.eq_tree.heading(c, text=c.upper())
        self.eq_tree.pack(fill="both", expand=True, padx=20, pady=10)

        btn_frame = tk.Frame(self.content_area, bg="#E9F7EF"); btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔄 Refresh List", bg="#27AE60", fg="white", command=self.refresh_eq, padx=10).pack(side="left", padx=5)
        if self.role == "Admin":
            tk.Button(btn_frame, text="🗑️ Delete Selected", bg="#C0392B", fg="white", command=self.handle_del_eq, padx=10).pack(side="left", padx=5)

        self.refresh_eq()

    def refresh_eq(self):
        for i in self.eq_tree.get_children(): self.eq_tree.delete(i)
        for row in fetch_all_equipment(): self.eq_tree.insert("", "end", values=row)

    def handle_add_eq(self):
        from database.db_manager import add_equipment
        try:
            name = self.eq_n.get()
            add_equipment(name, int(self.eq_q.get()), self.eq_r.get())
            add_log(self.username, f"Added Equipment: {name}")
            self.refresh_eq()
        except:
            messagebox.showerror("Error", "Check inputs! ⚠️")

    def handle_del_eq(self):
        sel = self.eq_tree.selection()
        if sel:
            eid = self.eq_tree.item(sel)['values'][0]
            from database.db_manager import delete_equipment
            delete_equipment(eid)
            add_log(self.username, f"Deleted Equipment ID: {eid}")
            self.refresh_eq()

    # --- LOGOUT ---
    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure? 🔒"):
            self.controller.show_login()
            self.destroy()
