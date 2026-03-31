from pathlib import Path

_ROOT = Path(__file__).parent.parent  # project root


class Images:
    ICON        = str(_ROOT / "assets" / "images" / "icon.png")
    FRONT_LOGIN = str(_ROOT / "assets" / "images" / "front_login.jpg")
    COMP_BG     = str(_ROOT / "assets" / "images" / "comp_bg.png")
    ADD         = str(_ROOT / "assets" / "images" / "add.png")
    BG_FG       = str(_ROOT / "assets" / "images" / "bg_fg.png")
    DASHBOARD   = str(_ROOT / "assets" / "images" / "dashboard.png")


class Models:
    MASK_DETECTOR = str(_ROOT / "assets" / "models" / "face_mask.pt")
