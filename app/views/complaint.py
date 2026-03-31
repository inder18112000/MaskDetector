from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox, Style
import sms_sending
from app.paths import Images
from app.db import complaints as db_complaints
from app.db import locations as db_locations
from app import theme
from app.validators import require, valid_email, valid_phone
from PIL import Image, ImageTk

# ── palette ──────────────────────────────────────────────────────────────────
PRIMARY  = "#1a73e8"
PRIMARY2 = "#1557b0"
ACCENT   = "#ff6b35"
CARD     = "#ffffff"
INPUT    = "#f8f9fa"
TEXT     = "#202124"
MUTED    = "#5f6368"
BORDER   = "#dadce0"
SUCCESS  = "#34a853"
DISABLED_BG  = "#efefef"
DISABLED_FG  = "#aaaaaa"


class comp:

    # ── helpers ───────────────────────────────────────────────────────────────
    def _build_loc_map(self):
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

    def _resize_bg(self, event=None):
        w = self.com.winfo_width()
        h = self.com.winfo_height()
        if w < 10 or h < 10:
            return
        img = Image.open(self._bg_src).resize((w, h), Image.LANCZOS).convert('RGBA')
        # Dark overlay so the white card stands out clearly
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 150))
        img = Image.alpha_composite(img, overlay).convert('RGB')
        self._bg_photo = ImageTk.PhotoImage(img)
        self._bg_label.config(image=self._bg_photo)

    def _section_header(self, parent, text, row):
        """Render a section label with a coloured left-accent bar."""
        f = Frame(parent, bg=CARD)
        f.grid(row=row, column=0, columnspan=4, sticky=EW, pady=(18, 6))
        Frame(f, bg=PRIMARY, width=3, height=16).pack(side=LEFT)
        Label(f, text=f"  {text}",
              font=('Helvetica', 10, 'bold'), bg=CARD,
              fg=MUTED).pack(side=LEFT)

    def _field(self, parent, label, row, col, colspan=1, width=22):
        """Label + Entry helper. Returns the Entry widget."""
        Label(parent, text=label,
              font=('Helvetica', 10, 'bold'), bg=CARD,
              fg=MUTED, anchor=W).grid(
              row=row, column=col, columnspan=colspan,
              sticky=W, padx=(4, 4), pady=(0, 3))
        e = Entry(parent, font=('Helvetica', 12), width=width,
                  bg=INPUT, fg=TEXT, relief=FLAT,
                  highlightthickness=1,
                  highlightbackground=BORDER,
                  highlightcolor=PRIMARY,
                  insertbackground=TEXT)
        e.grid(row=row + 1, column=col, columnspan=colspan,
               ipady=8, padx=(4, 4), pady=(0, 4), sticky=EW)
        return e

    # ── actions ───────────────────────────────────────────────────────────────
    def back(self):
        self.com.destroy()
        from app.views.login import log
        log()

    def ShowChoice(self):
        is_other = str(self.r.get()) == "other"
        self.T.config(
            state=NORMAL if is_other else DISABLED,
            bg=INPUT if is_other else DISABLED_BG,
            fg=TEXT if is_other else DISABLED_FG,
        )
        if not is_other:
            self.T.delete(1.0, END)
        self._desc_hint.config(
            text="" if is_other else "Enable by selecting 'Other' above")

    def sub_comp(self):
        name  = self.name_e.get().strip()
        phone = self.phone_e.get().strip()
        email = self.email_e.get().strip()
        loc   = self._loc_map.get(self.s_loc.get(), "")

        if not require([("your full name", self.name_e),
                        ("your phone number", self.phone_e),
                        ("your email address", self.email_e)]):
            return
        if not valid_phone(phone, self.phone_e):
            return
        if not valid_email(email, self.email_e):
            return
        if not loc:
            if not self._loc_map:
                showerror('No Locations',
                          'No surveillance locations are configured yet.\n'
                          'Please contact an administrator.')
            else:
                showerror('Missing Field', 'Please select a surveillance location.')
            return

        if str(self.r.get()) == "other":
            report = self.T.get(1.0, "end-1c").strip()
            if not report:
                showerror('Missing Description',
                          'Please describe the violation in the description box.')
                self.T.focus(); return
        else:
            report = str(self.r.get())

        if db_complaints.get_by_email(email) is not None:
            showerror('Already Submitted',
                      'A complaint has already been registered with this email address.')
            self.email_e.focus(); return

        cid = db_complaints.create(name, phone, email, report, loc)
        try:
            sms_sending.send_sms(phone)
        except Exception:
            pass

        # ── Confirmation card ─────────────────────────────────────────────────
        for w in self.card.winfo_children():
            w.destroy()

        conf = Frame(self.card, bg=CARD, padx=52, pady=44)
        conf.pack()
        Label(conf, text="✔  Complaint Registered",
              font=('Helvetica', 20, 'bold'), bg=CARD, fg=SUCCESS).pack(pady=(0, 10))
        Frame(conf, bg=BORDER, height=1).pack(fill=X, pady=(0, 20))
        Label(conf, text="Reference Number",
              font=('Helvetica', 11), bg=CARD, fg=MUTED).pack()
        Label(conf, text=f"CMP-{cid:04d}",
              font=('Helvetica', 30, 'bold'), bg=CARD, fg=PRIMARY).pack(pady=(4, 14))
        Label(conf,
              text=f"An SMS confirmation has been sent to {phone}.",
              font=('Helvetica', 11), bg=CARD, fg=MUTED).pack(pady=(0, 28))
        theme.btn(conf, "← Back to Login", self.back, width=220).pack()

    # ── init ──────────────────────────────────────────────────────────────────
    def __init__(self):
        self.com = Tk()
        self.com.withdraw()          # hide default small window immediately
        theme.maximize(self.com)
        self.com.title("Mask Detector — Register Complaint")
        self.icon_photo = PhotoImage(file=Images.ICON)
        self.com.iconphoto(False, self.icon_photo)

        # Resizable background (same image as login, darkened overlay applied in _resize_bg)
        self._bg_src   = Images.FRONT_LOGIN
        self._bg_label = Label(self.com, bd=0)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.com.bind("<Configure>", self._resize_bg)
        self.com.update_idletasks()
        self._resize_bg()

        # ── Outer card (shadow effect via offset frame) ───────────────────────
        shadow = Frame(self.com, bg="#cccccc")
        shadow.place(relx=0.502, rely=0.502, anchor=CENTER)

        card = Frame(shadow, bg=CARD)
        card.pack(padx=(0, 3), pady=(0, 3))
        self.card = card

        style = Style()
        style.configure('comp.TCombobox', arrowsize=20, font=('Helvetica', 12))

        # ── Coloured header band ──────────────────────────────────────────────
        header = Frame(card, bg=PRIMARY, padx=36, pady=22)
        header.grid(row=0, column=0, sticky=EW)

        # Back button — top-left of header, always visible
        theme.btn(header, "← Back", self.back,
                  bg=PRIMARY2, fg="white", width=90, height=30,
                  font=('Helvetica', 10, 'bold')).pack(anchor=W, pady=(0, 10))

        Label(header, text="Register a Complaint",
              font=('Helvetica', 20, 'bold'),
              bg=PRIMARY, fg="white").pack(anchor=W)
        Label(header, text="Report mask non-compliance at a surveillance location",
              font=('Helvetica', 10),
              bg=PRIMARY, fg="#c8d8f8").pack(anchor=W, pady=(3, 0))

        # ── Form body ─────────────────────────────────────────────────────────
        body = Frame(card, bg=CARD, padx=36, pady=20)
        body.grid(row=1, column=0, sticky=NSEW)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0, minsize=16)   # gutter
        body.columnconfigure(2, weight=1)
        body.columnconfigure(3, weight=0)

        # ── Personal info ─────────────────────────────────────────────────────
        self._section_header(body, "PERSONAL INFORMATION", row=0)

        self.name_e  = self._field(body, "Full Name",     row=1, col=0, colspan=1, width=20)
        self.phone_e = self._field(body, "Phone Number",  row=1, col=2, colspan=2, width=20)
        self.email_e = self._field(body, "Email Address", row=3, col=0, colspan=4, width=46)

        # ── Location ──────────────────────────────────────────────────────────
        self._section_header(body, "SURVEILLANCE LOCATION", row=5)

        self._loc_map = {}
        loc_vals = self._build_loc_map()

        Label(body, text="Select Location",
              font=('Helvetica', 10, 'bold'), bg=CARD, fg=MUTED, anchor=W).grid(
              row=6, column=0, columnspan=4, sticky=W, padx=4, pady=(0, 3))
        self.s_loc = Combobox(body, values=loc_vals,
                              font=('Helvetica', 12), width=44,
                              state='readonly', style='comp.TCombobox')
        self.s_loc.grid(row=7, column=0, columnspan=4,
                        ipady=6, padx=4, pady=(0, 4), sticky=EW)

        # ── Violation type ────────────────────────────────────────────────────
        self._section_header(body, "VIOLATION TYPE", row=8)

        self.r = StringVar(value="Wearing Mask Violation")
        rf = Frame(body, bg=INPUT, bd=0, highlightthickness=1,
                   highlightbackground=BORDER)
        rf.grid(row=9, column=0, columnspan=4, sticky=EW, padx=4, pady=(0, 4))

        for text, val in [
            ("🦺  Mask Not Worn",              "Wearing Mask Violation"),
            ("↔️  Social Distancing Violation", "Social Distancing Violation"),
            ("✏️  Other (describe below)",      "other"),
        ]:
            rb = Radiobutton(rf, text=f"  {text}", variable=self.r, value=val,
                             font=('Helvetica', 11), bg=INPUT, fg=TEXT,
                             activebackground=INPUT, selectcolor=CARD,
                             command=self.ShowChoice,
                             padx=12, pady=5,
                             indicatoron=True)
            rb.pack(anchor=W, fill=X)
            Frame(rf, bg=BORDER, height=1).pack(fill=X)

        # ── Description ───────────────────────────────────────────────────────
        self._section_header(body, "ADDITIONAL DESCRIPTION", row=10)

        self._desc_hint = Label(body,
                                text="Enable by selecting 'Other' above",
                                font=('Helvetica', 9, 'italic'),
                                bg=CARD, fg=DISABLED_FG, anchor=W)
        self._desc_hint.grid(row=11, column=0, columnspan=4,
                             sticky=W, padx=4, pady=(0, 3))

        self.T = Text(body, font=('Helvetica', 12), height=4, width=46,
                      bg=DISABLED_BG, fg=DISABLED_FG, relief=FLAT,
                      highlightthickness=1, highlightbackground=BORDER,
                      highlightcolor=PRIMARY, insertbackground=TEXT,
                      padx=10, pady=8)
        self.T.grid(row=12, column=0, columnspan=4,
                    padx=4, pady=(0, 4), sticky=EW)
        self.T.config(state=DISABLED)

        # ── Footer ────────────────────────────────────────────────────────────
        footer = Frame(card, bg="#f5f7fa", padx=36, pady=16)
        footer.grid(row=2, column=0, sticky=EW)

        Frame(footer, bg=BORDER, height=1).pack(fill=X, pady=(0, 14))

        btn_row = Frame(footer, bg="#f5f7fa")
        btn_row.pack()

        theme.btn(btn_row, "✔  Submit Complaint", self.sub_comp,
                  bg=SUCCESS, width=220).pack()

        self.name_e.focus()
        self.com.deiconify()
        theme.fade_in(self.com)
        self.com.mainloop()
