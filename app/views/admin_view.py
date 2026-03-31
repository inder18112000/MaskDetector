from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox, Treeview, Style
from app.db import users as db_users
from app import theme


class view:
    def getValues(self):
        rows = db_users.get_all()
        for k in self.obj.get_children():
            self.obj.delete(k)
        for count, row in enumerate(rows):
            tag = 'even' if count % 2 == 0 else 'odd'
            self.obj.insert('', index=count, values=list(row), tags=(tag,))

    def __init__(self):
        self.root = Tk()
        theme.maximize(self.root)
        self.root.title('Mask Detector — View Admins')
        self.root.config(bg=theme.L_BG)

        style = Style()
        theme.style_treeview(style)

        # Header
        hdr = Frame(self.root, bg=theme.L_PANEL, height=70)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        Label(hdr, text="👥  Admin Management",
              font=theme.F_TITLE, bg=theme.L_PANEL, fg=theme.WHITE).pack(
              side=LEFT, padx=24, pady=14)

        Label(self.root, text="Double-click a row to edit or delete an admin.",
              font=theme.F_SMALL, bg=theme.L_BG, fg=theme.L_MUTED).pack(pady=(12, 4))

        # Treeview
        tree_frame = Frame(self.root, bg=theme.L_BG)
        tree_frame.pack(fill=BOTH, expand=True, padx=24, pady=8)

        col = ('Username', 'Email', 'Role')
        self.obj = Treeview(tree_frame, columns=col, style="Custom.Treeview",
                            selectmode='browse')
        for i in col:
            self.obj.heading(i, text=i)
        self.obj.column('Username', width=260, anchor=W)
        self.obj.column('Email',    width=320, anchor=W)
        self.obj.column('Role',     width=180, anchor=CENTER)
        self.obj['show'] = 'headings'

        self.obj.tag_configure('even', background=theme.L_INPUT)
        self.obj.tag_configure('odd',  background=theme.L_CARD)

        self.getValues()
        self.obj.bind('<Double-1>', self.onDoubleClick)
        self.obj.pack(fill=BOTH, expand=True)
        theme.fade_in(self.root)
        self.root.mainloop()

    def onDoubleClick(self, event):
        self.items = self.obj.item(self.obj.focus())['values']
        if not self.items:
            return

        self.r1 = Toplevel(self.root)
        self.r1.title('Edit Admin')
        self.r1.resizable(False, False)
        self.r1.configure(bg=theme.L_CARD)
        x = (self.r1.winfo_screenwidth()  // 2) - 240
        y = (self.r1.winfo_screenheight() // 2) - 200
        self.r1.geometry(f"480x400+{x}+{y}")
        self.r1.grab_set()

        f = Frame(self.r1, bg=theme.L_CARD, padx=36, pady=28)
        f.pack(fill=BOTH, expand=True)

        Label(f, text="Edit Admin Account",
              font=theme.F_HEAD, bg=theme.L_CARD, fg=theme.L_TEXT).pack(pady=(0, 20))

        Label(f, text="Email", font=theme.F_SUB,
              bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).pack(fill=X)
        self.txt1 = Entry(f, font=theme.F_ENTRY, width=44,
                          bg=theme.L_INPUT, fg=theme.L_MUTED,
                          relief=FLAT, highlightthickness=1,
                          highlightbackground=theme.L_BORDER)
        self.txt1.pack(ipady=6, pady=(2, 12))
        self.txt1.insert(0, self.items[1])
        self.txt1.config(state='readonly')

        Label(f, text="Username", font=theme.F_SUB,
              bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).pack(fill=X)
        self.txt2 = Entry(f, font=theme.F_ENTRY, width=44,
                          bg=theme.L_INPUT, fg=theme.L_TEXT,
                          relief=FLAT, highlightthickness=1,
                          highlightbackground=theme.L_BORDER,
                          highlightcolor=theme.L_PANEL,
                          insertbackground=theme.L_TEXT)
        self.txt2.pack(ipady=6, pady=(2, 12))
        self.txt2.insert(0, self.items[0])

        Label(f, text="Role", font=theme.F_SUB,
              bg=theme.L_CARD, fg=theme.L_TEXT, anchor=W).pack(fill=X)
        self.txt3 = Combobox(f, values=['Super Admin', 'Admin'],
                             font=theme.F_ENTRY, width=42, state='readonly')
        self.txt3.pack(ipady=4, pady=(2, 20))
        col = ['Super Admin', 'Admin']
        self.txt3.current(col.index(self.items[2]))

        btn_row = Frame(f, bg=theme.L_CARD)
        btn_row.pack()
        theme.btn(btn_row, "💾  Update", self.updateUser,
                  bg=theme.L_PANEL, width=160).grid(row=0, column=0, padx=8)
        theme.btn(btn_row, "🗑  Delete", self.deleteUser,
                  bg=theme.DANGER, width=160).grid(row=0, column=1, padx=8)

        self.r1.mainloop()

    def updateUser(self):
        db_users.update(self.txt1.get(), self.txt2.get(), self.txt3.get())
        showinfo("Updated", "Admin updated successfully.")
        self.getValues()
        self.r1.destroy()

    def deleteUser(self):
        if askyesno("Confirm Delete", f"Delete admin '{self.items[0]}'? This cannot be undone."):
            db_users.delete(self.txt1.get())
            self.getValues()
            self.r1.destroy()
