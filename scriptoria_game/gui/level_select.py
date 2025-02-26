import tkinter as tk
from gui.base_screen import BaseScreen

class LevelSelect(BaseScreen):
    def __init__(self, master, game_manager):
        super().__init__(master, game_manager)
        self.setup()
    
    def setup(self):
        # Create title
        title_label = self.create_label(
            self.frame, 
            text="SELECT LEVEL", 
            font_type="title", 
            color="title"
        )
        title_label.pack(pady=(40, 30))
        
        # Level buttons
        levels_frame = tk.Frame(self.frame, bg="black")
        levels_frame.pack(pady=10)
        
        # Get all levels
        levels = self.game_manager.level_manager.get_all_levels()
        
        for i, level in enumerate(levels):
            level_status = "✓ " if level.is_completed() else ""
            button_text = f"{level_status}Level {i+1}: {level.name}"
            
            # If previous level is completed or this is the first level
            is_enabled = i == 0 or levels[i-1].is_completed()
            
            button = self.create_button(
                levels_frame, 
                text=button_text, 
                command=lambda idx=i: self.game_manager.start_level(idx),
                font_type="normal",
                # bg="black",
                # fg="white" if is_enabled else "gray",
                width=40,
                state=tk.NORMAL if is_enabled else tk.DISABLED
            )
            button.pack(pady=5)
        
        # Back button
        back_button = self.create_button(
            self.frame, 
            text="Back to Main Menu", 
            command=self.game_manager.show_main_menu,
            font_type="normal"
        )
        back_button.pack(pady=20)