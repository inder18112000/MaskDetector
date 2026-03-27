import cv2
import PIL.Image, PIL.ImageTk
from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox, Style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import app.state as state
from app.camera.video_capture import MyVideoCapture
from app.paths import Images
from app.db import locations as db_locations
from app.db import surveillance as db_surv
from app import theme

BG    = theme.D_BG
PANEL = theme.D_PANEL
FG    = theme.D_FG
CARD  = theme.D_CARD


class dasboard:
    # ── navigation ────────────────────────────────────────────────────────────
    def view(self):
        from app.views.admin_view import view
        view()

    def add(self):
        self.rootd.destroy()
        from app.views.admin_add import add
        add()

    def comp_show(self):
        from app.views.complaint_show import comp_show
        comp_show()

    def showsurv(self):
        from app.views.surveillance_history import showsurv
        showsurv()

    def light(self):
        self.rootd.destroy()
        from app.views.dashboard_light import dasboard_light
        dasboard_light(state.result)

    def lg(self):
        self.rootd.destroy()
        from app.views.login import log
        log()

    # ── location management ───────────────────────────────────────────────────
    def addl(self):
        s = self.loc.get().strip()
        if not s:
            showerror("Error", "Location name cannot be empty.")
            return
        if not db_locations.exists(s):
            db_locations.create(s)
            showinfo("Add Location", "Location added successfully.")
        else:
            showerror("Error", "Location already exists.")
        self.rootadd.destroy()

    def addloc(self):
        self.rootadd = Toplevel(self.rootd)
        self.rootadd.title("Add Surveillance Location")
        self.rootadd.resizable(False, False)
        self.rootadd.configure(bg=CARD)
        x = (self.rootadd.winfo_screenwidth()  // 2) - 200
        y = (self.rootadd.winfo_screenheight() // 2) - 110
        self.rootadd.geometry(f"400x220+{x}+{y}")
        self.rootadd.grab_set()

        f = Frame(self.rootadd, bg=CARD, padx=30, pady=24)
        f.pack(fill=BOTH, expand=True)

        Label(f, text="New Surveillance Location",
              font=theme.F_SUB, bg=CARD, fg=FG).pack(pady=(0, 14))
        self.loc = Entry(f, font=theme.F_ENTRY, width=34,
                         bg=theme.D_INPUT, fg=FG, insertbackground=FG,
                         relief=FLAT, highlightthickness=1,
                         highlightbackground=theme.D_BORDER,
                         highlightcolor=theme.L_PANEL)
        self.loc.pack(ipady=7, pady=(0, 16))
        self.loc.focus()
        theme.btn(f, "Add Location", self.addl, width=240).pack()

    # ── surveillance save ─────────────────────────────────────────────────────
    def sur(self):
        db_surv.create(
            str(self.s_loc.get()), str(self.txt2.get()), str(self.txt1.get()),
            str(self.txt3.get()), str(self.mp.get()), str(self.up.get()),
        )
        showinfo("Saved", "Surveillance data saved successfully.")

    # ── camera ────────────────────────────────────────────────────────────────
    def start_camera(self):
        # Clear any existing chart
        if self._chart_widget is not None:
            self._chart_widget.destroy()
            self._chart_widget = None

        self.submit["state"] = DISABLED
        self.masked = 0
        self.unmasked = 0
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

        for entry, row in [(self.txt3, 7), (self.mp, 9), (self.up, 10)]:
            entry.config(state="normal")
            entry.delete(0, END)
            entry.config(state="disabled")
            entry.grid(row=row, column=1, padx=8, pady=4)

        self.cap = MyVideoCapture()
        try:
            self.cap.startVideo(int(str(self.mode.get())))
        except ValueError:
            self.start["state"] = NORMAL
            self.submit["state"] = DISABLED
            showerror("Camera Error",
                      "Could not open camera.\n\n"
                      "• Check that the camera index is correct.\n"
                      "• On macOS, grant camera access in System Settings → Privacy → Camera.")
            return

        self.cap_width  = int(self.cap.width)  + 200
        self.cap_height = int(self.cap.height) + 100

        self.camera = Frame(self.main_frame, bg=BG)
        self.canvas = Canvas(self.camera,
                             width=self.cap_width,
                             height=self.cap_height,
                             bg=BG, highlightthickness=0)
        self.canvas.pack(expand=True)
        self.camera.pack(fill=BOTH, expand=True)

        self.stop["state"] = NORMAL
        self.delay = 15
        self.flag = True
        self.update()

    def stop_camera(self):
        self.submit["state"] = NORMAL
        self.start["state"] = NORMAL
        self.stop["state"] = DISABLED

        self.txt3.config(state="normal")
        self.txt3.delete(0, END)
        self.txt3.insert(0, datetime.now().strftime("%H:%M:%S"))
        self.txt3.config(state="disabled")
        self.txt3.grid(row=7, column=1, padx=8, pady=4)

        total = int(self.masked) + int(self.unmasked)
        m_pct = (int(self.masked) / total) * 100 if total else 0
        u_pct = (int(self.unmasked) / total) * 100 if total else 0

        for entry, row, val in [
            (self.mp, 9,  f"{m_pct:.1f} %"),
            (self.up, 10, f"{u_pct:.1f} %"),
        ]:
            entry.config(state="normal")
            entry.delete(0, END)
            entry.insert(0, val)
            entry.config(state="disabled")
            entry.grid(row=row, column=1, padx=8, pady=4)

        if self.flag:
            self.cap.camera_release()
            self.canvas.destroy()
            if state.vid:
                state.vid.release()
            self.flag = False
            self.camera.destroy()

        fig = Figure(facecolor=CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD)
        ax.pie([self.masked, self.unmasked], radius=1,
               labels=["Masked", "Unmasked"],
               colors=[theme.SUCCESS, theme.DANGER],
               autopct='%0.1f%%', shadow=False,
               wedgeprops=dict(width=0.6),
               textprops=dict(color=FG))
        ax.set_title("Mask Compliance", fontsize=13, fontweight='bold', color=FG)
        chart = FigureCanvasTkAgg(fig, self.main_frame)
        self._chart_widget = chart.get_tk_widget()
        self._chart_widget.pack(fill=BOTH, expand=True, padx=40, pady=40)

    def update(self):
        if not self.flag:
            return

        from app.camera.mask_detector import detect, MASKED, UNMASKED

        font       = cv2.FONT_HERSHEY_SIMPLEX
        color_ok   = (52, 168, 83)
        color_warn = (234, 67, 53)
        thickness  = 2

        ret, img = self.cap.get_frame()
        if not ret or img is None:
            self.rootd.after(self.delay, self.update)
            return
        img = cv2.resize(img, (850, 600))
        img = cv2.flip(img, 1)

        detections, has_face = detect(img)

        if not has_face:
            cv2.putText(img, "No face detected", (30, 40), font, 0.8,
                        (200, 200, 200), thickness, cv2.LINE_AA)
        else:
            for (x, y, w, h, status) in detections:
                if status == MASKED:
                    color = color_ok
                    label = "Mask On"
                    self.masked += 1
                else:
                    color = color_warn
                    label = "No Mask!"
                    self.unmasked += 1
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, max(y - 8, 16)), font, 0.7,
                            color, thickness, cv2.LINE_AA)

        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.rootd.after(self.delay, self.update)

    # ── init ──────────────────────────────────────────────────────────────────
    def __init__(self, result):
        state.mode = 1
        self.rootd = Tk()
        self.rootd.state("zoomed")
        self.rootd.title("Mask Detector")
        self.icon_photo = PhotoImage(file=Images.ICON)
        self.rootd.iconphoto(False, self.icon_photo)
        self.rootd.config(bg=BG)
        self.rootd.minsize(900, 600)

        style = Style()
        style.configure('my.TCombobox', arrowsize=20, font=theme.F_ENTRY)

        self.flag = False
        self._chart_widget = None
        self.cap_width  = 1050
        self.cap_height = 700

        # ── Top nav bar (pack first so it's on top) ───────────────────────────
        nav = Frame(self.rootd, bg=PANEL, height=50)
        nav.pack(side=TOP, fill=X)
        nav.pack_propagate(False)

        self.ad_btn   = theme.btn(nav, "➕  Add Admin",   self.add,       width=150)
        self.view_btn = theme.btn(nav, "👥  View Admins", self.view,      width=150)
        theme.btn(nav, "📋  Complaints", self.comp_show, width=150).pack(side=LEFT, padx=4, pady=6)
        theme.btn(nav, "📜  History",    self.showsurv,  width=150).pack(side=LEFT, padx=4, pady=6)
        self.ad_btn.pack(side=LEFT, padx=4, pady=6)
        self.view_btn.pack(side=LEFT, padx=4, pady=6)

        # ── Bottom bar ────────────────────────────────────────────────────────
        bottom = Frame(self.rootd, bg=theme.D_PANEL2, height=60)
        bottom.pack(side=BOTTOM, fill=X)
        bottom.pack_propagate(False)

        self.addloc_btn = theme.btn(bottom, "📍  Add Location", self.addloc, width=200)
        self.addloc_btn.pack(side=LEFT, padx=16, pady=10)

        theme.btn(bottom, "☀️  Light Mode", self.light,
                  bg=theme.L_PANEL, width=150).pack(side=LEFT, padx=8, pady=10)

        theme.btn(bottom, "⏻  Logout", self.lg,
                  bg=theme.DANGER, width=130).pack(side=RIGHT, padx=16, pady=10)

        # ── Left sidebar ──────────────────────────────────────────────────────
        self.bf1 = Frame(self.rootd, bg=PANEL, width=300)
        self.bf1.pack(side=LEFT, fill=Y)
        self.bf1.pack_propagate(False)

        # User info
        info_frame = Frame(self.bf1, bg=PANEL, pady=16)
        info_frame.pack(fill=X)

        Label(info_frame, text=result[0],
              font=theme.F_SUB, bg=PANEL, fg=FG).pack()
        Label(info_frame, text=f"[ {result[3]} ]",
              font=theme.F_SMALL, bg=PANEL, fg=theme.D_MUTED).pack()
        Label(info_frame, text=result[1],
              font=theme.F_SMALL, bg=PANEL, fg=theme.D_MUTED).pack(pady=(2, 0))

        Frame(self.bf1, bg=theme.D_BORDER, height=1).pack(fill=X, padx=16, pady=8)

        form_frame = Frame(self.bf1, bg=PANEL)
        form_frame.pack(fill=X, padx=12, pady=4)

        for row, text in [(4, "📍 Location"), (5, "📅 Date"),
                          (6, "🕐 Start Time"), (7, "🕐 End Time")]:
            Label(form_frame, text=text, font=theme.F_BODY,
                  bg=PANEL, fg=FG, anchor=W).grid(
                  row=row, column=0, sticky=W, padx=6, pady=3)

        Frame(self.bf1, bg=theme.D_BORDER, height=1).pack(fill=X, padx=16, pady=8)

        stat_frame = Frame(self.bf1, bg=PANEL)
        stat_frame.pack(fill=X, padx=12, pady=4)

        for row, text in [(9, "✅ Masked"), (10, "⚠️  Unmasked")]:
            Label(stat_frame, text=text, font=theme.F_BODY,
                  bg=PANEL, fg=FG, anchor=W).grid(
                  row=row, column=0, sticky=W, padx=6, pady=3)

        Frame(self.bf1, bg=theme.D_BORDER, height=1).pack(fill=X, padx=16, pady=8)

        cam_frame = Frame(self.bf1, bg=PANEL)
        cam_frame.pack(fill=X, padx=12)
        Label(cam_frame, text="📷 Camera Index",
              font=theme.F_BODY, bg=PANEL, fg=FG).grid(
              row=0, column=0, sticky=W, padx=6, pady=4)
        self.mode = Entry(cam_frame, font=theme.F_ENTRY, width=6,
                          relief=FLAT, highlightthickness=1,
                          highlightbackground=theme.D_BORDER,
                          highlightcolor=theme.L_PANEL,
                          bg=theme.D_INPUT, fg=FG,
                          insertbackground=FG, justify=CENTER)
        self.mode.insert(0, "0")
        self.mode.grid(row=0, column=1, padx=6, pady=4, ipady=4)

        self.s_loc = Combobox(form_frame, values=db_locations.get_all(),
                              font=theme.F_ENTRY, width=18,
                              state='readonly', style='my.TCombobox')
        self.s_loc.grid(row=4, column=1, padx=6, pady=3)

        entry_cfg = dict(font=theme.F_ENTRY, width=18, relief=FLAT,
                         bg=theme.D_INPUT, fg=FG,
                         disabledbackground=theme.D_INPUT,
                         disabledforeground=theme.D_MUTED,
                         highlightthickness=1,
                         highlightbackground=theme.D_BORDER)

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

        Frame(self.bf1, bg=theme.D_BORDER, height=1).pack(fill=X, padx=16, pady=8)

        btn_frame = Frame(self.bf1, bg=PANEL)
        btn_frame.pack(fill=X, padx=16, pady=8)

        self.start = theme.btn(btn_frame, "▶  Start", self.start_camera,
                               bg=theme.SUCCESS, width=120, height=38)
        self.start.grid(row=0, column=0, padx=4)

        self.stop = theme.btn(btn_frame, "■  Stop", self.stop_camera,
                              bg=theme.DANGER, width=120, height=38)
        self.stop.grid(row=0, column=1, padx=4)
        self.stop["state"] = DISABLED

        self.submit = theme.btn(self.bf1, "💾  Save Surveillance", self.sur, width=260, height=42)
        self.submit.pack(padx=16, pady=10)
        self.submit["state"] = DISABLED

        # ── Main content area ─────────────────────────────────────────────────
        self.main_frame = Frame(self.rootd, bg=BG)
        self.main_frame.pack(side=LEFT, fill=BOTH, expand=True)

        if result[3] == "Admin":
            self.ad_btn["state"]     = DISABLED
            self.view_btn["state"]   = DISABLED
            self.addloc_btn["state"] = DISABLED

        self.rootd.mainloop()
