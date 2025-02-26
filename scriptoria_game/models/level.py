class Level:
    def __init__(self, name, description, goal, tutorial):
        self.name = name
        self.description = description
        self.goal = goal
        self.tutorial = tutorial
        self.completed = False
        
    def mark_completed(self):
        """Mark this level as completed"""
        self.completed = True
        
    def is_completed(self):
        """Check if this level is completed"""
        return self.completed