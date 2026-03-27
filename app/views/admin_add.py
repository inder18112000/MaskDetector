from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox
import secrets
import otp
import app.state as state
from app.paths import Images
from app.db import users as db_users
from app.security import hash_password
from app import theme


class add:
    def back(self):
        self.roota.destroy()
        if state.mode == 1:
            from app.views.dashboard_dark import dasboard
            dasboard(state.result)
        else:
            from app.views.dashboard_light import dasboard_light
            dasboard_light(state.result)

    def press(self):
        if secrets.compare_digest(str(self.str1), str(self.e1.get())):
            db_users.create(self.username, self.email,
                            hash_password(self.password), self.role)
            showinfo('Success', 'Admin account created successfully.')
            self.otp_win.destroy()
            self.roota.destroy()
            if state.mode == 1:
                from app.views.dashboard_dark import dasboard
                dasboard(state.result)
            else:
                from app.views.dashboard_light import dasboard_light
                dasboard_light(state.result)
        elif self.e1.get() == "":
            showerror("Error", "Please enter the OTP.")
        else:
            showerror("Error", "Incorrect OTP. Please try again.")

    def checkLogin(self):
        self.username = self.txt4.get().strip()
        self.email    = self.txt1.get().strip()
        self.password = self.txt2.get()
        self.role     = self.txt3.get()
        if not self.username or not self.email or not self.password or not self.role:
            showerror('Missing Fields', 'Please fill in all fields.')
            return
        if db_users.get_by_email(self.email) is not None:
            showerror('', 'An account with this email already exists.')
            return
        try:
            self.str1 = otp.send(self.email)
        except otp.OTPSendError as e:
            showerror('Email Error', str(e))
            return
        self._show_otp_window()

    def _show_otp_window(self):
        self.otp_win = Toplevel(self.roota)
        self.otp_win.title("Verify New Admin")
        self.otp_win.resizable(False, False)
        self.otp_win.configure(bg=theme.L_CARD)
        x = (self.otp_win.winfo_screenwidth()  // 2) - 210
        y = (self.otp_win.winfo_screenheight() // 2) - 160
        self.otp_win.geometry(f"420x300+{x}+{y}")
        self.otp_win.grab_set()

        f = Frame(self.otp_win, bg=theme.L_CARD, padx=36, pady=28)
        f.pack(fill=BOTH, expand=True)

        Label(f, text="🔐  Verify Admin Email",
              font=theme.F_HEAD, bg=theme.L_CARD, fg=theme.L_TEXT).pack(pady=(0, 6))
        Label(f, text=f"OTP sent to: {self.email}",
              font=theme.F_SMALL, bg=theme.L_CARD, fg=theme.L_MUTED).pack(pady=(0, 18))

        self.e1 = Entry(f, font=('Helvetica', 18, 'bold'), width=12,
                        justify=CENTER, bg=theme.L_INPUT, fg=theme.L_PANEL,
                        relief=FLAT, highlightthickness=1,
                        highlightbackground=theme.L_BORDER,
                        highlightcolor=theme.L_PANEL,
                        insertbackground=theme.L_PANEL)
        self.e1.pack(ipady=10, pady=(0, 18))
        self.e1.focus()
        self.otp_win.bind('<Return>', lambda e: self.press())

        theme.btn(f, "Verify & Create Account", self.press,
                  bg=theme.SUCCESS, width=260).pack()

    def __init__(self):
        self.roota = Tk()
        self.roota.state("zoomed")
        self.roota.title("Mask Detector — Add Admin")
        self.icon_photo = PhotoImage(file=Images.ICON)
        self.roota.iconphoto(False, self.icon_photo)

        # Background image
        self.bg_photo = PhotoImage(file=Images.ADD)
        Label(self.roota, image=self.bg_photo, bd=0).place(x=0, y=0, relwidth=1, relheight=1)

        # ── Card ─────────────────────────────────────────────────────────────
        card = Frame(self.roota, bg=theme.L_CARD, padx=36, pady=32)
        card.place(x=130, y=260)

        Label(card, text="Add New Admin",
              font=theme.F_TITLE, bg=theme.L_CARD, fg=theme.L_PANEL).grid(
              row=0, column=0, columnspan=2, pady=(0, 4))
        Label(card, text="Fill in the details below and verify via OTP",
              font=theme.F_SMALL, bg=theme.L_CARD, fg=theme.L_MUTED).grid(
              row=1, column=0, columnspan=2, pady=(0, 20))

        Frame(card, bg=theme.L_BORDER, height=1).grid(
              row=2, column=0, columnspan=2, sticky=EW, pady=(0, 16))

        fields = [
            (3, "Username",  False),
            (4, "Email",     False),
            (5, "Password",  True),
        ]
        entries = []
        for row, label, secret in fields:
            Label(card, text=label, font=theme.F_SUB,
                  bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).grid(
                  row=row, column=0, sticky=W, padx=(0, 16), pady=4)
            e = Entry(card, font=theme.F_ENTRY, width=32,
                      show="●" if secret else "",
                      bg=theme.L_INPUT, fg=theme.L_TEXT,
                      relief=FLAT, highlightthickness=1,
                      highlightbackground=theme.L_BORDER,
                      highlightcolor=theme.L_PANEL,
                      insertbackground=theme.L_TEXT)
            e.grid(row=row, column=1, ipady=7, pady=4)
            entries.append(e)
        self.txt4, self.txt1, self.txt2 = entries

        Label(card, text="Role", font=theme.F_SUB,
              bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).grid(
              row=6, column=0, sticky=W, padx=(0, 16), pady=4)
        self.txt3 = Combobox(card, values=('Super Admin', 'Admin'),
                             font=theme.F_ENTRY, width=30, state='readonly')
        self.txt3.grid(row=6, column=1, ipady=4, pady=4)

        Frame(card, bg=theme.L_BORDER, height=1).grid(
              row=7, column=0, columnspan=2, sticky=EW, pady=12)

        btn_frame = Frame(card, bg=theme.L_CARD)
        btn_frame.grid(row=8, column=0, columnspan=2)

        theme.btn(btn_frame, "← Back", self.back,
                  bg=theme.L_MUTED, width=160).grid(row=0, column=0, padx=8)
        theme.btn(btn_frame, "Send OTP & Create", self.checkLogin,
                  width=220).grid(row=0, column=1, padx=8)

        self.roota.mainloop()
