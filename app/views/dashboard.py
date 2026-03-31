"""
Single parameterised Dashboard class — replaces dashboard_dark.py and
dashboard_light.py.  Theme colours are injected via a ThemePalette instance.

Usage:
    from app.views.dashboard import Dashboard, DARK_PALETTE, LIGHT_PALETTE
    Dashboard(session, DARK_PALETTE)
"""

from __future__ import annotations

import threading
import queue as _queue
from dataclasses import dataclass
from datetime import datetime

import cv2
import PIL.Image
import PIL.ImageTk
from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox, Style, Treeview
from tkinter.simpledialog import askstring
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import secrets

import app.state as state
from app.session import AppSession
from app.camera.video_capture import MyVideoCapture
from app.camera.mask_detector import detect, MASKED, UNMASKED
from app.camera.tracker import PersonTracker
from app.paths import Images
from app.db import locations as db_locations
from app.db import surveillance as db_surv
from app.db import cities as db_cities
from app.db import users as db_users
from app.security import hash_password
from app import theme
from app.logger import get
import otp

_log = get(__name__)


# ── Theme Palette ─────────────────────────────────────────────────────────────

@dataclass
class ThemePalette:
    name:              str    # "dark" | "light"
    bg:                str    # window / main-area background
    panel:             str    # nav bar + sidebar background
    panel2:            str    # bottom bar background
    card:              str    # card / dialog background
    panel_fg:          str    # text colour ON the panel (navbar, sidebar headers)
    panel_muted:       str    # secondary / hint text ON the panel background
    fg:                str    # general label / content text
    inp:               str    # input field background
    border:            str    # separator / border colour
    muted:             str    # de-emphasised / hint text
    # sidebar read-only entries (date, time, percentages)
    entry_bg:          str
    entry_disabled_bg: str
    entry_disabled_fg: str
    entry_border:      str
    # toggle-theme button
    toggle_label:      str
    toggle_bg:         str


DARK_PALETTE = ThemePalette(
    name              = "dark",
    bg                = theme.D_BG,
    panel             = theme.D_PANEL,
    panel2            = theme.D_PANEL2,
    card              = theme.D_CARD,
    panel_fg          = theme.D_FG,
    panel_muted       = "#9399b2",   # slightly lighter than D_MUTED, readable on dark panel
    fg                = theme.D_FG,
    inp               = theme.D_INPUT,
    border            = theme.D_BORDER,
    muted             = theme.D_MUTED,
    entry_bg          = theme.D_INPUT,
    entry_disabled_bg = theme.D_INPUT,
    entry_disabled_fg = theme.D_MUTED,
    entry_border      = theme.D_BORDER,
    toggle_label      = "☀️  Light Mode",
    toggle_bg         = theme.L_PANEL,
)

LIGHT_PALETTE = ThemePalette(
    name              = "light",
    bg                = theme.L_BG,
    panel             = theme.L_PANEL,
    panel2            = theme.L_PANEL2,
    card              = theme.L_CARD,
    panel_fg          = theme.L_FG,
    panel_muted       = "#c8d8f8",   # light blue-white, readable on blue panel
    fg                = theme.L_TEXT,
    inp               = theme.L_INPUT,
    border            = theme.L_BORDER,
    muted             = theme.L_MUTED,
    entry_bg          = "#2a63c8",
    entry_disabled_bg = "#2a63c8",
    entry_disabled_fg = "#a8c8f8",
    entry_border      = "#4a90d9",
    toggle_label      = "🌙  Dark Mode",
    toggle_bg         = theme.D_PANEL,
)

# ─────────────────────────────────────────────────────────────────────────────


class Dashboard:
    """Main application dashboard — works for both dark and light themes."""

    # ── navigation guards ─────────────────────────────────────────────────────

    def _nav_guard(self) -> bool:
        if self.flag:
            ans = askyesnocancel(
                "Surveillance In Progress",
                "A surveillance session is currently recording.\n\n"
                "Yes    — Stop camera and SAVE this session, then switch.\n"
                "No     — Stop camera WITHOUT saving, then switch.\n"
                "Cancel — Stay on the current view."
            )
            if ans is None:
                return False
            self.stop_camera()
            if ans:
                self.sur()
            return True

        if str(self.submit["state"]) == NORMAL:
            ans = askyesnocancel(
                "Unsaved Surveillance Data",
                "You have a surveillance session that has not been saved.\n\n"
                "Yes    — SAVE this session, then switch.\n"
                "No     — Switch WITHOUT saving (data will be lost).\n"
                "Cancel — Stay on the current view."
            )
            if ans is None:
                return False
            if ans:
                self.sur()
            return True

        return True

    def _clear_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()
        self._chart_widget = None
        self._placeholder  = None
        self._current_panel = None

    def _restore_placeholder(self):
        P = self.P
        self._clear_main()
        self._set_active_nav("")
        self._placeholder = Frame(self.main_frame, bg=P.bg)
        self._placeholder.place(relx=0.5, rely=0.5, anchor=CENTER)

        # ── Stats summary row ─────────────────────────────────────────────────
        from app.db import complaints as _dbc_stats
        try:
            pending_count  = _dbc_stats.count_by_status("Pending")
            sessions_today = db_surv.count_today()
        except Exception:
            pending_count  = "—"
            sessions_today = "—"

        stats_row = Frame(self._placeholder, bg=P.bg)
        stats_row.pack(pady=(0, 24))
        for label, value, nav_fn in [
            ("Pending Complaints", pending_count,  self.show_complaints),
            ("Sessions Today",     sessions_today, self.show_history),
        ]:
            card = Frame(stats_row, bg=P.card, padx=28, pady=18, cursor="hand2")
            card.pack(side=LEFT, padx=12)
            lbl_val  = Label(card, text=str(value), font=('Helvetica', 30, 'bold'),
                             bg=P.card, fg=P.fg)
            lbl_val.pack()
            lbl_name = Label(card, text=label, font=theme.F_SMALL,
                             bg=P.card, fg=P.muted)
            lbl_name.pack()
            for w in (card, lbl_val, lbl_name):
                w.bind("<Button-1>", lambda e, fn=nav_fn: fn())

        # ── Idle prompt ───────────────────────────────────────────────────────
        Label(self._placeholder, text="📷",
              font=('Helvetica', 40), bg=P.bg, fg=P.muted).pack()
        Label(self._placeholder,
              text="Select a location and press  ▶ Start",
              font=theme.F_SUB, bg=P.bg, fg=P.fg).pack(pady=(8, 4))
        Label(self._placeholder,
              text="Results and compliance chart will appear here after the session.",
              font=theme.F_SMALL, bg=P.bg, fg=P.muted).pack()

    # ── treeview helper ───────────────────────────────────────────────────────

    def _style_tree(self) -> Style:
        """Apply theme-appropriate treeview style and return the Style object."""
        P = self.P
        s = Style()
        if P.name == "dark":
            theme.style_treeview(s, bg=P.card, fg=P.fg,
                                 heading_bg=P.panel, heading_fg=P.fg,
                                 row_bg=P.inp, alt_bg=P.panel2)
        else:
            theme.style_treeview(s)
        return s

    def _tag_tree(self, tree):
        """Configure even/odd row tags on a Treeview widget."""
        P = self.P
        tree.tag_configure('even', background=P.inp,  foreground=P.fg)
        tree.tag_configure('odd',  background=P.card, foreground=P.fg)

    # ── admin management ──────────────────────────────────────────────────────

    def manage_admins(self):
        if not self._nav_guard():
            return
        self._clear_main()
        self._set_active_nav("admins")
        P = self.P

        panel = Frame(self.main_frame, bg=P.bg)
        panel.pack(fill=BOTH, expand=True)
        self._current_panel = panel

        hdr = Frame(panel, bg=P.panel, height=50)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        theme.btn(hdr, "← Dashboard", self._restore_placeholder,
                  width=130).pack(side=LEFT, padx=12, pady=8)
        Label(hdr, text="👥  Admin Management",
              font=theme.F_SUB, bg=P.panel, fg=P.panel_fg).pack(side=LEFT, padx=8)

        content = Frame(panel, bg=P.bg)
        content.pack(fill=BOTH, expand=True, padx=16, pady=16)

        # ── Left: Add Admin form ─────────────────────────────────────────────
        left = Frame(content, bg=P.card, padx=20, pady=16)
        left.pack(side=LEFT, fill=Y, padx=(0, 12))

        Label(left, text="Add New Admin",
              font=theme.F_SUB, bg=P.card, fg=P.fg).pack(pady=(0, 10))
        Frame(left, bg=P.border, height=1).pack(fill=X, pady=(0, 10))

        entry_cfg = dict(font=theme.F_ENTRY, width=26,
                         bg=P.inp, fg=P.fg, relief=FLAT,
                         highlightthickness=1, highlightbackground=P.border,
                         highlightcolor=P.panel, insertbackground=P.fg)

        Label(left, text="Username", font=theme.F_BODY, bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
        e_username = Entry(left, **entry_cfg)
        e_username.pack(ipady=6, pady=(2, 8), fill=X)

        Label(left, text="Email", font=theme.F_BODY, bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
        e_email = Entry(left, **entry_cfg)
        e_email.pack(ipady=6, pady=(2, 8), fill=X)

        Label(left, text="Password", font=theme.F_BODY, bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
        e_password = Entry(left, show="●", **entry_cfg)
        e_password.pack(ipady=6, pady=(2, 8), fill=X)

        Label(left, text="Role", font=theme.F_BODY, bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
        e_role = Combobox(left, values=('Super Admin', 'Admin'),
                          font=theme.F_ENTRY, width=24, state='readonly')
        e_role.pack(ipady=4, pady=(2, 16), fill=X)

        def do_send_otp():
            username = e_username.get().strip()
            email    = e_email.get().strip()
            password = e_password.get()
            role     = e_role.get()
            if not username or not email or not password or not role:
                showerror("Missing Fields", "Please fill in all fields.")
                return
            if db_users.get_by_email(email) is not None:
                showerror("Duplicate", "An account with this email already exists.")
                return
            try:
                otp_code = otp.send(email, purpose="verify")
            except otp.OTPSendError as e:
                showerror("Email Error", str(e))
                return

            otp_win = Toplevel(self.root)
            otp_win.title("Verify Admin Email")
            otp_win.resizable(False, False)
            otp_win.configure(bg=P.card)
            ox = (otp_win.winfo_screenwidth()  // 2) - 210
            oy = (otp_win.winfo_screenheight() // 2) - 140
            otp_win.geometry(f"420x320+{ox}+{oy}")
            otp_win.grab_set()

            f = Frame(otp_win, bg=P.card, padx=36, pady=28)
            f.pack(fill=BOTH, expand=True)
            Label(f, text="🔐  Verify Admin Email",
                  font=theme.F_HEAD, bg=P.card, fg=P.fg).pack(pady=(0, 6))
            Label(f, text=f"OTP sent to: {email}",
                  font=theme.F_SMALL, bg=P.card, fg=P.muted).pack(pady=(0, 16))
            e_otp = Entry(f, font=('Helvetica', 18, 'bold'), width=12,
                          justify=CENTER, bg=P.inp, fg=P.panel,
                          relief=FLAT, highlightthickness=1,
                          highlightbackground=P.border,
                          highlightcolor=P.panel, insertbackground=P.panel)
            e_otp.pack(ipady=10, pady=(0, 8))
            e_otp.focus()

            _attempts_left = [3]
            lbl_otp_attempts = Label(f, text="3 attempts remaining",
                                     font=theme.F_SMALL, bg=P.card, fg=P.muted)
            lbl_otp_attempts.pack(pady=(0, 12))

            def verify():
                if secrets.compare_digest(str(otp_code), str(e_otp.get())):
                    db_users.create(username, email, hash_password(password), role)
                    showinfo("Success", "Admin account created successfully.")
                    otp_win.destroy()
                    e_username.delete(0, END)
                    e_email.delete(0, END)
                    e_password.delete(0, END)
                    refresh_tree()
                elif e_otp.get() == "":
                    showerror("Error", "Please enter the OTP.")
                else:
                    _attempts_left[0] -= 1
                    if _attempts_left[0] <= 0:
                        otp_win.destroy()
                        showerror("Too Many Attempts",
                                  "Too many incorrect attempts. Please try again later.")
                        return
                    rem = _attempts_left[0]
                    lbl_otp_attempts.config(
                        text=f"{rem} attempt{'s' if rem != 1 else ''} remaining",
                        fg=theme.DANGER,
                    )
                    showerror("Error", "Incorrect OTP. Please try again.")

            otp_win.bind('<Return>', lambda ev: verify())
            theme.btn(f, "Verify & Create Account", verify,
                      bg=theme.SUCCESS, width=260).pack()

        theme.btn(left, "📨  Send OTP & Create", do_send_otp, width=220).pack(pady=(4, 0))

        # ── Right: View/Edit Admins treeview ─────────────────────────────────
        right = Frame(content, bg=P.bg)
        right.pack(side=LEFT, fill=BOTH, expand=True)

        Label(right, text="All Admins",
              font=theme.F_SUB, bg=P.bg, fg=P.fg, anchor=W).pack(fill=X, pady=(0, 4))
        Label(right, text="Double-click a row to edit or delete.",
              font=theme.F_SMALL, bg=P.bg, fg=P.muted, anchor=W).pack(fill=X, pady=(0, 6))

        self._style_tree()
        tree_frame = Frame(right, bg=P.bg)
        tree_frame.pack(fill=BOTH, expand=True)

        col = ('Username', 'Email', 'Role')
        tree = Treeview(tree_frame, columns=col,
                        style="Custom.Treeview", selectmode='browse')
        for c in col:
            tree.heading(c, text=c)
        tree.column('Username', width=220, anchor=W)
        tree.column('Email',    width=300, anchor=W)
        tree.column('Role',     width=150, anchor=CENTER)
        tree['show'] = 'headings'
        self._tag_tree(tree)

        sb = Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=True)

        def refresh_tree():
            for k in tree.get_children():
                tree.delete(k)
            for i, row in enumerate(db_users.get_all()):
                tree.insert('', END, values=list(row),
                            tags=('even' if i % 2 == 0 else 'odd',))

        def on_double_click(event):
            items = tree.item(tree.focus())['values']
            if not items:
                return
            dlg = Toplevel(self.root)
            dlg.title("Edit Admin")
            dlg.resizable(False, False)
            dlg.configure(bg=P.card)
            dx = (dlg.winfo_screenwidth()  // 2) - 240
            dy = (dlg.winfo_screenheight() // 2) - 200
            dlg.geometry(f"480x380+{dx}+{dy}")
            dlg.grab_set()

            f = Frame(dlg, bg=P.card, padx=36, pady=28)
            f.pack(fill=BOTH, expand=True)
            Label(f, text="Edit Admin Account",
                  font=theme.F_HEAD, bg=P.card, fg=P.fg).pack(pady=(0, 20))

            Label(f, text="Email (read-only)", font=theme.F_BODY,
                  bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
            e_em = Entry(f, font=theme.F_ENTRY, width=44,
                         bg=P.inp, fg=P.muted,
                         relief=FLAT, highlightthickness=1,
                         highlightbackground=P.border)
            e_em.pack(ipady=6, pady=(2, 12))
            e_em.insert(0, items[1])
            e_em.config(state='readonly')

            Label(f, text="Username", font=theme.F_BODY,
                  bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
            e_un = Entry(f, font=theme.F_ENTRY, width=44,
                         bg=P.inp, fg=P.fg, relief=FLAT,
                         highlightthickness=1, highlightbackground=P.border,
                         highlightcolor=P.panel, insertbackground=P.fg)
            e_un.pack(ipady=6, pady=(2, 12))
            e_un.insert(0, items[0])

            Label(f, text="Role", font=theme.F_BODY,
                  bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
            e_rl = Combobox(f, values=['Super Admin', 'Admin'],
                            font=theme.F_ENTRY, width=42, state='readonly')
            e_rl.pack(ipady=4, pady=(2, 20))
            e_rl.current(['Super Admin', 'Admin'].index(items[2]))

            btn_row = Frame(f, bg=P.card)
            btn_row.pack()

            def do_update():
                db_users.update(e_em.get(), e_un.get(), e_rl.get())
                showinfo("Updated", "Admin updated successfully.")
                refresh_tree()
                dlg.destroy()

            def do_delete():
                if askyesno("Confirm",
                            f"Delete admin '{items[0]}'? This cannot be undone."):
                    db_users.delete(e_em.get())
                    refresh_tree()
                    dlg.destroy()

            theme.btn(btn_row, "💾  Update", do_update,
                      bg=P.panel, width=160).grid(row=0, column=0, padx=8)
            theme.btn(btn_row, "🗑  Delete", do_delete,
                      bg=theme.DANGER, width=160).grid(row=0, column=1, padx=8)

        tree.bind('<Double-1>', on_double_click)
        refresh_tree()

    # ── complaints ────────────────────────────────────────────────────────────

    def show_complaints(self):
        if not self._nav_guard():
            return
        self._clear_main()
        self._set_active_nav("complaints")
        P = self.P

        panel = Frame(self.main_frame, bg=P.bg)
        panel.pack(fill=BOTH, expand=True)
        self._current_panel = panel

        hdr = Frame(panel, bg=P.panel, height=50)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        theme.btn(hdr, "← Dashboard", self._restore_placeholder,
                  width=130).pack(side=LEFT, padx=12, pady=8)
        Label(hdr, text="📋  Registered Complaints",
              font=theme.F_SUB, bg=P.panel, fg=P.panel_fg).pack(side=LEFT, padx=8)

        bar = Frame(panel, bg=P.card, pady=10)
        bar.pack(fill=X, padx=16, pady=(10, 0))
        Label(bar, text="Filter by Location:",
              font=theme.F_BODY, bg=P.card, fg=P.fg).pack(side=LEFT, padx=(12, 8))

        s = Style()
        s.configure('my.TCombobox', arrowsize=20)
        self._style_tree()

        loc_values = db_locations.get_all() + ["All Locations"]
        s_loc_cb = Combobox(bar, values=loc_values, font=theme.F_ENTRY,
                            width=24, state='readonly', style='my.TCombobox')
        s_loc_cb.pack(side=LEFT, ipady=4, padx=(0, 10))
        s_loc_cb.set("All Locations")

        tree_frame = Frame(panel, bg=P.bg)
        tree_frame.pack(fill=BOTH, expand=True, padx=16, pady=10)

        col = ('ID', 'Name', 'Mobile', 'Email', 'Report', 'Location', 'Status')
        tree = Treeview(tree_frame, columns=col,
                        style="Custom.Treeview", selectmode='browse')
        for c in col:
            tree.heading(c, text=c)
        widths = {'ID': 50, 'Name': 140, 'Mobile': 110, 'Email': 190,
                  'Report': 250, 'Location': 150, 'Status': 190}
        for c in col:
            tree.column(c, width=widths.get(c, 120), anchor=W)
        tree['show'] = 'headings'
        self._tag_tree(tree)

        sb  = Scrollbar(tree_frame, orient=VERTICAL,   command=tree.yview)
        sbh = Scrollbar(tree_frame, orient=HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=sb.set, xscrollcommand=sbh.set)
        sb.pack(side=RIGHT, fill=Y)
        sbh.pack(side=BOTTOM, fill=X)
        tree.pack(fill=BOTH, expand=True)

        def do_search():
            s_val = s_loc_cb.get()
            from app.db import complaints as _dbc
            rows = (_dbc.get_all() if s_val in ("All Locations", "")
                    else _dbc.get_by_location(s_val))
            for k in tree.get_children():
                tree.delete(k)
            for i, row in enumerate(rows):
                tree.insert('', END, values=row,
                            tags=('even' if i % 2 == 0 else 'odd',))

        theme.btn(bar, "🔍  Search", do_search, width=120).pack(side=LEFT, padx=4)
        do_search()

        from app.db import complaints as _dbc

        def on_complaint_click(event):
            item_id = tree.focus()
            if not item_id:
                return
            values = tree.item(item_id)['values']
            if not values:
                return
            cid, name, mobile, email_val, report, location, current_status = values

            dlg = Toplevel(self.root)
            dlg.title(f"Complaint #{cid}")
            dlg.resizable(False, False)
            dlg.configure(bg=P.card)
            dx = (dlg.winfo_screenwidth()  // 2) - 210
            dy = (dlg.winfo_screenheight() // 2) - 175
            dlg.geometry(f"420x340+{dx}+{dy}")
            dlg.grab_set()

            df = Frame(dlg, bg=P.card, padx=30, pady=20)
            df.pack(fill=BOTH, expand=True)
            Label(df, text=f"Complaint #{cid}",
                  font=theme.F_HEAD, bg=P.card, fg=P.fg).pack(pady=(0, 6))
            Frame(df, bg=P.border, height=1).pack(fill=X, pady=(0, 10))

            for lbl_text, val in [("Name",     name),
                                   ("Location", location),
                                   ("Report",   report),
                                   ("Status",   current_status)]:
                row_f = Frame(df, bg=P.card)
                row_f.pack(fill=X, pady=2)
                Label(row_f, text=f"{lbl_text}:", font=theme.F_SMALL,
                      bg=P.card, fg=P.muted, width=9, anchor=W).pack(side=LEFT)
                Label(row_f, text=str(val), font=theme.F_BODY,
                      bg=P.card, fg=P.fg, anchor=W).pack(side=LEFT)

            Frame(df, bg=P.border, height=1).pack(fill=X, pady=(10, 8))
            Label(df, text="Change Status:", font=theme.F_BODY,
                  bg=P.card, fg=P.fg, anchor=W).pack(fill=X)

            _STATUS_OPTS = ["Pending", "Under Review", "Surveillance Done", "Dismissed"]
            status_cb = Combobox(df, values=_STATUS_OPTS, font=theme.F_ENTRY,
                                 width=30, state='readonly')
            status_cb.pack(ipady=4, pady=(4, 14), fill=X)
            try:
                status_cb.current(_STATUS_OPTS.index(str(current_status)))
            except ValueError:
                status_cb.current(0)

            def do_update_status():
                new_status = status_cb.get()
                _dbc.update_status_by_id(int(cid), new_status)
                showinfo("Updated",
                         f"Complaint #{cid} status updated to '{new_status}'.")
                dlg.destroy()
                do_search()

            theme.btn(df, "Update Status", do_update_status, width=200).pack()

        tree.bind('<Double-1>', on_complaint_click)

    # ── surveillance history ──────────────────────────────────────────────────

    def show_history(self):
        if not self._nav_guard():
            return
        self._clear_main()
        self._set_active_nav("history")
        P = self.P

        panel = Frame(self.main_frame, bg=P.bg)
        panel.pack(fill=BOTH, expand=True)
        self._current_panel = panel

        hdr = Frame(panel, bg=P.panel, height=50)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        theme.btn(hdr, "← Dashboard", self._restore_placeholder,
                  width=130).pack(side=LEFT, padx=12, pady=8)
        Label(hdr, text="📜  Surveillance History",
              font=theme.F_SUB, bg=P.panel, fg=P.panel_fg).pack(side=LEFT, padx=8)

        # ── Filter bar ────────────────────────────────────────────────────────
        filter_bar = Frame(panel, bg=P.card, pady=8)
        filter_bar.pack(fill=X, padx=16, pady=(8, 0))

        _entry_sm = dict(font=theme.F_ENTRY, width=11,
                         bg=P.inp, fg=P.fg, relief=FLAT,
                         highlightthickness=1, highlightbackground=P.border,
                         insertbackground=P.fg)
        Label(filter_bar, text="From:", font=theme.F_BODY,
              bg=P.card, fg=P.fg).pack(side=LEFT, padx=(12, 4))
        hist_from = Entry(filter_bar, **_entry_sm)
        hist_from.pack(side=LEFT, ipady=4)
        hist_from.insert(0, "2020-01-01")

        Label(filter_bar, text="To:", font=theme.F_BODY,
              bg=P.card, fg=P.fg).pack(side=LEFT, padx=(8, 4))
        hist_to = Entry(filter_bar, **_entry_sm)
        hist_to.pack(side=LEFT, ipady=4)
        hist_to.insert(0, datetime.today().strftime("%Y-%m-%d"))

        Label(filter_bar, text="Location:", font=theme.F_BODY,
              bg=P.card, fg=P.fg).pack(side=LEFT, padx=(8, 4))
        _loc_hist_vals = ["All Locations"] + db_locations.get_all()
        hist_loc = Combobox(filter_bar, values=_loc_hist_vals,
                             font=theme.F_ENTRY, width=20, state='readonly',
                             style='my.TCombobox')
        hist_loc.pack(side=LEFT, ipady=4, padx=(0, 8))
        hist_loc.set("All Locations")

        self._style_tree()
        tree_frame = Frame(panel, bg=P.bg)
        tree_frame.pack(fill=BOTH, expand=True, padx=16, pady=(8, 16))

        col = ('ID', 'City', 'Place', 'Area', 'Date', 'Start', 'End',
               'Masked %', 'Unmasked %', 'Total Persons')
        tree = Treeview(tree_frame, columns=col,
                        style="Custom.Treeview", selectmode='browse')
        for c in col:
            tree.heading(c, text=c)
        widths = {'ID': 50, 'City': 110, 'Place': 150, 'Area': 120,
                  'Date': 100, 'Start': 80, 'End': 80,
                  'Masked %': 90, 'Unmasked %': 90, 'Total Persons': 90}
        for c in col:
            tree.column(c, width=widths.get(c, 90), anchor=CENTER)
        tree['show'] = 'headings'
        self._tag_tree(tree)

        sb  = Scrollbar(tree_frame, orient=VERTICAL,   command=tree.yview)
        sbh = Scrollbar(tree_frame, orient=HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=sb.set, xscrollcommand=sbh.set)
        sb.pack(side=RIGHT, fill=Y)
        sbh.pack(side=BOTTOM, fill=X)
        tree.pack(fill=BOTH, expand=True)

        def do_filter():
            from_d = hist_from.get().strip()
            to_d   = hist_to.get().strip()
            loc    = hist_loc.get()
            loc    = "" if loc in ("All Locations", "") else loc
            try:
                rows = db_surv.get_filtered(from_d, to_d, loc)
            except Exception:
                rows = db_surv.get_all()
            for k in tree.get_children():
                tree.delete(k)
            for i, row in enumerate(rows):
                tree.insert('', END, values=list(row),
                            tags=('even' if i % 2 == 0 else 'odd',))

        theme.btn(filter_bar, "Filter", do_filter, width=100).pack(side=LEFT)
        do_filter()

    # ── theme toggle + logout ─────────────────────────────────────────────────

    def _toggle_theme(self):
        other = DARK_PALETTE if self.P.name == "light" else LIGHT_PALETTE
        self.root.destroy()
        Dashboard(self.session, other)

    def _set_active_nav(self, name: str) -> None:
        """Highlight the named nav section button; restore all others."""
        self._active_section = name
        _ACTIVE = "#4a9aff"      # lighter highlight vs default L_PANEL #1a73e8
        _BASE   = theme.L_PANEL
        for section, sbtn in (("complaints", self._complaints_btn),
                               ("history",    self._history_btn),
                               ("admins",     self._admins_btn)):
            if sbtn._disabled:
                continue
            color = _ACTIVE if section == name else _BASE
            sbtn._bg       = color
            sbtn._hover_bg = theme.StyledButton._darken(color)
            sbtn._draw(color)

    def lg(self):
        if not askyesno("Logout", "Are you sure you want to logout?"):
            return
        self.root.destroy()
        from app.views.login import log
        log()

    # ── location management ───────────────────────────────────────────────────

    def _build_loc_map(self) -> list:
        rows = db_locations.get_all_with_city()
        self._loc_map = {}
        for s_loc, city, place_name, area in rows:
            if not city.strip():
                continue
            if place_name.strip() and area.strip():
                key = f"{city} — {place_name} — {area}"
            else:
                key = f"{city} — {s_loc}"
            self._loc_map[key] = s_loc
        return sorted(self._loc_map.keys())

    def _get_area(self) -> str:
        return self._loc_map.get(self.s_loc.get(), self.s_loc.get())

    def addl(self):
        city       = self.loc_city.get().strip()
        place_name = self.loc_place.get().strip()
        area       = self.loc.get().strip()
        if not city:
            showerror("Error", "Please select or add a city.")
            return
        if not place_name:
            showerror("Error", "Place name cannot be empty.")
            return
        if not area:
            showerror("Error", "Area name cannot be empty.")
            return
        s_loc_key = f"{place_name} — {area}"
        if len(s_loc_key) > 95:
            showerror("Error",
                      "Place name + Area combined must be under 95 characters.")
            return
        if db_locations.exists(s_loc_key):
            showerror("Error",
                      "A location with this Place Name and Area already exists.")
            self.rootadd.destroy()
            return
        db_locations.create(s_loc_key, city, place_name, area)
        new_vals = self._build_loc_map()
        self.s_loc.config(values=new_vals)
        display = f"{city} — {place_name} — {area}"
        if display in new_vals:
            self.s_loc.set(display)
        if new_vals and self._no_loc_banner.winfo_ismapped():
            self._no_loc_banner.pack_forget()
            self.start["state"] = "normal"
        showinfo("Add Location", "Location added successfully.")
        self.rootadd.destroy()

    def addloc(self):
        P = self.P
        self.rootadd = Toplevel(self.root)
        self.rootadd.title("Add Surveillance Location")
        self.rootadd.resizable(False, False)
        self.rootadd.configure(bg=P.card)
        x = (self.rootadd.winfo_screenwidth()  // 2) - 200
        y = (self.rootadd.winfo_screenheight() // 2) - 175
        self.rootadd.geometry(f"420x360+{x}+{y}")
        self.rootadd.grab_set()

        f = Frame(self.rootadd, bg=P.card, padx=30, pady=24)
        f.pack(fill=BOTH, expand=True)

        Label(f, text="New Surveillance Location",
              font=theme.F_SUB, bg=P.card, fg=P.fg).pack(pady=(0, 14))

        entry_cfg = dict(font=theme.F_ENTRY, width=28,
                         bg=P.inp, fg=P.fg, insertbackground=P.fg,
                         relief=FLAT, highlightthickness=1,
                         highlightbackground=P.border,
                         highlightcolor=P.panel)

        Label(f, text="City", font=theme.F_BODY,
              bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
        city_row = Frame(f, bg=P.card)
        city_row.pack(fill=X, pady=(2, 12))
        self.loc_city = Combobox(city_row, values=db_cities.get_all(),
                                 font=theme.F_ENTRY, width=26, state='readonly')
        self.loc_city.pack(side=LEFT, ipady=5)
        self.loc_city.focus()

        def _add_city():
            name = askstring("New City", "Enter city name:",
                             parent=self.rootadd)
            if name:
                name = name.strip()
                if name and not db_cities.exists(name):
                    db_cities.create(name)
                if name:
                    self.loc_city.config(values=db_cities.get_all())
                    self.loc_city.set(name)

        theme.btn(city_row, "+", _add_city,
                  width=32, height=32).pack(side=LEFT, padx=(6, 0))

        Label(f, text="Place Name  (e.g. Sunrise Public School)",
              font=theme.F_BODY, bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
        self.loc_place = Entry(f, **entry_cfg)
        self.loc_place.pack(ipady=7, pady=(2, 12), fill=X)

        Label(f, text="Area  (e.g. Main Gate)",
              font=theme.F_BODY, bg=P.card, fg=P.fg, anchor=W).pack(fill=X)
        self.loc = Entry(f, **entry_cfg)
        self.loc.pack(ipady=7, pady=(2, 16), fill=X)

        theme.btn(f, "Add Location", self.addl, width=240).pack()

    # ── surveillance save ─────────────────────────────────────────────────────

    def sur(self):
        area = self._get_area()
        db_surv.create(
            area, str(self.txt2.get()), str(self.txt1.get()),
            str(self.txt3.get()), str(self.mp.get()), str(self.up.get()),
            self.total_persons,
        )
        showinfo("Saved", "Surveillance data saved successfully.")

    # ── camera ────────────────────────────────────────────────────────────────

    def start_camera(self):
        P = self.P
        self._clear_main()

        self.submit["state"] = DISABLED
        self.masked   = 0
        self.unmasked = 0
        self.masked_lbl.config(text="0")
        self.unmasked_lbl.config(text="0")
        self.start["state"] = DISABLED

        for entry, row, value in [
            (self.txt2, 5, str(datetime.today().date())),
            (self.txt1, 6, datetime.now().strftime("%H:%M:%S")),
        ]:
            entry.config(state="normal")
            entry.delete(0, END)
            entry.insert(0, value)
            entry.config(state="disabled")
            entry.grid(row=row, column=1, padx=8, pady=4)

        for entry, row in [(self.txt3, 7), (self.mp, 9),
                           (self.up, 10), (self.tp, 13)]:
            entry.config(state="normal")
            entry.delete(0, END)
            entry.config(state="disabled")
            entry.grid(row=row, column=1, padx=8, pady=4)

        self.tracker       = PersonTracker()
        self.total_persons = 0

        self.cap = MyVideoCapture()
        try:
            cam_val = self.mode.get()
            cam_idx = (int(cam_val.split()[1])
                       if cam_val.startswith("Camera") else int(cam_val))
            self.cap.startVideo(cam_idx)
        except ValueError:
            self.start["state"] = NORMAL
            self.submit["state"] = DISABLED
            showerror("Camera Error",
                      "Could not open camera.\n\n"
                      "• Check that the camera index is correct.\n"
                      "• On macOS, grant camera access in System Settings → Privacy → Camera.")
            return

        self.camera = Frame(self.main_frame, bg=P.bg)
        self.canvas = Canvas(self.camera, bg=P.bg, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True)
        self.camera.pack(fill=BOTH, expand=True)

        self._det_result      = ([], False)
        self._det_id          = 0
        self._counted_id      = 0
        self._inference_active = True
        self._det_queue        = _queue.Queue(maxsize=1)
        threading.Thread(target=self._run_inference, daemon=True).start()

        self.stop["state"] = NORMAL
        self.delay = 15
        self.flag  = True
        self.update()

    def stop_camera(self):
        self.submit["state"] = NORMAL
        self.start["state"]  = NORMAL
        self.stop["state"]   = DISABLED

        self._inference_active = False
        try:
            self._det_queue.get_nowait()
        except Exception:
            pass

        self.txt3.config(state="normal")
        self.txt3.delete(0, END)
        self.txt3.insert(0, datetime.now().strftime("%H:%M:%S"))
        self.txt3.config(state="disabled")
        self.txt3.grid(row=7, column=1, padx=8, pady=4)

        if self.flag:
            self.flag = False
            self.cap.camera_release()
            self.canvas.destroy()
            self.session.release_capture()
            self.camera.destroy()

        if self.tracker is not None:
            for track in self.tracker.get_active() + self.tracker.get_finalized():
                if track.is_masked:
                    self.masked += 1
                else:
                    self.unmasked += 1

        self.total_persons = self.masked + self.unmasked
        total  = self.total_persons
        m_pct  = (self.masked   / total) * 100 if total else 0
        u_pct  = (self.unmasked / total) * 100 if total else 0

        for entry, row, val in [
            (self.mp, 9,  f"{m_pct:.1f} %"),
            (self.up, 10, f"{u_pct:.1f} %"),
            (self.tp, 13, str(total)),
        ]:
            entry.config(state="normal")
            entry.delete(0, END)
            entry.insert(0, val)
            entry.config(state="disabled")
            entry.grid(row=row, column=1, padx=8, pady=4)

        P = self.P
        fig = Figure(facecolor=P.card)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(P.card)
        ax.pie([self.masked, self.unmasked], radius=1,
               labels=["Masked", "Unmasked"],
               colors=[theme.SUCCESS, theme.DANGER],
               autopct='%0.1f%%', shadow=False,
               wedgeprops=dict(width=0.6),
               textprops=dict(color=P.fg))
        ax.set_title("Mask Compliance", fontsize=13, fontweight='bold', color=P.fg)
        chart = FigureCanvasTkAgg(fig, self.main_frame)
        self._chart_widget = chart.get_tk_widget()
        self._chart_widget.pack(fill=BOTH, expand=True, padx=40, pady=40)

    def _run_inference(self):
        while self._inference_active:
            try:
                frame = self._det_queue.get(timeout=0.3)
                self._det_result = detect(frame)
                self._det_id    += 1
            except _queue.Empty:
                pass
            except Exception:
                _log.exception("Inference thread error")

    def update(self):
        if not self.flag:
            return

        font       = cv2.FONT_HERSHEY_SIMPLEX
        color_ok   = (52,  168, 83)
        color_warn = (234,  67, 53)
        thickness  = 2

        ret, img = self.cap.get_frame()
        if not ret or img is None:
            self.root.after(self.delay, self.update)
            return

        img    = cv2.flip(img, 1)
        orig_h, orig_w = img.shape[:2]

        try:
            self._det_queue.put_nowait(img.copy())
        except _queue.Full:
            pass

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 32:
            cw, ch = 850, 600
        display_img = cv2.resize(img, (cw, ch))
        sx = cw / orig_w
        sy = ch / orig_h

        if self._det_id != self._counted_id:
            self._counted_id      = self._det_id
            detections, has_face  = self._det_result
            if self.tracker is not None:
                self.tracker.update(detections)
                for track in self.tracker.get_finalized():
                    if track.is_masked:
                        self.masked   += 1
                    else:
                        self.unmasked += 1
        else:
            detections, has_face = self._det_result

        if not has_face:
            cv2.putText(display_img, "No face detected", (30, 40),
                        font, 0.8, (200, 200, 200), thickness, cv2.LINE_AA)
        else:
            for (x, y, w, h, status) in detections:
                color = color_ok if status == MASKED else color_warn
                label = "Mask On" if status == MASKED else "No Mask!"
                xd = int(x * sx); yd = int(y * sy)
                wd = int(w * sx); hd = int(h * sy)
                cv2.rectangle(display_img, (xd, yd), (xd+wd, yd+hd), color, 2)
                cv2.putText(display_img, label, (xd, max(yd-8, 16)),
                            font, 0.7, color, thickness, cv2.LINE_AA)

        self.masked_lbl.config(text=str(self.masked))
        self.unmasked_lbl.config(text=str(self.unmasked))

        self.photo = PIL.ImageTk.PhotoImage(
            image=PIL.Image.fromarray(display_img))
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.root.after(self.delay, self.update)

    # ── constructor ───────────────────────────────────────────────────────────

    def __init__(self, session: AppSession, palette: ThemePalette):
        self.session = session
        self.P       = palette

        # Sync legacy state module so old code that reads state.mode still works
        state.mode = 1 if palette.name == "dark" else 2

        P = self.P
        self.root = Tk()
        theme.maximize(self.root)
        self.root.title("Mask Detector")
        self.icon_photo = PhotoImage(file=Images.ICON)
        self.root.iconphoto(False, self.icon_photo)
        self.root.config(bg=P.bg)
        self.root.minsize(900, 600)

        sty = Style()
        sty.configure('my.TCombobox', arrowsize=20, font=theme.F_ENTRY)

        # Surveillance state
        self.flag          = False
        self._chart_widget = None
        self._placeholder  = None
        self._current_panel = None
        self._active_section = ""
        self.masked        = 0
        self.unmasked      = 0
        self.tracker       = None
        self.total_persons = 0
        # Inference threading state
        self._inference_active = False
        self._det_queue        = None
        self._det_result       = ([], False)
        self._det_id           = 0
        self._counted_id       = 0

        # ── Top nav bar ───────────────────────────────────────────────────────
        nav = Frame(self.root, bg=P.panel, height=50)
        nav.pack(side=TOP, fill=X)
        nav.pack_propagate(False)

        self._complaints_btn = theme.btn(nav, "📋  Complaints", self.show_complaints, width=150)
        self._complaints_btn.pack(side=LEFT, padx=4, pady=6)
        self._history_btn = theme.btn(nav, "📜  History", self.show_history, width=150)
        self._history_btn.pack(side=LEFT, padx=4, pady=6)
        self.ad_btn   = theme.btn(nav, "➕  Add Admin",   self.manage_admins, width=150)
        self.view_btn = theme.btn(nav, "👥  View Admins", self.manage_admins, width=150)
        self._admins_btn = self.ad_btn   # nav indicator target for admin section
        self.ad_btn.pack(side=LEFT, padx=4, pady=6)
        self.view_btn.pack(side=LEFT, padx=4, pady=6)

        # ── Bottom bar ────────────────────────────────────────────────────────
        bottom = Frame(self.root, bg=P.panel2, height=60)
        bottom.pack(side=BOTTOM, fill=X)
        bottom.pack_propagate(False)

        self.addloc_btn = theme.btn(bottom, "📍  Add Location", self.addloc,
                                    width=200)
        self.addloc_btn.pack(side=LEFT, padx=16, pady=10)

        theme.btn(bottom, P.toggle_label, self._toggle_theme,
                  bg=P.toggle_bg, width=150).pack(side=LEFT, padx=8, pady=10)

        theme.btn(bottom, "⏻  Logout", self.lg,
                  bg=theme.DANGER, width=130).pack(side=RIGHT, padx=16, pady=10)

        # ── Left sidebar ──────────────────────────────────────────────────────
        self.bf1 = Frame(self.root, bg=P.panel, width=300)
        self.bf1.pack(side=LEFT, fill=Y)
        self.bf1.pack_propagate(False)

        # User info block
        info_frame = Frame(self.bf1, bg=P.panel, pady=16)
        info_frame.pack(fill=X)
        Label(info_frame, text=session.username,
              font=theme.F_SUB, bg=P.panel, fg=P.panel_fg).pack()
        Label(info_frame, text=f"[ {session.role} ]",
              font=theme.F_SMALL, bg=P.panel, fg=P.panel_muted).pack()
        Label(info_frame, text=session.email,
              font=theme.F_SMALL, bg=P.panel, fg=P.panel_muted).pack(pady=(2, 0))

        Frame(self.bf1, bg=P.border, height=1).pack(fill=X, padx=16, pady=8)

        form_frame = Frame(self.bf1, bg=P.panel)
        form_frame.pack(fill=X, padx=12, pady=4)

        for row, text in [(4, "📍 Location"), (5, "📅 Date"),
                          (6, "🕐 Start Time"), (7, "🕐 End Time")]:
            Label(form_frame, text=text, font=theme.F_BODY,
                  bg=P.panel, fg=P.panel_fg, anchor=W).grid(
                  row=row, column=0, sticky=W, padx=6, pady=3)

        Frame(self.bf1, bg=P.border, height=1).pack(fill=X, padx=16, pady=8)

        stat_frame = Frame(self.bf1, bg=P.panel)
        stat_frame.pack(fill=X, padx=12, pady=4)

        for row, text in [(9, "✅ Masked %"), (10, "⚠️  Unmasked %")]:
            Label(stat_frame, text=text, font=theme.F_BODY,
                  bg=P.panel, fg=P.panel_fg, anchor=W).grid(
                  row=row, column=0, sticky=W, padx=6, pady=3)

        Label(stat_frame, text="Exited Masked:",
              font=theme.F_SMALL, bg=P.panel, fg=theme.SUCCESS, anchor=W).grid(
              row=11, column=0, sticky=W, padx=6, pady=(8, 1))
        self.masked_lbl = Label(stat_frame, text="0",
                                font=('Helvetica', 14, 'bold'),
                                bg=P.panel, fg=theme.SUCCESS, anchor=W)
        self.masked_lbl.grid(row=11, column=1, sticky=W, padx=6)

        Label(stat_frame, text="Exited Unmasked:",
              font=theme.F_SMALL, bg=P.panel, fg=theme.DANGER, anchor=W).grid(
              row=12, column=0, sticky=W, padx=6, pady=(1, 4))
        self.unmasked_lbl = Label(stat_frame, text="0",
                                  font=('Helvetica', 14, 'bold'),
                                  bg=P.panel, fg=theme.DANGER, anchor=W)
        self.unmasked_lbl.grid(row=12, column=1, sticky=W, padx=6)

        Label(stat_frame, text="👤 Total Persons",
              font=theme.F_BODY, bg=P.panel, fg=P.panel_fg, anchor=W).grid(
              row=13, column=0, sticky=W, padx=6, pady=3)

        Frame(self.bf1, bg=P.border, height=1).pack(fill=X, padx=16, pady=8)

        cam_frame = Frame(self.bf1, bg=P.panel)
        cam_frame.pack(fill=X, padx=12)
        Label(cam_frame, text="📷 Camera",
              font=theme.F_BODY, bg=P.panel, fg=P.panel_fg).grid(
              row=0, column=0, sticky=W, padx=6, pady=4)
        _cam_opts    = [f"Camera {i}" for i in range(4)]
        _cam_opts[0] = "Camera 0 (Built-in)"
        self.mode = Combobox(cam_frame, values=_cam_opts,
                             font=theme.F_ENTRY, width=16,
                             state='readonly', style='my.TCombobox')
        self.mode.set(_cam_opts[0])
        self.mode.grid(row=0, column=1, padx=6, pady=4, ipady=4)

        # Location combobox
        self._loc_map: dict = {}
        _loc_vals = self._build_loc_map()
        self.s_loc = Combobox(form_frame, values=_loc_vals,
                              font=theme.F_ENTRY, width=18,
                              state='readonly', style='my.TCombobox')
        self.s_loc.grid(row=4, column=1, padx=6, pady=3)

        # Sidebar read-only entry fields (date, time, percentages)
        entry_cfg = dict(font=theme.F_ENTRY, width=18, relief=FLAT,
                         bg=P.entry_bg,
                         fg=P.panel_fg,
                         disabledbackground=P.entry_disabled_bg,
                         disabledforeground=P.entry_disabled_fg,
                         highlightthickness=1,
                         highlightbackground=P.entry_border)

        self.txt2 = Entry(form_frame, **entry_cfg)
        self.txt2.config(state="disabled")
        self.txt2.grid(row=5, column=1, padx=6, pady=3, ipady=4)

        self.txt1 = Entry(form_frame, **entry_cfg)
        self.txt1.config(state="disabled")
        self.txt1.grid(row=6, column=1, padx=6, pady=3, ipady=4)

        self.txt3 = Entry(form_frame, **entry_cfg)
        self.txt3.config(state="disabled")
        self.txt3.grid(row=7, column=1, padx=6, pady=3, ipady=4)

        self.mp = Entry(stat_frame, **entry_cfg)
        self.mp.config(state="disabled")
        self.mp.grid(row=9, column=1, padx=6, pady=3, ipady=4)

        self.up = Entry(stat_frame, **entry_cfg)
        self.up.config(state="disabled")
        self.up.grid(row=10, column=1, padx=6, pady=3, ipady=4)

        self.tp = Entry(stat_frame, **entry_cfg)
        self.tp.config(state="disabled")
        self.tp.grid(row=13, column=1, padx=6, pady=3, ipady=4)

        Frame(self.bf1, bg=P.border, height=1).pack(fill=X, padx=16, pady=8)

        btn_frame = Frame(self.bf1, bg=P.panel)
        btn_frame.pack(fill=X, padx=16, pady=8)

        self.start = theme.btn(btn_frame, "▶  Start", self.start_camera,
                               bg=theme.SUCCESS, width=120, height=38)
        self.start.grid(row=0, column=0, padx=4)

        self.stop = theme.btn(btn_frame, "■  Stop", self.stop_camera,
                              bg=theme.DANGER, width=120, height=38)
        self.stop.grid(row=0, column=1, padx=4)
        self.stop["state"] = DISABLED

        self.submit = theme.btn(self.bf1, "💾  Save Surveillance", self.sur,
                                width=260, height=42)
        self.submit.pack(padx=16, pady=10)
        self.submit["state"] = DISABLED

        # ── Empty-locations warning banner ────────────────────────────────────
        self._no_loc_banner = Label(
            self.bf1,
            text="⚠  No locations configured.\nClick 📍 Add Location to get started.",
            font=theme.F_SMALL, bg=P.panel, fg=theme.WARNING,
            justify=CENTER, wraplength=260,
        )
        if not _loc_vals:
            self.start["state"] = "disabled"
            self._no_loc_banner.pack(padx=16, pady=(0, 8))

        # ── Main content area ─────────────────────────────────────────────────
        self.main_frame = Frame(self.root, bg=P.bg)
        self.main_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # Idle placeholder — rendered via shared helper
        self._restore_placeholder()

        # Disable admin controls for non-Super Admin
        if session.role == "Admin":
            self.ad_btn["state"]     = DISABLED
            self.view_btn["state"]   = DISABLED
            self.addloc_btn["state"] = DISABLED

        theme.fade_in(self.root)
        self.root.mainloop()
