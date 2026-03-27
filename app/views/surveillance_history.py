from tkinter import *
from tkinter.ttk import Treeview, Style, Scrollbar
from app.db import surveillance as db_surv
from app import theme


class showsurv:
    def getValues(self):
        rows = db_surv.get_all()
        for k in self.obj.get_children():
            self.obj.delete(k)
        for count, row in enumerate(rows):
            tag = 'even' if count % 2 == 0 else 'odd'
            self.obj.insert('', index=count, values=list(row), tags=(tag,))

    def __init__(self):
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title('Mask Detector — Surveillance History')
        self.root.config(bg=theme.L_BG)

        style = Style()
        theme.style_treeview(style)

        # Header
        hdr = Frame(self.root, bg=theme.L_PANEL, height=70)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        Label(hdr, text="📜  Surveillance History",
              font=theme.F_TITLE, bg=theme.L_PANEL, fg=theme.WHITE).pack(
              side=LEFT, padx=24, pady=14)

        Label(self.root,
              text="All recorded surveillance sessions are listed below.",
              font=theme.F_SMALL, bg=theme.L_BG, fg=theme.L_MUTED).pack(pady=(12, 4))

        # Treeview
        tree_frame = Frame(self.root, bg=theme.L_BG)
        tree_frame.pack(fill=BOTH, expand=True, padx=24, pady=8)

        col = ('ID', 'Location', 'Date', 'Start', 'End', 'Masked %', 'Unmasked %')
        self.obj = Treeview(tree_frame, columns=col,
                            style="Custom.Treeview", selectmode='browse')
        for i in col:
            self.obj.heading(i, text=i)

        widths = {'ID': 50, 'Location': 180, 'Date': 120,
                  'Start': 100, 'End': 100, 'Masked %': 120, 'Unmasked %': 120}
        for c in col:
            self.obj.column(c, width=widths.get(c, 120), anchor=CENTER)
        self.obj['show'] = 'headings'

        self.obj.tag_configure('even', background=theme.L_INPUT)
        self.obj.tag_configure('odd',  background=theme.L_CARD)

        sb = Scrollbar(tree_frame, orient=VERTICAL, command=self.obj.yview)
        self.obj.configure(yscrollcommand=sb.set)
        sb.pack(side=RIGHT, fill=Y)
        self.obj.pack(fill=BOTH, expand=True)

        self.getValues()
        self.root.mainloop()
