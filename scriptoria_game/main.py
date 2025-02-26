# FILE: main.py
import tkinter as tk
import tkinter.font
from constants import GameState, Mode
from models.player import Player
from game.level_manager import LevelManager
from game.game_logic import GameLogic
from gui.main_menu import MainMenu
from gui.level_select import LevelSelect
from gui.game_screen import GameScreen

class GameManager:
    def __init__(self, root):
        self.root = root
        self.game_state = GameState.MAIN_MENU
        
        # Configure window
        self.root.title("Scriptoria: The Text Wizard's Journey")
        self.root.geometry("800x600")
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        
        # Initialize game components
        self.level_manager = LevelManager()
        self.game_logic = GameLogic(self.level_manager)
        self.player = Player()
        
        # Initialize screens
        self.main_menu = MainMenu(self.root, self)
        self.level_select = LevelSelect(self.root, self)
        self.game_screen = GameScreen(self.root, self)
        
        # Game map data
        self.game_map = []
        self.original_map = []
        
        # Show main menu
        self.show_main_menu()
        
        # Set up key bindings
        self.root.bind('<Key>', self.handle_keypress)
        self.root.bind('<Escape>', self.handle_escape)
        
    def show_main_menu(self):
        """Show the main menu screen"""
        self.game_state = GameState.MAIN_MENU
        
        # Hide all screens
        self.level_select.hide()
        self.game_screen.hide()
        
        # Show main menu
        self.main_menu.show()
        
    def show_level_select(self):
        """Show the level select screen"""
        self.game_state = GameState.LEVEL_SELECT
        
        # Hide all screens
        self.main_menu.hide()
        self.game_screen.hide()
        
        # Show level select
        self.level_select.show()
        
    def start_level(self, level_index):
        """Start a specific level"""
        self.game_state = GameState.PLAYING
        
        # Hide all screens
        self.main_menu.hide()
        self.level_select.hide()
        
        # Reset player for new level
        self.player.reset_for_level(level_index)
        
        # Create game map
        self.game_map, self.original_map, player_position = self.level_manager.create_map(level_index)
        self.player.position = player_position
        
        # Show game screen
        self.game_screen.show()
        
        # Clear messages and add welcome message
        self.game_screen.messages = []
        self.game_screen.add_message(f"Starting level {level_index + 1}: {self.level_manager.get_level(level_index).name}")
        self.game_screen.add_message("Press 'p' to pause the game")
        
        # Update the display
        self.game_screen.update_display(self.player, self.player.current_level, self.game_map, self.original_map)
        
        # Focus for keyboard input
        self.game_screen.canvas.focus_set()
    
    def handle_keypress(self, event):
        """Handle keyboard input based on game state"""
        key = event.char
        
        # Main menu controls
        if self.game_state == GameState.MAIN_MENU:
            if key == 'p' or key == 'P':
                self.show_level_select()
            elif key == 'q' or key == 'Q':
                self.quit_game()
                
        # Level select controls
        elif self.game_state == GameState.LEVEL_SELECT:
            # Numbers 1-9 to select levels
            if key.isdigit() and 1 <= int(key) <= len(self.level_manager.get_all_levels()):
                level_idx = int(key) - 1
                if level_idx == 0 or self.level_manager.get_level(level_idx-1).is_completed():
                    self.start_level(level_idx)
                    
        # Game playing controls
        elif self.game_state == GameState.PLAYING:
            self.handle_game_input(key)
                
    def handle_escape(self, event):
        """Handle the Escape key separately"""
        if self.game_state == GameState.PLAYING:
            # Check if we need to exit insert mode first
            if self.player.mode == Mode.INSERT:
                self.player.mode = Mode.NORMAL
                self.game_screen.add_message("Switched to normal mode")
                
                # For level 1, check if "wizard" was typed when exiting insert mode
                if self.player.current_level == 1:
                    map_text = self.game_map[4]
                    typed_text = ''.join(map_text[3:9])
                    if typed_text == "wizard":
                        self.game_screen.add_message("You typed the magic word!")
                        self.complete_level()
                
                self.game_screen.update_display(self.player, self.player.current_level, self.game_map, self.original_map)
            else:
                # Show pause menu or return to main menu
                self.show_main_menu()
        elif self.game_state == GameState.LEVEL_SELECT:
            self.show_main_menu()
    
    def handle_game_input(self, key):
        """Process input during gameplay"""
        current_level = self.player.current_level
        level_completed = False
        message = None
        
        # Mode switching
        if self.player.mode == Mode.NORMAL and key == 'i':
            self.player.mode = Mode.INSERT
            message = "Switched to insert mode"
        elif self.player.mode == Mode.NORMAL and key == 'v':
            self.player.mode = Mode.VISUAL
            message = "Switched to visual mode"
        else:
            # Handle input based on current mode
            if self.player.mode == Mode.NORMAL:
                self.game_map, self.original_map, self.player.position, level_completed, mode_message = \
                    self.game_logic.handle_normal_mode(key, self.game_map, self.original_map, 
                                                      self.player.position, self.player.current_level)
                if mode_message:
                    message = mode_message
                    
            elif self.player.mode == Mode.INSERT:
                self.game_map, self.original_map, self.player.position, level_completed, mode_message = \
                    self.game_logic.handle_insert_mode(key, self.game_map, self.original_map, 
                                                     self.player.position, self.player.current_level)
                if mode_message:
                    message = mode_message
                    
            elif self.player.mode == Mode.VISUAL:
                self.game_map, self.original_map, self.player.position, mode_message = \
                    self.game_logic.handle_visual_mode(key, self.game_map, self.original_map, 
                                                     self.player.position)
                if mode_message:
                    message = mode_message
            
            # Handle game pause
            if key == 'p' or key == 'P':
                message = "Game paused"
                self.game_state = GameState.PAUSED
                self.show_main_menu()
                
        # Add message if there is one
        if message:
            self.game_screen.add_message(message)
            
        # Update display
        self.game_screen.update_display(self.player, self.player.current_level, self.game_map, self.original_map)
        
        # Check if level is completed
        if level_completed:
            self.complete_level()
    
    def complete_level(self):
        """Handle level completion"""
        current_level = self.player.current_level
        
        # Mark level as completed
        level = self.level_manager.get_level(current_level)
        level.mark_completed()
        
        # Update score
        self.player.score += 100
        
        # Show completion message
        self.game_screen.add_message(f"Level {current_level + 1} completed! +100 points")
        
        # Check if there are more levels
        if current_level + 1 < len(self.level_manager.get_all_levels()):
            # Ask if player wants to continue to next level
            self.game_screen.add_message("Press 'n' for next level or 'm' for menu")
            
            # Set up special key binding for next level
            def next_level_handler(event):
                if event.char == 'n':
                    self.start_level(current_level + 1)
                elif event.char == 'm':
                    self.show_level_select()
                self.root.unbind('<Key>', next_level_id)
                
            next_level_id = self.root.bind('<Key>', next_level_handler)
        else:
            # Game completed
            self.game_state = GameState.COMPLETED
            self.game_screen.add_message("Congratulations! You've completed all levels!")
            self.game_screen.add_message("Press any key to return to menu")
            
            # Bind any key to return to menu
            def back_to_menu(event):
                self.show_main_menu()
                self.root.unbind('<Key>', back_id)
                
            back_id = self.root.bind('<Key>', back_to_menu)
    
    def quit_game(self):
        """Exit the game"""
        self.root.quit()

def main():
    """Main entry point for the game"""
    root = tk.Tk()
    game = GameManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()