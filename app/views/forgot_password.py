from tkinter import *
from tkinter.messagebox import *
import secrets
import otp
from app.paths import Images
from app.db import users as db_users
from app.security import hash_password, verify_password
from app import theme


class forgot:
    def password(self, parent=None):
        """Open the Reset Password screen.

        When *parent* is supplied the screen opens as a modal Toplevel over the
        login window.  When called standalone (parent=None) it behaves as before,
        creating its own Tk() root.
        """
        if parent is None:
            self.rootf = Tk()
            theme.maximize(self.rootf)
            self.rootf.title("Mask Detector — Reset Password")
            self.icon_photo = PhotoImage(file=Images.ICON)
            self.rootf.iconphoto(False, self.icon_photo)
            _standalone = True
        else:
            self.rootf = Toplevel(parent)
            sw = parent.winfo_screenwidth()
            sh = parent.winfo_screenheight()
            w, h = 700, 580
            self.rootf.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
            self.rootf.title("Mask Detector — Reset Password")
            self.rootf.resizable(False, False)
            self.rootf.grab_set()
            _standalone = False

        # Background
        self.bg_photo = PhotoImage(file=Images.BG_FG)
        Label(self.rootf, image=self.bg_photo, bd=0).place(
            x=0, y=0, relwidth=1, relheight=1)

        # ── Card ─────────────────────────────────────────────────────────────
        card = Frame(self.rootf, bg=theme.L_CARD, padx=40, pady=36)
        card.place(relx=0.5, rely=0.5, anchor=CENTER)

        Label(card, text="Reset Password",
              font=theme.F_TITLE, bg=theme.L_CARD, fg=theme.L_PANEL).grid(
              row=0, column=0, columnspan=2, pady=(0, 4))
        Label(card, text="Enter your email to receive a one-time password",
              font=theme.F_SMALL, bg=theme.L_CARD, fg=theme.L_MUTED).grid(
              row=1, column=0, columnspan=2, pady=(0, 20))

        Frame(card, bg=theme.L_BORDER, height=1).grid(
              row=2, column=0, columnspan=2, sticky=EW, pady=(0, 16))

        Label(card, text="Email Address", font=theme.F_SUB,
              bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).grid(
              row=3, column=0, sticky=W, padx=(0, 16), pady=4)
        self.e1 = Entry(card, font=theme.F_ENTRY, width=34,
                        bg=theme.L_INPUT, fg=theme.L_TEXT,
                        relief=FLAT, highlightthickness=1,
                        highlightbackground=theme.L_BORDER,
                        highlightcolor=theme.L_PANEL,
                        insertbackground=theme.L_TEXT)
        self.e1.grid(row=3, column=1, ipady=7, pady=4)
        self.e1.focus()

        self.rootf.bind('<Return>', lambda e: self.gen())

        theme.btn(card, "Send OTP", self.gen, width=220).grid(
              row=4, column=0, columnspan=2, pady=16)

        self.bf2 = card
        theme.fade_in(self.rootf)
        if _standalone:
            self.rootf.mainloop()

    def gen(self):
        if not self.e1.get().strip():
            showerror("Error", "Please enter your email address.")
            return
        self.result = db_users.get_by_email(self.e1.get().strip())
        if self.result is None:
            showerror('Not Found', 'No account found for that email.')
            return
        try:
            self.str1 = otp.send(self.result[1], purpose="reset")
        except otp.OTPSendError as e:
            showerror('Email Error', str(e))
            return

        # Show OTP + new password fields
        Frame(self.bf2, bg=theme.L_BORDER, height=1).grid(
              row=5, column=0, columnspan=2, sticky=EW, pady=(4, 16))

        entry_cfg = dict(font=theme.F_ENTRY, width=34,
                         bg=theme.L_INPUT, fg=theme.L_TEXT,
                         relief=FLAT, highlightthickness=1,
                         highlightbackground=theme.L_BORDER,
                         highlightcolor=theme.L_PANEL,
                         insertbackground=theme.L_TEXT)

        for row, label, secret in [
            (6, "Enter OTP",          False),
            (7, "New Password",       True),
            (8, "Confirm Password",   True),
        ]:
            Label(self.bf2, text=label, font=theme.F_SUB,
                  bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).grid(
                  row=row, column=0, sticky=W, padx=(0, 16), pady=4)

        self.eotp = Entry(self.bf2, **entry_cfg)
        self.eotp.grid(row=6, column=1, ipady=7, pady=4)
        self.eotp.focus()

        self.new = Entry(self.bf2, show="●", **entry_cfg)
        self.new.grid(row=7, column=1, ipady=7, pady=4)

        self.ren = Entry(self.bf2, show="●", **entry_cfg)
        self.ren.grid(row=8, column=1, ipady=7, pady=4)

        self.rootf.bind('<Return>', lambda e: self.press())

        theme.btn(self.bf2, "Reset Password", self.press,
                  bg=theme.SUCCESS, width=220).grid(
                  row=9, column=0, columnspan=2, pady=16)

    def press(self):
        if not secrets.compare_digest(str(self.str1), str(self.eotp.get())):
            showerror("Invalid OTP", "The OTP you entered is incorrect.")
            return
        if verify_password(self.new.get(), self.result[2]):
            showerror("Error", "New password cannot be the same as your current password.")
            return
        if self.new.get() != self.ren.get():
            showerror("Error", "Passwords do not match.")
            return
        db_users.update_password(self.e1.get().strip(), hash_password(self.new.get()))
        showinfo('Success', 'Password updated successfully. Please log in again.')
        self.rootf.destroy()
