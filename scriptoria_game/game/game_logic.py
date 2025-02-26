from constants import Mode

class GameLogic:
    def __init__(self, level_manager):
        self.level_manager = level_manager
        self.mode_help = {
            Mode.NORMAL: "Movement mode: h(←) j(↓) k(↑) l(→)",
            Mode.INSERT: "Text creation mode: type to create text, ESC to exit",
            Mode.VISUAL: "Selection mode: move to select, y to copy, d to remove"
        }
    
    def handle_normal_mode(self, key, game_map, original_map, player_position, current_level):
        """Handle input in normal mode"""
        y, x = player_position
        old_y, old_x = y, x
        level_completed = False
        message = None
        
        # Movement (Vim-like)
        if key == 'h':  # left
            x = max(0, x - 1)
        elif key == 'j':  # down
            y = min(len(game_map) - 1, y + 1)
        elif key == 'k':  # up
            y = max(0, y - 1)
        elif key == 'l':  # right
            x = min(len(game_map[0]) - 1, x + 1)
        elif key == 'x':  # Delete character
            if game_map[y][x] == 'X':
                game_map[y][x] = ' '
                original_map[y][x] = ' '  # Also update original map
                message = "You removed a rune!"
                
                # Check if level is complete (no more X)
                if current_level == 2 and not any('X' in row for row in game_map):
                    level_completed = True
        elif key == 'w':  # Word movement (forward)
            # Implement word movement - jump to next word
            if current_level >= 3:  # Only active in level 4+
                found = False
                # Look ahead for the next word
                for test_x in range(x + 1, len(game_map[y])):
                    if game_map[y][test_x].isalpha() and (test_x == 0 or not game_map[y][test_x-1].isalpha()):
                        x = test_x
                        found = True
                        break
                
                if not found:
                    # Try the next line
                    for test_y in range(y + 1, len(game_map)):
                        for test_x in range(len(game_map[test_y])):
                            if game_map[test_y][test_x].isalpha() and (test_x == 0 or not game_map[test_y][test_x-1].isalpha()):
                                y = test_y
                                x = test_x
                                found = True
                                break
                        if found:
                            break
        elif key == 'b':  # Word movement (backward)
            # Implement backward word movement
            if current_level >= 4:  # Only active in level 5+
                found = False
                # Look backward for the previous word
                for test_x in range(x - 1, -1, -1):
                    if game_map[y][test_x].isalpha() and (test_x == len(game_map[y])-1 or not game_map[y][test_x+1].isalpha()):
                        x = test_x
                        found = True
                        break
                
                if not found:
                    # Try the previous line
                    for test_y in range(y - 1, -1, -1):
                        for test_x in range(len(game_map[test_y])-1, -1, -1):
                            if game_map[test_y][test_x].isalpha() and (test_x == len(game_map[test_y])-1 or not game_map[test_y][test_x+1].isalpha()):
                                y = test_y
                                x = test_x
                                found = True
                                break
                        if found:
                            break
        
        # Check if movement is valid
        if game_map[y][x] != '#':  # Not a wall
            # Check for special tiles
            if game_map[y][x] == 'O':  # Portal/goal
                level_completed = True
                
            # Update position and map
            # First, restore the original cell at old position
            game_map[old_y][old_x] = original_map[old_y][old_x]
            
            # Store what's currently at the new position (for restoration later)
            current_cell = game_map[y][x]
            
            # Place player at new position
            game_map[y][x] = 'P'
            player_position[0] = y
            player_position[1] = x
        
        return game_map, original_map, player_position, level_completed, message
    
    def handle_insert_mode(self, key, game_map, original_map, player_position, current_level):
        """Handle input in insert mode"""
        y, x = player_position
        level_completed = False
        message = None
        
        # Place character at cursor position if printable
        if 32 <= ord(key) <= 126:
            game_map[y][x] = key
            original_map[y][x] = key  # Update original map too
            
            # Move cursor right
            if x < len(game_map[0]) - 2:
                x += 1
                # Restore original content at new position before moving player
                current_cell = original_map[y][x]
                player_position[0] = y
                player_position[1] = x
                game_map[y][x] = 'P'
        
        # For level 1, check if "wizard" was typed (called only after ESC in the UI)
        if current_level == 1:
            map_text = game_map[4]
            typed_text = ''.join(map_text[3:9])
            if typed_text == "wizard":
                message = "You typed the magic word!"
                level_completed = True
                
        return game_map, original_map, player_position, level_completed, message
    
    def handle_visual_mode(self, key, game_map, original_map, player_position):
        """Handle input in visual mode"""
        message = None
        
        # Simple visual mode implementation
        if key == 'y':
            message = "Text copied! (Visual mode demonstration)"
        elif key == 'd':
            message = "Text deleted! (Visual mode demonstration)"
            
        return game_map, original_map, player_position, message