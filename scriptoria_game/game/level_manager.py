from models.level import Level

class LevelManager:
    def __init__(self):
        self.levels = []
        self.setup_levels()
        
    def setup_levels(self):
        """Initialize all game levels"""
        self.levels = [
            Level("The Path Begins", 
                  "Welcome to Scriptoria, young apprentice. Learn to navigate the text realm.",
                  "Move to the glowing portal (O) using h, j, k, l keys",
                  "Press h for left, j for down, k for up, l for right"),
            
            Level("The Dual States", 
                  "A text wizard must know when to observe and when to create.",
                  "Press 'i' to enter insert mode, type the magic word 'wizard', then press ESC",
                  "i enters creation mode, ESC returns to movement mode"),
            
            Level("The Deletion Arts",
                  "Sometimes removing text is as powerful as creating it.",
                  "Delete the evil runes (X) using 'x' in normal mode",
                  "Move to a rune, press 'x' to remove it"),
            
            Level("The Word Traveler",
                  "A skilled text wizard can leap across words with a single command.",
                  "Jump to the end of each word using 'w' and reach the portal",
                  "Press 'w' to jump to the start of the next word"),
            
            Level("Backward Motion",
                  "Moving backward is just as important as moving forward.",
                  "Use 'b' to jump backward to previous words and collect all gems",
                  "Press 'b' to jump to the start of the previous word")
        ]
    
    def get_level(self, index):
        """Get a level by index"""
        if 0 <= index < len(self.levels):
            return self.levels[index]
        return None
        
    def get_all_levels(self):
        """Get all levels"""
        return self.levels
        
    def create_map(self, level_num):
        """Create a map for the specified level number"""
        game_map = []
        player_position = [0, 0]
        
        if level_num == 0:  # First level - movement
            game_map = [
                list("##############################"),
                list("#                            #"),
                list("#  P                         #"),
                list("#                            #"),
                list("#                            #"),
                list("#                          O #"),
                list("#                            #"),
                list("##############################")
            ]
            player_position = [2, 3]  # P position
        elif level_num == 1:  # Second level - modes
            game_map = [
                list("##############################"),
                list("#                            #"),
                list("#  P                         #"),
                list("#                            #"),
                list("#  [Type 'wizard' here]      #"),
                list("#                            #"),
                list("#                            #"),
                list("##############################")
            ]
            player_position = [2, 3]
        elif level_num == 2:  # Third level - deletion
            game_map = [
                list("##############################"),
                list("#                            #"),
                list("#  P     X     X     X       #"),
                list("#                            #"),
                list("#    X     X     X     X     #"),
                list("#                          O #"),
                list("#                            #"),
                list("##############################")
            ]
            player_position = [2, 3]
        elif level_num == 3:  # Word movement
            game_map = [
                list("##############################"),
                list("#                            #"),
                list("#  P  word1  word2  word3    #"),
                list("#                            #"),
                list("#    word4  word5  word6   O #"),
                list("#                            #"),
                list("#                            #"),
                list("##############################")
            ]
            player_position = [2, 3]
        elif level_num == 4:  # Backward movement
            game_map = [
                list("##############################"),
                list("#                            #"),
                list("#             P              #"),
                list("#                            #"),
                list("#  gem1  gem2  gem3  gem4    #"),
                list("#                          O #"),
                list("#                            #"),
                list("##############################")
            ]
            player_position = [2, 13]
            
        # Create a deep copy of the map without player to preserve elements
        original_map = []
        for row in game_map:
            new_row = []
            for cell in row:
                if cell == 'P':
                    new_row.append(' ')  # Don't include player in original map
                else:
                    new_row.append(cell)
            original_map.append(new_row)
            
        return game_map, original_map, player_position