from enum import Enum

class Mode(Enum):
    NORMAL = 1
    INSERT = 2
    VISUAL = 3

class GameState(Enum):
    MAIN_MENU = 1
    LEVEL_SELECT = 2
    PLAYING = 3
    PAUSED = 4
    COMPLETED = 5

# Color definitions
COLORS = {
    "bg": "black",
    "text": "white",
    "player": "#00FF00",
    "portal": "#0088FF",
    "rune": "#FF0000",
    "wall": "#444444",
    "word": "#FFCC00",
    "gem": "#FF00FF",
    "title": "green",
    "hint": "cyan",
    "mode": "yellow",
}

# Font configurations
FONT_TYPES = {
    "title": ("Courier", 16, "bold"),
    "normal": ("Courier", 12, "normal"),
    "map": ("Courier", 14, "bold"),
    "menu": ("Courier", 18, "bold"),
    "large_title": ("Courier", 28, "bold"),
}
