PALETTE = {
    # Backgrounds — deep plum-violet with warm undertone
    "bg_base":        "#12091A",   # near-black with violet depth
    "bg_surface":     "#1E1028",   # deep plum — cards, frames, LabelFrames
    "bg_input":       "#2A1535",   # slightly lighter plum for entry fields

    # Accents — soft lavender-violet
    "accent_strong":  "#7040B8",   # darkened lavender-violet — ~6:1 contrast vs text_primary
    "accent_mid":     "#8F5ED0",   # mid lavender — hover states (was accent_strong)
    "accent_soft":    "#D8C0F0",   # pale lavender — LabelFrame titles, links
    "accent_glow":    "#4A2A78",   # deep violet — borders, separators

    # Text — warm soft white with lavender cast
    "text_primary":   "#EEE8F8",   # warm near-white with faint violet tint
    "text_secondary": "#B8A8D0",   # muted lavender-grey — captions, hints

    # Semantic — desaturated, palette-tinted variants
    "success":        "#6DFAA2",   # richer emerald-teal — Start button
    "danger":         "#D47A8F",   # dusty rose-red — warm, not alarm-red
    "warning":        "#D4A84B",   # warm amber-gold — softer than pure yellow
    "info":           "#4AE0E4",   # richer periwinkle-blue — Preview button
}

# Font constants — (family, size[, style])
FONT_FAMILY    = "Georgia"
FONT_TITLE     = (FONT_FAMILY, 22, "bold")
FONT_HEADING   = (FONT_FAMILY, 15, "bold")
FONT_BODY      = (FONT_FAMILY, 13)
FONT_BODY_BOLD = (FONT_FAMILY, 13, "bold")
FONT_SMALL     = (FONT_FAMILY, 13)
FONT_TINY      = (FONT_FAMILY, 12)
FONT_ENTRY     = (FONT_FAMILY, 12)
FONT_MONO      = ("Consolas", 12)


def _inject_asmrify_theme():
    from ttkbootstrap.themes.standard import STANDARD_THEMES
    p = PALETTE
    STANDARD_THEMES["asmrify"] = {
        "type": "dark",
        "colors": {
            "primary":   p["accent_strong"],
            "secondary": p["bg_surface"],
            "success":   p["success"],
            "info":      p["info"],
            "warning":   p["warning"],
            "danger":    p["danger"],
            "light":     p["bg_surface"],
            "dark":      p["bg_base"],
            "bg":        p["bg_base"],
            "fg":        p["text_primary"],
            "selectbg":  p["accent_strong"],
            "selectfg":  p["text_primary"],
            "border":    p["accent_glow"],
            "inputfg":   p["text_primary"],
            "inputbg":   p["bg_input"],
            "active":    p["accent_mid"],
        },
    }


def apply_theme(style, root=None):
    import tkinter.ttk as _stdlib_ttk
    p = PALETTE

    # Propagate bg_base to the root window and every widget that inherits from "."
    # This kills the superhero grey bleed-through on notebook panes, canvas areas, etc.
    if root is not None:
        root.configure(bg=p["bg_base"])

    style.configure(".",
                    background=p["bg_base"],
                    foreground=p["text_primary"],
                    bordercolor=p["accent_glow"],
                    darkcolor=p["bg_base"],
                    lightcolor=p["bg_surface"],
                    troughcolor=p["bg_base"],
                    selectbackground=p["accent_strong"],
                    selectforeground=p["text_primary"],
                    fieldbackground=p["bg_input"],
                    font=FONT_BODY,
                    borderwidth=1)

    # Apply LabelFrame styles to both ttkbootstrap and stdlib ttk engines so that
    # _tk_ttk.LabelFrame widgets also pick up the dark surface colours.
    for s in (style, _stdlib_ttk.Style()):
        s.configure("TLabelframe",       background=p["bg_surface"], bordercolor=p["accent_glow"])
        s.configure("TLabelframe.Label", background=p["bg_surface"], foreground=p["accent_soft"],
                    font=FONT_SMALL)

    style.configure("TFrame",              background=p["bg_base"])
    style.configure("Surface.TFrame",      background=p["bg_surface"])
    style.configure("ScrollInner.TFrame",  background=p["bg_base"])

    style.configure("TLabel",
                    background=p["bg_surface"],
                    foreground=p["text_primary"],
                    font=FONT_BODY)
    style.configure("secondary.TLabel",
                    foreground=p["text_secondary"],
                    font=FONT_SMALL,
                    background=p["bg_surface"])
    style.configure("primary.TLabel",  foreground=p["accent_soft"],    font=FONT_BODY,  background=p["bg_surface"])
    style.configure("success.TLabel",  foreground=p["success"],        font=FONT_BODY,  background=p["bg_surface"])
    style.configure("danger.TLabel",   foreground=p["danger"],         font=FONT_BODY,  background=p["bg_surface"])
    style.configure("warning.TLabel",  foreground=p["warning"],        font=FONT_BODY,  background=p["bg_surface"])
    style.configure("info.TLabel",     foreground=p["info"],           font=FONT_BODY,  background=p["bg_surface"])

    # Base button — regular weight (secondary/utility buttons)
    style.configure("TButton",
                    font=FONT_BODY,
                    background=p["bg_surface"],
                    foreground=p["text_primary"],
                    bordercolor=p["accent_glow"])
    # Action buttons — bold, high contrast fg on coloured bg
    style.configure("primary.TButton",
                    background=p["accent_strong"],
                    foreground=p["text_primary"],
                    bordercolor=p["accent_glow"],
                    font=FONT_BODY_BOLD)
    style.map("primary.TButton",
              background=[("active", p["accent_mid"]), ("pressed", p["accent_glow"])])
    # Folder-picker: primary colours, regular weight
    style.configure("Folder.TButton",
                    background=p["accent_strong"],
                    foreground=p["text_primary"],
                    bordercolor=p["accent_glow"],
                    font=FONT_BODY)
    style.map("Folder.TButton",
              background=[("active", p["accent_mid"]), ("pressed", p["accent_glow"])])
    style.configure("secondary.TButton",
                    background=p["bg_surface"],
                    foreground=p["text_secondary"],
                    bordercolor=p["accent_glow"],
                    font=FONT_BODY)
    style.configure("success.TButton",
                    background=p["success"], foreground="#0A1A12",
                    bordercolor=p["success"], font=FONT_BODY_BOLD)
    style.configure("danger.TButton",
                    background=p["danger"],  foreground="#1A0810",
                    bordercolor=p["danger"],  font=FONT_BODY_BOLD)
    style.configure("info.TButton",
                    background=p["info"],    foreground="#08101A",
                    bordercolor=p["info"],    font=FONT_BODY_BOLD)

    style.configure("TEntry",
                    fieldbackground=p["bg_input"],
                    foreground=p["text_primary"],
                    bordercolor=p["accent_glow"],
                    font=FONT_ENTRY)
    # Readonly entries (folder path display): darker bg, softer text — not glaring
    style.map("TEntry",
              fieldbackground=[("readonly", p["bg_surface"])],
              foreground=[("readonly", p["text_secondary"])],
              bordercolor=[("readonly", p["accent_glow"])])
    style.configure("TCombobox",
                    fieldbackground=p["bg_input"],
                    foreground=p["text_primary"],
                    background=p["bg_surface"],
                    arrowcolor=p["accent_soft"],
                    font=FONT_ENTRY)

    style.configure("TNotebook",     background=p["bg_base"], bordercolor=p["bg_base"], wraptabs=True)
    style.configure("TNotebook.Tab",
                    background=p["bg_surface"],
                    foreground=p["text_secondary"],
                    font=FONT_SMALL,
                    padding=(12, 5))
    style.map("TNotebook.Tab",
              background=[("selected", p["accent_strong"])],
              foreground=[("selected", p["text_primary"])])

    style.configure("TRadiobutton",
                    background=p["bg_surface"],
                    foreground=p["text_primary"],
                    font=FONT_BODY)
    style.configure("primary.TRadiobutton",
                    background=p["bg_surface"],
                    foreground=p["text_primary"],
                    font=FONT_BODY)

    style.configure("TCheckbutton",
                    background=p["bg_surface"],
                    foreground=p["text_primary"],
                    font=FONT_BODY)

    style.configure("TProgressbar",
                    background=p["accent_strong"],
                    troughcolor=p["bg_base"])
    style.configure("striped.Horizontal.TProgressbar",
                    background=p["accent_strong"],
                    troughcolor=p["bg_base"])

    style.configure("TSeparator", background=p["accent_glow"])


_inactive_scale_imgs = []   # module-level ref — keeps PIL images alive for Tk

def register_inactive_scale_style(root):
    """Create image-based 'Inactive.Horizontal.TScale' style with a grey knob/track.

    Must be called once after the root window and theme exist.  Safe to call
    multiple times — subsequent calls are no-ops.
    """
    import tkinter.ttk as _ttk
    s = _ttk.Style(master=root)
    if "Inactive.Horizontal.Scale.slider" in s.element_names():
        return

    from PIL import Image, ImageDraw, ImageTk
    KNOB_COLOR  = "#6A6078"   # desaturated grey-lavender — readable but clearly inactive
    TRACK_COLOR = "#3A2E44"   # muted plum — darker than knob, lighter than bg

    size = 16
    knob_raw = Image.new("RGBA", (100, 100))
    ImageDraw.Draw(knob_raw).ellipse((0, 0, 95, 95), fill=KNOB_COLOR)
    knob_img = ImageTk.PhotoImage(knob_raw.resize((size, size), Image.LANCZOS))

    track_raw = Image.new("RGBA", (40, 8), TRACK_COLOR)
    track_img = ImageTk.PhotoImage(track_raw)

    _inactive_scale_imgs.extend([knob_img, track_img])

    s.element_create("Inactive.Horizontal.Scale.slider", "image", knob_img)
    s.element_create("Inactive.Horizontal.Scale.track",  "image", track_img)
    s.layout("Inactive.Horizontal.TScale", [
        ("Inactive.Horizontal.Scale.focus", {
            "expand": "1", "sticky": "nswe",
            "children": [
                ("Inactive.Horizontal.Scale.track",  {"sticky": "we"}),
                ("Inactive.Horizontal.Scale.slider", {"side": "left", "sticky": ""}),
            ],
        })
    ])


from ttkbootstrap.tooltip import ToolTip as _ToolTip

class ToolTip(_ToolTip):
    def __init__(self, widget, text="", wraplength=500, **kw):
        super().__init__(widget, text=text, wraplength=wraplength, **kw)
