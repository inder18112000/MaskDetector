# ── Shared UI Theme ──────────────────────────────────────────────────────────

# Light palette
L_BG      = "#f0f2f5"
L_PANEL   = "#1a73e8"
L_PANEL2  = "#1557b0"
L_FG      = "#ffffff"
L_TEXT    = "#202124"
L_MUTED   = "#5f6368"
L_CARD    = "#ffffff"
L_INPUT   = "#f8f9fa"
L_BORDER  = "#dadce0"

# Dark palette
D_BG      = "#0f0f0f"
D_PANEL   = "#1e1e2e"
D_PANEL2  = "#2a2a3d"
D_FG      = "#cdd6f4"
D_MUTED   = "#6c7086"
D_CARD    = "#1e1e2e"
D_INPUT   = "#181825"
D_BORDER  = "#313244"

# Accents
SUCCESS   = "#34a853"
SUCCESS2  = "#2d9248"
DANGER    = "#ea4335"
DANGER2   = "#c5221f"
WARNING   = "#fbbc04"
ACCENT    = "#ff6b35"
ACCENT2   = "#e55a28"
WHITE     = "#ffffff"

# Fonts
F_TITLE   = ('Helvetica', 22, 'bold')
F_HEAD    = ('Helvetica', 16, 'bold')
F_SUB     = ('Helvetica', 13, 'bold')
F_BODY    = ('Helvetica', 12)
F_SMALL   = ('Helvetica', 10)
F_BTN     = ('Helvetica', 12, 'bold')
F_ENTRY   = ('Helvetica', 12)
F_TABLE   = ('Helvetica', 11)


# ── Custom Canvas Button ──────────────────────────────────────────────────────

class StyledButton:
    """
    A Canvas-based button that works correctly on macOS.
    Supports custom bg/fg colours, hover effects, and disabled state.
    """

    def __init__(self, parent, text, command,
                 bg=L_PANEL, fg=WHITE,
                 hover_bg=None,
                 font=F_BTN,
                 width=160, height=38,
                 radius=8, padx=18):

        self._command  = command
        self._bg       = bg
        self._fg       = fg
        self._hover_bg = hover_bg or self._darken(bg)
        self._font     = font
        self._disabled = False
        self._text     = text

        self.canvas = __import__('tkinter').Canvas(
            parent,
            width=width, height=height,
            bg=parent.cget('bg'),
            highlightthickness=0,
            cursor="hand2",
        )

        self._w = width
        self._h = height
        self._r = radius

        self._draw(self._bg)

        self.canvas.bind("<Enter>",          self._on_enter)
        self.canvas.bind("<Leave>",          self._on_leave)
        self.canvas.bind("<ButtonPress-1>",  self._on_press)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    # ── public geometry methods (mimic tk widget) ─────────────────────────────
    def pack(self, **kw):   self.canvas.pack(**kw)
    def grid(self, **kw):   self.canvas.grid(**kw)
    def place(self, **kw):  self.canvas.place(**kw)
    def pack_forget(self):  self.canvas.pack_forget()
    def grid_forget(self):  self.canvas.grid_forget()

    def config(self, **kw):
        if 'state' in kw:
            if kw['state'] == 'disabled':
                self._disabled = True
                self.canvas.config(cursor="")
                self._draw("#aaaaaa")
            else:
                self._disabled = False
                self.canvas.config(cursor="hand2")
                self._draw(self._bg)
        if 'text' in kw:
            self._text = kw['text']
            self._draw(self._bg)

    def __setitem__(self, key, value):
        self.config(**{key: value})

    # ── drawing ───────────────────────────────────────────────────────────────
    def _draw(self, fill):
        self.canvas.delete("all")
        self._rounded_rect(0, 0, self._w, self._h, self._r, fill)
        self.canvas.create_text(
            self._w // 2, self._h // 2,
            text=self._text,
            fill=self._fg if not self._disabled else "#eeeeee",
            font=self._font,
        )

    def _rounded_rect(self, x1, y1, x2, y2, r, fill):
        c = self.canvas
        c.create_arc(x1, y1, x1+2*r, y1+2*r, start=90,  extent=90,  fill=fill, outline=fill)
        c.create_arc(x2-2*r, y1, x2, y1+2*r, start=0,   extent=90,  fill=fill, outline=fill)
        c.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90,  fill=fill, outline=fill)
        c.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90,  fill=fill, outline=fill)
        c.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline=fill)
        c.create_rectangle(x1, y1+r, x2, y2-r, fill=fill, outline=fill)

    @staticmethod
    def _darken(hex_color):
        """Return a slightly darker shade of a hex colour."""
        try:
            h = hex_color.lstrip('#')
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            r = max(0, int(r * 0.82))
            g = max(0, int(g * 0.82))
            b = max(0, int(b * 0.82))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    # ── event handlers ────────────────────────────────────────────────────────
    def _on_enter(self, _):
        if not self._disabled:
            self._draw(self._hover_bg)

    def _on_leave(self, _):
        if not self._disabled:
            self._draw(self._bg)

    def _on_press(self, _):
        if not self._disabled:
            self._draw(self._darken(self._hover_bg))

    def _on_release(self, _):
        if not self._disabled:
            self._draw(self._hover_bg)
            self._command()


def btn(parent, text, command,
        bg=L_PANEL, fg=WHITE,
        width=160, height=38,
        hover_bg=None, font=F_BTN):
    """Return a StyledButton (Canvas-based, macOS-compatible)."""
    return StyledButton(parent, text, command,
                        bg=bg, fg=fg,
                        hover_bg=hover_bg,
                        font=font,
                        width=width, height=height)


def style_treeview(style, bg=L_CARD, fg=L_TEXT, heading_bg=L_PANEL,
                   heading_fg=WHITE, row_bg=L_INPUT, alt_bg="#e8f0fe"):
    """Apply consistent Treeview styling."""
    style.configure("Custom.Treeview",
                    background=row_bg,
                    foreground=fg,
                    fieldbackground=row_bg,
                    font=F_TABLE,
                    rowheight=32)
    style.configure("Custom.Treeview.Heading",
                    background=heading_bg,
                    foreground=heading_fg,
                    font=('Helvetica', 11, 'bold'),
                    relief="flat")
    style.map("Custom.Treeview",
              background=[('selected', heading_bg)],
              foreground=[('selected', heading_fg)])
    style.map("Custom.Treeview.Heading",
              background=[('active', heading_bg)])
