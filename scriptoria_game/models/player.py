from constants import Mode

class Player:
    def __init__(self):
        self.mode = Mode.NORMAL
        self.position = [0, 0]  # [y, x]
        self.score = 0
        self.spells_learned = []
        self.current_level = 0
        
    def reset_for_level(self, level_number):
        """Reset player state for a new level"""
        self.mode = Mode.NORMAL
        self.current_level = level_number