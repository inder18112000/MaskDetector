from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
import secrets
import otp
import app.state as state
from app.paths import Images
from app.db import users as db_users
from app.security import verify_password
from app import theme
from PIL import Image, ImageTk

# ── Theme ────────────────────────────────────────────────────────────────────
PRIMARY      = "#1a73e8"
PRIMARY_DARK = "#1557b0"
ACCENT       = "#ff6b35"
BG_CARD      = "#ffffff"
BG_INPUT     = "#f8f9fa"
TEXT_DARK    = "#202124"
TEXT_MID     = "#5f6368"
TEXT_LIGHT   = "#ffffff"
BORDER       = "#dadce0"
SUCCESS      = "#34a853"
# ─────────────────────────────────────────────────────────────────────────────


class log:
    def __init__(self):
        self.root = Tk()
        self.root.state("zoomed")
        self.root.geometry("1550x766")
        self.root.title("MASK DETECTOR")

        self.icon_photo = PhotoImage(file=Images.ICON)
        self.root.iconphoto(False, self.icon_photo)

        # Background image (JPEG loaded via PIL)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        _img = Image.open(Images.FRONT_LOGIN).resize((sw, sh), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(_img)
        Label(self.root, image=self.bg_photo, bd=0).place(x=0, y=0, relwidth=1, relheight=1)

        # ── Register Complaints button (top-right) ───────────────────────────
        theme.btn(self.root, "⚠  Register Complaint", self.complaint,
                  bg=ACCENT, width=220).pack(padx=16, pady=16, anchor=NE)

        # ── Login card ───────────────────────────────────────────────────────
        card = Frame(self.root, bg=BG_CARD, padx=40, pady=36)
        card.place(relx=0.5, rely=0.5, anchor=CENTER)

        # App title inside card
        Label(card, text="MASK DETECTOR",
              font=('Helvetica', 22, 'bold'),
              bg=BG_CARD, fg=PRIMARY).grid(
              row=0, column=0, columnspan=2, pady=(0, 4))

        Label(card, text="Admin Login Portal",
              font=('Helvetica', 11),
              bg=BG_CARD, fg=TEXT_MID).grid(
              row=1, column=0, columnspan=2, pady=(0, 24))

        # Separator
        sep = Frame(card, bg=BORDER, height=1)
        sep.grid(row=2, column=0, columnspan=2, sticky=EW, pady=(0, 20))

        # Email field
        Label(card, text="Email Address",
              font=('Helvetica', 11, 'bold'),
              bg=BG_CARD, fg=TEXT_DARK, anchor=W).grid(
              row=3, column=0, columnspan=2, sticky=W, padx=4, pady=(0, 4))

        self.txt1 = Entry(card, font=('Helvetica', 13), width=36,
                          bg=BG_INPUT, fg=TEXT_DARK,
                          relief=FLAT, highlightthickness=1,
                          highlightbackground=BORDER,
                          highlightcolor=PRIMARY,
                          insertbackground=TEXT_DARK)
        self.txt1.grid(row=4, column=0, columnspan=2, ipady=8, padx=4, pady=(0, 16))

        # Password field
        Label(card, text="Password",
              font=('Helvetica', 11, 'bold'),
              bg=BG_CARD, fg=TEXT_DARK, anchor=W).grid(
              row=5, column=0, columnspan=2, sticky=W, padx=4, pady=(0, 4))

        self.txt2 = Entry(card, font=('Helvetica', 13), width=36,
                          show='●', bg=BG_INPUT, fg=TEXT_DARK,
                          relief=FLAT, highlightthickness=1,
                          highlightbackground=BORDER,
                          highlightcolor=PRIMARY,
                          insertbackground=TEXT_DARK)
        self.txt2.grid(row=6, column=0, columnspan=2, ipady=8, padx=4, pady=(0, 24))

        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.checkLogin())

        # Login button
        self.login_btn = theme.btn(card, "Sign In", self.checkLogin, width=340, height=44)
        self.login_btn.grid(row=7, column=0, columnspan=2, padx=4, pady=(0, 12))

        # Forgot password link-style button
        forgot_btn = Button(
            card,
            text="Forgot Password?",
            font=('Helvetica', 11),
            bg=BG_CARD, fg=PRIMARY,
            activebackground=BG_CARD,
            activeforeground=PRIMARY_DARK,
            relief=FLAT, cursor="hand2",
            bd=0,
            command=self.fp
        )
        forgot_btn.grid(row=8, column=0, columnspan=2, pady=(0, 4))

        self.root.mainloop()

    # ── Navigation ───────────────────────────────────────────────────────────
    def complaint(self):
        self.root.destroy()
        from app.views.complaint import comp
        comp()

    def fp(self):
        self.root.destroy()
        from app.views.forgot_password import forgot
        obj1 = forgot()
        obj1.password()
        log()

    # ── Login logic ──────────────────────────────────────────────────────────
    def checkLogin(self):
        email    = self.txt1.get().strip()
        password = self.txt2.get()

        if not email or not password:
            showerror('Missing Fields', 'Please enter both email and password.')
            return

        user = db_users.get_by_email(email)
        if user is None or not verify_password(password, user[2]):
            showerror('Login Failed', 'Invalid email or password.')
            return

        self.result = user
        if self.result[3] == "Super Admin":
            try:
                self.str1 = otp.send(self.result[1])
            except otp.OTPSendError as e:
                showerror('Email Error', str(e))
                return
            self._show_otp_window()
        else:
            showinfo('Welcome', f'Login successful. Welcome, {self.result[0]}!')
            self.root.destroy()
            state.result = self.result
            from app.views.dashboard_light import dasboard_light
            dasboard_light(state.result)

    def _show_otp_window(self):
        self.root1 = Toplevel(self.root)
        self.root1.title("Two-Factor Verification")
        self.root1.resizable(False, False)
        self.root1.grab_set()

        # Center the OTP window
        self.root1.geometry("420x320")
        self.root1.configure(bg=BG_CARD)
        self.root1.update_idletasks()
        x = (self.root1.winfo_screenwidth()  // 2) - 210
        y = (self.root1.winfo_screenheight() // 2) - 160
        self.root1.geometry(f"420x320+{x}+{y}")

        frame = Frame(self.root1, bg=BG_CARD, padx=36, pady=30)
        frame.pack(fill=BOTH, expand=True)

        Label(frame, text="🔐  Two-Factor Verification",
              font=('Helvetica', 15, 'bold'),
              bg=BG_CARD, fg=TEXT_DARK).pack(pady=(0, 6))

        Label(frame, text=f"An OTP has been sent to\n{self.result[1]}",
              font=('Helvetica', 10),
              bg=BG_CARD, fg=TEXT_MID, justify=CENTER).pack(pady=(0, 20))

        self.e1 = Entry(frame, font=('Helvetica', 18, 'bold'), width=12,
                        justify=CENTER, bg=BG_INPUT, fg=PRIMARY,
                        relief=FLAT, highlightthickness=1,
                        highlightbackground=BORDER,
                        highlightcolor=PRIMARY,
                        insertbackground=PRIMARY)
        self.e1.pack(ipady=10, pady=(0, 20))
        self.e1.focus()

        self.root1.bind('<Return>', lambda e: self.press())

        theme.btn(frame, "Verify OTP", self.press, bg=SUCCESS, width=220).pack()

    def press(self):
        if secrets.compare_digest(str(self.str1), str(self.e1.get())):
            showinfo('Welcome', f'Login successful. Welcome, {self.result[0]}!')
            self.root1.destroy()
            self.root.destroy()
            state.result = self.result
            from app.views.dashboard_light import dasboard_light
            dasboard_light(state.result)
        elif self.e1.get() == "":
            showerror("Error", "Please enter the OTP.")
        else:
            showerror("Error", "Incorrect OTP. Please try again.")
