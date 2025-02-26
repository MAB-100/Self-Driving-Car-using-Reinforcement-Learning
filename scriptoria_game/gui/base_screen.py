import tkinter as tk
from constants import COLORS, FONT_TYPES

class BaseScreen:
    """Base class for all screens in the game"""
    def __init__(self, master, game_manager):
        self.master = master
        self.game_manager = game_manager
        self.frame = tk.Frame(master, bg=COLORS["bg"])
        
    def setup(self):
        """Set up the screen UI elements"""
        pass
        
    def show(self):
        """Show this screen"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
    def hide(self):
        """Hide this screen"""
        self.frame.pack_forget()
        
    def create_label(self, parent, text, font_type="normal", color="text", **kwargs):
        """Helper to create a standardized label"""
        return tk.Label(
            parent,
            text=text,
            font=tk.font.Font(family=FONT_TYPES[font_type][0], 
                             size=FONT_TYPES[font_type][1], 
                             weight=FONT_TYPES[font_type][2]),
            fg=COLORS[color],
            bg=COLORS["bg"],
            **kwargs
        )
        
    def create_button(self, parent, text, command, font_type="normal", **kwargs):
        """Helper to create a standardized button"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=tk.font.Font(family=FONT_TYPES[font_type][0], 
                             size=FONT_TYPES[font_type][1], 
                             weight=FONT_TYPES[font_type][2]),
            bg=COLORS["bg"],
            fg=COLORS["text"],
            **kwargs
        )