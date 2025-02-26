import tkinter as tk
from gui.base_screen import BaseScreen
from constants import COLORS, Mode

class GameScreen(BaseScreen):
    def __init__(self, master, game_manager):
        super().__init__(master, game_manager)
        self.messages = []
        self.setup()
    
    def setup(self):
        # Level info frame
        self.info_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        self.info_frame.pack(pady=10, fill=tk.X)
        
        self.level_title = self.create_label(self.info_frame, text="", font_type="title", color="title")
        self.level_title.pack(anchor=tk.W, padx=10)
        
        self.level_desc = self.create_label(self.info_frame, text="", font_type="normal", color="text")
        self.level_desc.pack(anchor=tk.W, padx=10)
        
        self.level_goal = self.create_label(self.info_frame, text="", font_type="normal", color="text")
        self.level_goal.pack(anchor=tk.W, padx=10)
        
        # Game map canvas
        self.canvas = tk.Canvas(self.frame, bg=COLORS["bg"], highlightthickness=0)
        self.canvas.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
        
        # Mode and messages frame
        self.status_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        self.status_frame.pack(pady=5, fill=tk.X)
        
        self.mode_label = self.create_label(self.status_frame, text="", font_type="normal", color="mode")
        self.mode_label.pack(anchor=tk.W, padx=10)
        
        # Message area
        self.message_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        self.message_frame.pack(pady=5, fill=tk.X)
        
        self.message_area = tk.Text(
            self.message_frame, 
            height=3, 
            font=tk.font.Font(
                family="Courier", 
                size=12
            ),
            bg=COLORS["bg"], 
            fg=COLORS["text"],
            wrap=tk.WORD, 
            state=tk.DISABLED
        )
        self.message_area.pack(padx=10, fill=tk.X)
        
        # Tutorial hint
        self.hint_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        self.hint_frame.pack(pady=5, fill=tk.X, side=tk.BOTTOM)
        
        self.tutorial_label = self.create_label(self.hint_frame, text="", font_type="normal", color="hint")
        self.tutorial_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Back to menu button
        self.menu_button = self.create_button(
            self.frame, 
            text="Main Menu (ESC)", 
            command=self.game_manager.show_main_menu, 
            font_type="normal"
        )
        self.menu_button.pack(pady=5, side=tk.BOTTOM)
    
    def update_display(self, player, current_level, game_map, original_map):
        """Update the display with current game state"""
        level = self.game_manager.level_manager.get_level(current_level)
        mode_help = self.game_manager.game_logic.mode_help
        
        # Update level info
        self.level_title.config(text=f"Level: {level.name}")
        self.level_desc.config(text=level.description)
        self.level_goal.config(text=f"Goal: {level.goal}")
        
        # Update mode info
        self.mode_label.config(text=f"Mode: {player.mode.name} - {mode_help[player.mode]}")
        
        # Update tutorial hint
        self.tutorial_label.config(text=f"Hint: {level.tutorial}")
        
        # Update messages
        self.message_area.config(state=tk.NORMAL)
        self.message_area.delete(1.0, tk.END)
        for msg in self.messages[-3:]:
            self.message_area.insert(tk.END, msg + "\n")
        self.message_area.config(state=tk.DISABLED)
        
        # Update game map
        self.canvas.delete("all")
        cell_width = 20
        cell_height = 20
        
        # Draw the map
        for y, row in enumerate(game_map):
            for x, cell in enumerate(row):
                # Set color based on cell content
                if cell == '#':
                    color = COLORS["wall"]
                elif cell == 'P':
                    color = COLORS["player"]
                elif cell == 'O':
                    color = COLORS["portal"]
                elif cell == 'X':
                    color = COLORS["rune"]
                elif cell.isalpha() and original_map[y][x].isalpha():
                    # Special colored text for words
                    color = COLORS["word"]
                elif cell.isalpha() and "gem" in ''.join(original_map[y][x-3:x+1]):
                    # Special color for gems
                    color = COLORS["gem"]
                elif cell == ' ':
                    color = COLORS["bg"]
                else:
                    color = COLORS["text"]
                
                # Draw cell
                if cell != ' ':
                    x1 = x * cell_width
                    y1 = y * cell_height
                    x2 = x1 + cell_width
                    y2 = y1 + cell_height
                    
                    # For walls, draw rectangles
                    if cell == '#':
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                    else:
                        # For other cells, draw text
                        self.canvas.create_text(
                            x1 + cell_width/2, 
                            y1 + cell_height/2, 
                            text=cell, 
                            fill=color, 
                            font=tk.font.Font(
                                family="Courier", 
                                size=14, 
                                weight="bold"
                            )
                        )
    
    def add_message(self, message):
        """Add a message to the display"""
        if message:
            self.messages.append(message)