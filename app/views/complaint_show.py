from tkinter import *
from tkinter.ttk import Combobox, Style, Treeview
from app.db import complaints as db_complaints
from app.db import locations as db_locations
from app import theme


class comp_show:
    def __init__(self):
        self.root = Tk()
        theme.maximize(self.root)
        self.root.title('Mask Detector — Registered Complaints')
        self.root.config(bg=theme.L_BG)

        style = Style()
        theme.style_treeview(style)
        style.configure('my.TCombobox', arrowsize=20)

        # Header
        hdr = Frame(self.root, bg=theme.L_PANEL, height=70)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        Label(hdr, text="📋  Registered Complaints",
              font=theme.F_TITLE, bg=theme.L_PANEL, fg=theme.WHITE).pack(
              side=LEFT, padx=24, pady=14)

        # Filter bar
        bar = Frame(self.root, bg=theme.L_CARD, pady=12)
        bar.pack(fill=X, padx=24, pady=(16, 0))

        Label(bar, text="Filter by Location:",
              font=theme.F_SUB, bg=theme.L_CARD, fg=theme.L_TEXT).pack(side=LEFT, padx=(12, 8))

        self.l = db_locations.get_all() + ["All Locations"]
        self.s_loc = Combobox(bar, values=self.l, font=theme.F_ENTRY,
                              width=24, state='readonly', style='my.TCombobox')
        self.s_loc.pack(side=LEFT, ipady=4, padx=(0, 12))
        self.s_loc.set("All Locations")

        theme.btn(bar, "🔍  Search", self.search, width=140).pack(side=LEFT, padx=4)

        # Treeview
        tree_frame = Frame(self.root, bg=theme.L_BG)
        tree_frame.pack(fill=BOTH, expand=True, padx=24, pady=16)

        col = ('ID', 'Name', 'Mobile', 'Email', 'Report', 'Location', 'Status')
        self.obj = Treeview(tree_frame, columns=col,
                            style="Custom.Treeview", selectmode='browse')
        for i in col:
            self.obj.heading(i, text=i)

        widths = {'ID': 50, 'Name': 140, 'Mobile': 110, 'Email': 200,
                  'Report': 260, 'Location': 160, 'Status': 200}
        for c in col:
            self.obj.column(c, width=widths.get(c, 120), anchor=W)
        self.obj['show'] = 'headings'

        self.obj.tag_configure('even', background=theme.L_INPUT)
        self.obj.tag_configure('odd',  background=theme.L_CARD)

        sb = Scrollbar(tree_frame, orient=VERTICAL, command=self.obj.yview)
        self.obj.configure(yscrollcommand=sb.set)
        sb.pack(side=RIGHT, fill=Y)
        sb_h = Scrollbar(tree_frame, orient=HORIZONTAL, command=self.obj.xview)
        self.obj.configure(xscrollcommand=sb_h.set)
        sb_h.pack(side=BOTTOM, fill=X)
        self.obj.pack(fill=BOTH, expand=True)

        self.search()
        theme.fade_in(self.root)
        self.root.mainloop()

    def search(self):
        s = self.s_loc.get()
        rows = (db_complaints.get_all()
                if s in ("All Locations", "")
                else db_complaints.get_by_location(s))
        for k in self.obj.get_children():
            self.obj.delete(k)
        for count, row in enumerate(rows):
            tag = 'even' if count % 2 == 0 else 'odd'
            self.obj.insert('', index=count, values=row, tags=(tag,))
