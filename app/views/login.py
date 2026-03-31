from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
import secrets
import otp
import app.state as state
from app.session import AppSession
from app.paths import Images
from app.db import users as db_users
from app.security import verify_password
from app import theme
from PIL import Image, ImageTk, ImageDraw, ImageFont

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
        theme.maximize(self.root)
        self.root.title("MASK DETECTOR")

        self.icon_photo = PhotoImage(file=Images.ICON)
        self.root.iconphoto(False, self.icon_photo)

        # Background image — resizes with the window
        self._bg_src = Images.FRONT_LOGIN
        self._bg_label = Label(self.root, bd=0)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # ── Register Complaints button (top-right, ghost style) ──────────────
        # Rendered as a PIL RGBA image composited over the background photo so
        # the button corners are truly transparent (no canvas rectangle artifacts).
        self._complaint_photo = None
        self._complaint_btn = Label(self.root, bd=0, cursor="hand2",
                                    highlightthickness=0)
        self._complaint_btn.bind("<ButtonPress-1>",   lambda e: self._complaint_btn.config(image=self._complaint_press_photo))
        self._complaint_btn.bind("<ButtonRelease-1>", lambda e: (self._complaint_btn.config(image=self._complaint_hover_photo), self.complaint()))
        self._complaint_btn.bind("<Enter>",           lambda e: self._complaint_btn.config(image=self._complaint_hover_photo))
        self._complaint_btn.bind("<Leave>",           lambda e: self._complaint_btn.config(image=self._complaint_photo))

        self.root.bind("<Configure>", self._resize_bg)
        self.root.update_idletasks()
        self._resize_bg()

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

        theme.fade_in(self.root)
        self.root.mainloop()

    # ── Ghost button rendering ────────────────────────────────────────────────
    _BTN_W, _BTN_H, _BTN_PAD, _BTN_R = 220, 38, 16, 10

    def _make_complaint_overlay(self, fill_alpha, border_rgba, text_rgba):
        """Return a PIL RGBA overlay image for the complaint button."""
        overlay = Image.new('RGBA', (self._BTN_W, self._BTN_H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        # Semi-transparent dark backdrop for contrast
        d.rounded_rectangle(
            [(0, 0), (self._BTN_W - 1, self._BTN_H - 1)],
            radius=self._BTN_R, fill=(0, 0, 0, fill_alpha), outline=border_rgba, width=2,
        )
        try:
            fnt = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
        except Exception:
            try:
                fnt = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 14)
            except Exception:
                fnt = ImageFont.load_default()
        text = "⚠  Register Complaint"
        bbox = d.textbbox((0, 0), text, font=fnt)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((self._BTN_W - tw) // 2 - bbox[0],
                (self._BTN_H - th) // 2 - bbox[1]),
               text, font=fnt, fill=text_rgba)
        return overlay

    def _composite_btn(self, bg_img, fill_alpha, border_rgba, text_rgba):
        """Crop bg at button area, composite overlay, return PhotoImage."""
        bx = bg_img.width - self._BTN_W - self._BTN_PAD
        by = self._BTN_PAD
        crop = bg_img.crop((bx, by, bx + self._BTN_W, by + self._BTN_H)).convert('RGBA')
        composited = Image.alpha_composite(
            crop, self._make_complaint_overlay(fill_alpha, border_rgba, text_rgba))
        return ImageTk.PhotoImage(composited), bx, by

    def _resize_bg(self, event=None):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if w < 10 or h < 10:
            return
        img = Image.open(self._bg_src).resize((w, h), Image.LANCZOS)
        self._bg_photo = ImageTk.PhotoImage(img)
        self._bg_label.config(image=self._bg_photo)

        # Recomposite complaint button at all three states
        # Normal: dark backdrop + white border + white text
        self._complaint_photo,       bx, by = self._composite_btn(
            img, 110, (255, 255, 255, 220), (255, 255, 255, 255))
        # Hover: slightly brighter backdrop + orange border + orange text
        self._complaint_hover_photo, _,  _  = self._composite_btn(
            img, 150, (255, 107, 53, 255), (255, 107, 53, 255))
        # Press: strong dark backdrop + orange
        self._complaint_press_photo, _,  _  = self._composite_btn(
            img, 190, (200,  80, 20, 255), (200,  80, 20, 255))
        self._complaint_btn.config(image=self._complaint_photo)
        self._complaint_btn.place(x=bx, y=by,
                                  width=self._BTN_W, height=self._BTN_H)

    # ── Navigation ───────────────────────────────────────────────────────────
    def complaint(self):
        self.root.destroy()
        from app.views.complaint import comp
        comp()

    def fp(self):
        from app.views.forgot_password import forgot
        obj1 = forgot()
        obj1.password(parent=self.root)

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
        self.session = AppSession.from_row(user, theme="light")
        if self.result[3] == "Super Admin":
            try:
                self.str1 = otp.send(self.result[1], purpose="login")
            except otp.OTPSendError as e:
                showerror('Email Error', str(e))
                return
            self._show_otp_window()
        else:
            showinfo('Welcome', f'Login successful. Welcome, {self.result[0]}!')
            self.root.destroy()
            state.result = self.session
            from app.views.dashboard import Dashboard, LIGHT_PALETTE
            Dashboard(self.session, LIGHT_PALETTE)

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
        self.e1.pack(ipady=10, pady=(0, 8))
        self.e1.focus()

        self._otp_attempts_left = 3
        self._otp_attempts_lbl = Label(frame, text="3 attempts remaining",
                                       font=('Helvetica', 10),
                                       bg=BG_CARD, fg=TEXT_MID)
        self._otp_attempts_lbl.pack(pady=(0, 14))

        self.root1.bind('<Return>', lambda e: self.press())

        theme.btn(frame, "Verify OTP", self.press, bg=SUCCESS, width=220).pack()

    def press(self):
        if secrets.compare_digest(str(self.str1), str(self.e1.get())):
            showinfo('Welcome', f'Login successful. Welcome, {self.result[0]}!')
            self.root1.destroy()
            self.root.destroy()
            state.result = self.session
            from app.views.dashboard import Dashboard, LIGHT_PALETTE
            Dashboard(self.session, LIGHT_PALETTE)
        elif self.e1.get() == "":
            showerror("Error", "Please enter the OTP.")
        else:
            self._otp_attempts_left -= 1
            if self._otp_attempts_left <= 0:
                self.root1.destroy()
                showerror("Too Many Attempts",
                          "Too many incorrect attempts. Please try again later.")
                return
            rem = self._otp_attempts_left
            self._otp_attempts_lbl.config(
                text=f"{rem} attempt{'s' if rem != 1 else ''} remaining",
                fg=theme.DANGER,
            )
            showerror("Error", "Incorrect OTP. Please try again.")
