import tkinter as tk
from gui.base_screen import BaseScreen
from constants import FONT_TYPES, COLORS

class MainMenu(BaseScreen):
    def __init__(self, master, game_manager):
        super().__init__(master, game_manager)
        self.setup()
    
    def setup(self):
        # Create title
        title_label = self.create_label(
            self.frame, 
            text="SCRIPTORIA", 
            font_type="large_title", 
            color="title"
        )
        title_label.pack(pady=(80, 20))
        
        subtitle_label = self.create_label(
            self.frame,
            text="The Text Wizard's Journey", 
            font_type="menu",
            color="hint"
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Menu buttons
        play_button = self.create_button(
            self.frame, 
            text="Play Game", 
            command=self.game_manager.show_level_select,
            font_type="menu",
            width=20, bd=1
        )
        play_button.pack(pady=10)
        
        instructions_button = self.create_button(
            self.frame, 
            text="Instructions", 
            command=self.show_instructions,
            font_type="menu",
            width=20, bd=1
        )
        instructions_button.pack(pady=10)
        
        quit_button = self.create_button(
            self.frame, 
            text="Quit", 
            command=self.game_manager.quit_game,
            font_type="menu",
            width=20, bd=1
        )
        quit_button.pack(pady=10)
    
    def show_instructions(self):
        """Show game instructions"""
        from tkinter import messagebox
        messagebox.showinfo("Instructions", 
                           "Welcome to Scriptoria, young wizard!\n\n" +
                           "In this mysterious world, you'll learn powerful text manipulation magic.\n\n" +
                           "Basic Controls:\n" +
                           "- Movement: h (left), j (down), k (up), l (right)\n" +
                           "- Mode switching: i (insert mode), v (visual mode), ESC (normal mode)\n" +
                           "- Special abilities: x (delete), w (word forward), b (word backward)\n\n" +
                           "Follow the instructions in each level to master the mystical arts of text manipulation!")