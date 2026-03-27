from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox, Style
import sms_sending
from app.paths import Images
from app.db import complaints as db_complaints
from app.db import locations as db_locations
from app import theme


class comp:
    def back(self):
        self.com.destroy()
        from app.views.login import log
        log()

    def sub_comp(self):
        if str(self.r.get()) == "other":
            self.report = self.T.get(1.0, "end-1c").strip()
        else:
            self.report = str(self.r.get())

        name  = self.name.get().strip()
        phone = self.phone.get().strip()
        email = self.email.get().strip()
        loc   = self.s_loc.get()

        if not name or not phone or not email or not loc:
            showerror('Missing Fields', 'Please fill in all required fields.')
            return

        if db_complaints.get_by_email(email) is not None:
            showerror('', 'A complaint has already been registered with this email.')
            return

        db_complaints.create(name, phone, email, self.report, loc)
        showinfo("Submitted", "Your complaint has been registered successfully.")
        sms_sending.send_sms(phone)
        self.com.destroy()
        from app.views.login import log
        log()

    def ShowChoice(self):
        self.T.config(state=DISABLED)
        self.T.delete(1.0, END)
        if str(self.r.get()) == "other":
            self.T.config(state=NORMAL)

    def __init__(self):
        self.com = Tk()
        self.com.state("zoomed")
        self.com.title("Mask Detector — Register Complaint")
        self.icon_photo = PhotoImage(file=Images.ICON)
        self.com.iconphoto(False, self.icon_photo)

        # Background
        self.bg_photo = PhotoImage(file=Images.COMP_BG)
        Label(self.com, image=self.bg_photo, bd=0).place(x=0, y=0, relwidth=1, relheight=1)

        # ── Card ─────────────────────────────────────────────────────────────
        card = Frame(self.com, bg=theme.L_CARD, padx=40, pady=32)
        card.place(relx=0.5, rely=0.5, anchor=CENTER)

        Label(card, text="Register a Complaint",
              font=theme.F_TITLE, bg=theme.L_CARD, fg=theme.L_PANEL).grid(
              row=0, column=0, columnspan=2, pady=(0, 4))
        Label(card, text="Report mask or social distancing violations",
              font=theme.F_SMALL, bg=theme.L_CARD, fg=theme.L_MUTED).grid(
              row=1, column=0, columnspan=2, pady=(0, 16))

        Frame(card, bg=theme.L_BORDER, height=1).grid(
              row=2, column=0, columnspan=2, sticky=EW, pady=(0, 14))

        style = Style()
        style.configure('my.TCombobox', arrowsize=20)

        entry_cfg = dict(font=theme.F_ENTRY, width=34,
                         bg=theme.L_INPUT, fg=theme.L_TEXT,
                         relief=FLAT, highlightthickness=1,
                         highlightbackground=theme.L_BORDER,
                         highlightcolor=theme.L_PANEL,
                         insertbackground=theme.L_TEXT)

        for row, label in [(3, "Full Name"), (4, "Phone Number"), (5, "Email Address")]:
            Label(card, text=label, font=theme.F_SUB,
                  bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).grid(
                  row=row, column=0, sticky=W, padx=(0, 16), pady=4)

        self.name  = Entry(card, **entry_cfg)
        self.name.grid(row=3, column=1, ipady=7, pady=4)
        self.phone = Entry(card, **entry_cfg)
        self.phone.grid(row=4, column=1, ipady=7, pady=4)
        self.email = Entry(card, **entry_cfg)
        self.email.grid(row=5, column=1, ipady=7, pady=4)

        Label(card, text="Surveillance Location", font=theme.F_SUB,
              bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).grid(
              row=6, column=0, sticky=W, padx=(0, 16), pady=4)
        self.s_loc = Combobox(card, values=db_locations.get_all(),
                              font=theme.F_ENTRY, width=32,
                              state='readonly', style='my.TCombobox')
        self.s_loc.grid(row=6, column=1, ipady=4, pady=4)

        Label(card, text="Violation Type", font=theme.F_SUB,
              bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).grid(
              row=7, column=0, sticky=W, padx=(0, 16), pady=(12, 4))

        self.r = StringVar(value="Wearing Mask Violation")
        radio_frame = Frame(card, bg=theme.L_CARD)
        radio_frame.grid(row=7, column=1, sticky=W, pady=(12, 4))

        for text, val in [
            ("Mask Violation",              "Wearing Mask Violation"),
            ("Social Distancing Violation", "Social Distancing Violation"),
            ("Other (describe below)",      "other"),
        ]:
            Radiobutton(radio_frame, text=text, variable=self.r, value=val,
                        font=theme.F_BODY, bg=theme.L_CARD, fg=theme.L_TEXT,
                        activebackground=theme.L_CARD,
                        selectcolor=theme.L_INPUT,
                        command=self.ShowChoice).pack(anchor=W)

        Label(card, text="Description", font=theme.F_SUB,
              bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).grid(
              row=8, column=0, sticky=NW, padx=(0, 16), pady=(8, 4))
        self.T = Text(card, font=theme.F_ENTRY, height=5, width=34,
                      bg=theme.L_INPUT, fg=theme.L_TEXT,
                      relief=FLAT, highlightthickness=1,
                      highlightbackground=theme.L_BORDER,
                      highlightcolor=theme.L_PANEL,
                      insertbackground=theme.L_TEXT,
                      padx=8, pady=6)
        self.T.grid(row=8, column=1, pady=(8, 4))
        self.T.config(state=DISABLED)

        Frame(card, bg=theme.L_BORDER, height=1).grid(
              row=9, column=0, columnspan=2, sticky=EW, pady=14)

        btn_row = Frame(card, bg=theme.L_CARD)
        btn_row.grid(row=10, column=0, columnspan=2)

        theme.btn(btn_row, "← Back", self.back,
                  bg=theme.L_MUTED, width=160).grid(row=0, column=0, padx=8)
        theme.btn(btn_row, "Submit Complaint", self.sub_comp,
                  bg=theme.ACCENT, width=200).grid(row=0, column=1, padx=8)

        self.com.mainloop()
