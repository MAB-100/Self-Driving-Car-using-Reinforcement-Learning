#!/usr/bin/env python3

import curses
import textwrap

################################################################################
# DATA STRUCTURES AND UTILITY FUNCTIONS
################################################################################

class Chapter:
    """
    Holds the text environment (a list of strings) and the condition for puzzle
    completion. Also tracks which "Arcane Spells" are introduced in this chapter.
    """
    def __init__(self, title, environment, puzzle_check, instructions):
        """
        :param title: String name of the chapter
        :param environment: List of strings (each string is one line of text)
        :param puzzle_check: A function(game) -> bool that returns True when puzzle is solved
        :param instructions: A short text or list of lines describing new commands/puzzles
        """
        self.title = title
        self.environment = environment  # list of strings
        self.puzzle_check = puzzle_check
        self.instructions = instructions


class Game:
    """
    Main game state: current chapter index, text buffer, player position, mode, etc.
    """
    def __init__(self, screen):
        self.screen = screen
        self.chapters = []
        self.current_chapter_index = 0

        # Player/cursor position in the text environment
        self.cursor_y = 0
        self.cursor_x = 0

        # Mode can be "MANIPULATE" or "CREATION"
        self.mode = "MANIPULATE"

        # For handling multi-key commands like 'dd' or 'dw'
        self.command_buffer = ""

        # For storing yanked text (lines).
        self.yank_buffer = []

        # For searching
        self.last_search = ""

    def current_chapter(self):
        return self.chapters[self.current_chapter_index]

    def environment(self):
        return self.current_chapter().environment

    def width(self):
        """Max line width in the current environment"""
        return max(len(line) for line in self.environment())

    def height(self):
        """Number of lines in the current environment"""
        return len(self.environment())

    def reset_cursor(self):
        """Reset cursor to top-left whenever a new chapter starts or puzzle resets."""
        self.cursor_y = 0
        self.cursor_x = 0
        self.mode = "MANIPULATE"
        self.command_buffer = ""


################################################################################
# PUZZLE CHECK FUNCTIONS
################################################################################

def puzzle_check_ch1(game):
    """
    Chapter 1 puzzle:
    The puzzle is solved if line #1 (0-based: the second line) contains the word 'FIXED'.
    """
    env = game.environment()
    if len(env) > 1 and "FIXED" in env[1]:
        return True
    return False

def puzzle_check_ch2(game):
    """
    Chapter 2 puzzle:
    Solved if line #1 ends with an exclamation mark ('!').
    """
    env = game.environment()
    if len(env) > 1 and env[1].endswith("!"):
        return True
    return False

def puzzle_check_ch3(game):
    """
    Chapter 3 puzzle:
    Solved if line #1 is the same as line #2 (meaning the user copied line #1 and pasted it
    into line #2).
    """
    env = game.environment()
    if len(env) > 2 and env[1] == env[2]:
        return True
    return False

def puzzle_check_ch4(game):
    """
    Chapter 4 puzzle:
    Solved if any line contains 'UNLOCKED' (i.e., user replaced 'KEYRUNE' with 'UNLOCKED').
    """
    env = game.environment()
    for line in env:
        if "UNLOCKED" in line:
            return True
    return False

def puzzle_check_ch5(game):
    """
    Chapter 5 puzzle:
    Solved if 'BAD' no longer appears in any line.
    """
    env = game.environment()
    for line in env:
        if "BAD" in line:
            return False
    return True

def puzzle_check_ch6(game):
    """
    Chapter 6 puzzle:
    Solved if no line starts with 'XX' (the user presumably used repeated edits or macros
    to remove those prefixes).
    """
    env = game.environment()
    for line in env:
        if line.startswith("XX"):
            return False
    return True

def puzzle_check_ch7(game):
    """
    Chapter 7 puzzle:
    Solved if at least one line contains 'CLEAN' (indicating the user replaced 'CORRUPT').
    """
    env = game.environment()
    for line in env:
        if "CLEAN" in line:
            return True
    return False


################################################################################
# INITIAL CHAPTER DATA
################################################################################

def get_chapters():
    """
    Returns a list of 7 Chapter objects, each with:
    - Title
    - Initial environment (list of strings)
    - A puzzle check function
    - Instructions or story text
    """
    ch1_env = [
        "Chapter 1: The Awakening",
        "There is a broken rune here: [???]",
        "Hint: Move the cursor to the bracket area and insert 'FIXED'."
    ]
    ch1_instructions = [
        "Welcome, Arcane Scribe!",
        "MOVEMENT: Use 'h' (left), 'j' (down), 'k' (up), 'l' (right).",
        "CREATION MODE: Press 'i' to begin inserting text at the cursor. Press ESC to exit Creation Mode.",
        "REMOVING CHARACTERS: Use 'x' in MANIPULATE mode to remove the character under the cursor.",
        "GOAL: Remove '[???]' by using 'x' (or simply overwrite in Creation Mode), and insert 'FIXED' on line 2."
    ]

    ch2_env = [
        "Chapter 2: The Paths of Creation",
        "This line needs an exclamation at the end",
        "Try appending or opening a new line. Also, 'x' can remove characters."
    ]
    ch2_instructions = [
        "NEW SPELLS: 'a' to append text after the cursor, 'o' to open a new empty line below.",
        "Press ESC to return to MANIPULATE mode after inserting text.",
        "Use 'x' to remove any unwanted characters.",
        "GOAL: Add '!' at the end of line 2."
    ]

    ch3_env = [
        "Chapter 3: Gathering & Placing",
        "Copy this line and place it below",
        "....................... (Paste target here)",
        "Remember: 'yy' yanks a line, 'p' pastes it, 'dd' removes a line."
    ]
    ch3_instructions = [
        "NEW SPELLS: 'yy' to yank an entire line, 'p' to paste below. 'dd' deletes an entire line.",
        "GOAL: Make line 2 match line 3 (copy line 2 and paste it into line 3)."
    ]

    ch4_env = [
        "Chapter 4: The Great Search",
        "We have lost the KEYRUNE in here. Must search '/KEYRUNE'",
        "Then go to next occurrence with 'n'. Replace KEYRUNE with UNLOCKED!"
    ]
    ch4_instructions = [
        "NEW SPELLS: '/keyword' to search, 'n' to jump to next match.",
        "GOAL: Find 'KEYRUNE' and change it to 'UNLOCKED'."
    ]

    ch5_env = [
        "Chapter 5: The Art of Subtle Precision",
        "This line has BAD words. Use dw or cw to remove or change them.",
        "More BAD text is here. Remove 'BAD' from all lines!"
    ]
    ch5_instructions = [
        "NEW SPELLS: 'dw' (delete word), 'cw' (change word). Also 'w'/'b' to move by words, '0'/'$' for line start/end.",
        "GOAL: Erase 'BAD' everywhere so it no longer appears in any line."
    ]

    ch6_env = [
        "Chapter 6: The Dance of Repetition",
        "XXThis line has a prefix XX to remove",
        "XXAll these lines start with XX. There's about XXfive of them below",
        "XXHello",
        "XXHello",
        "XXHello"
    ]
    ch6_instructions = [
        "Though macros aren't fully implemented here, you can repeatedly edit to remove 'XX'.",
        "GOAL: Ensure no line begins with 'XX'."
    ]

    ch7_env = [
        "Chapter 7: Master of Scriptoria",
        "One final corruption: CORRUPT text is hidden. Replace it with CLEAN globally if you wish.",
        "Puzzle is solved if at least one line has 'CLEAN' instead of 'CORRUPT'."
    ]
    ch7_instructions = [
        "FINAL CHALLENGE: Combine all your skills! Searching, insertion, deletion, etc.",
        "GOAL: Replace 'CORRUPT' with 'CLEAN' in at least one line."
    ]

    return [
        Chapter("Chapter 1", ch1_env, puzzle_check_ch1, ch1_instructions),
        Chapter("Chapter 2", ch2_env, puzzle_check_ch2, ch2_instructions),
        Chapter("Chapter 3", ch3_env, puzzle_check_ch3, ch3_instructions),
        Chapter("Chapter 4", ch4_env, puzzle_check_ch4, ch4_instructions),
        Chapter("Chapter 5", ch5_env, puzzle_check_ch5, ch5_instructions),
        Chapter("Chapter 6", ch6_env, puzzle_check_ch6, ch6_instructions),
        Chapter("Chapter 7", ch7_env, puzzle_check_ch7, ch7_instructions),
    ]


################################################################################
# MAIN GAME LOOP
################################################################################

def main(screen):
    curses.curs_set(1)  # Make the cursor visible
    screen.keypad(True)

    # Initialize the game state
    game = Game(screen)
    game.chapters = get_chapters()

    # Main game loop over chapters
    while game.current_chapter_index < len(game.chapters):
        game.reset_cursor()
        run_chapter(game)
        game.current_chapter_index += 1

        if game.current_chapter_index >= len(game.chapters):
            # All chapters done
            end_game_sequence(screen)
            break

    screen.clear()
    screen.addstr(0, 0, "Thanks for playing! You have completed the adventure.")
    screen.refresh()
    screen.getch()

def run_chapter(game):
    """
    Runs the main loop for a single chapter.
    """
    chapter = game.current_chapter()
    screen = game.screen

    # Show instructions briefly
    display_instructions(screen, chapter.title, chapter.instructions)
    screen.getch()  # Wait for any keypress to continue

    while True:
        # Render the environment
        screen.clear()
        display_environment(game)
        screen.refresh()

        # Check puzzle
        if chapter.puzzle_check(game):
            # Puzzle solved
            break

        # Get user input
        key = screen.getch()
        handle_key(game, key)

################################################################################
# INPUT HANDLING
################################################################################

def handle_key(game, key):
    """
    Interpret user input from curses in MANIPULATE mode or CREATION mode.
    We'll handle:
      - Movement (h,j,k,l)
      - Basic edits (x, dd, dw, cw, etc.)
      - Yanking/pasting (yy, p)
      - Searching (/keyword, n)
      - Insert/Append/Open new line (i, a, o)
    """
    # Convert curses key to a character if possible
    if 0 <= key <= 255:
        ch = chr(key)
    else:
        ch = ""  # special key like arrow, ignore in this context

    if game.mode == "CREATION":
        # If in creation mode, pressing ESC switches back to manipulate mode
        if key == 27:  # ESC
            game.mode = "MANIPULATE"
        else:
            # Insert typed character into current line
            insert_char(game, ch)
        return

    # If we're in MANIPULATE mode
    if ch in ['h','j','k','l','i','a','o','x','y','p','/','n','d','c','w','b','0','$']:
        game.command_buffer += ch
        interpret_command_buffer(game)
    elif key == 27:  # ESC in manipulate mode
        # Clear any partial commands
        game.command_buffer = ""
    else:
        # If it doesn't match recognized keys, flush the buffer
        game.command_buffer = ""

def interpret_command_buffer(game):
    """
    Parse the command buffer to handle multi-key incantations:
      - dd, dw, cw, yy, etc.
      - /pattern (search)
      - single-key commands h,j,k,l,x...
    We'll do a simplified approach:
      1. If command_buffer is length=1, it might be a single command.
      2. If length=2, see if it forms 'dd', 'dw', etc.
      3. If it's a search (/...) we wait for Enter.
    """
    cb = game.command_buffer

    # Single-key or partial
    if len(cb) == 1:
        c = cb[0]
        if c == 'h':
            move_left(game)
            game.command_buffer = ""
        elif c == 'j':
            move_down(game)
            game.command_buffer = ""
        elif c == 'k':
            move_up(game)
            game.command_buffer = ""
        elif c == 'l':
            move_right(game)
            game.command_buffer = ""
        elif c == 'i':
            game.mode = "CREATION"
            game.command_buffer = ""
        elif c == 'a':
            move_right(game)
            game.mode = "CREATION"
            game.command_buffer = ""
        elif c == 'o':
            open_new_line(game)
            game.command_buffer = ""
        elif c == 'x':
            delete_char_at_cursor(game)
            game.command_buffer = ""
        elif c == 'y':
            # Possibly 'yy', so wait for second 'y'
            pass
        elif c == 'p':
            paste_line_below(game)
            game.command_buffer = ""
        elif c == '/':
            # We'll gather the pattern until user presses Enter
            pass
        elif c == 'n':
            search_next(game)
            game.command_buffer = ""
        elif c in ['w','b','0','$']:
            move_word_or_line(game, c)
            game.command_buffer = ""
        else:
            # Possibly first half of a 2-char command like 'dd'
            pass

    elif len(cb) == 2:
        # Two-character commands
        first, second = cb[0], cb[1]
        if first == 'y' and second == 'y':
            yank_entire_line(game)
            game.command_buffer = ""
        elif first == 'd' and second == 'd':
            delete_entire_line(game)
            game.command_buffer = ""
        elif first == 'd' and second == 'w':
            delete_word(game)
            game.command_buffer = ""
        elif first == 'c' and second == 'w':
            change_word(game)
            game.command_buffer = ""
        else:
            # Possibly /pattern or other commands
            pass

    # If we have a search command (/...), handle that once the user hits Enter
    if cb.startswith('/'):
        # We watch for newline or carriage return to finalize the search pattern
        if cb.endswith('\n') or cb.endswith('\r'):
            pattern = cb[1:-1]  # skip leading '/', trailing newline
            perform_search(game, pattern)
            game.command_buffer = ""

    # If longer than 2 and not a search, just clear it
    if len(cb) > 2 and not cb.startswith('/'):
        game.command_buffer = ""


################################################################################
# COMMAND IMPLEMENTATIONS
################################################################################

def move_left(game):
    if game.cursor_x > 0:
        game.cursor_x -= 1

def move_right(game):
    line_length = len(game.environment()[game.cursor_y])
    if game.cursor_x < line_length:
        game.cursor_x += 1

def move_up(game):
    if game.cursor_y > 0:
        game.cursor_y -= 1
        # Clamp x if the new line is shorter
        new_len = len(game.environment()[game.cursor_y])
        if game.cursor_x > new_len:
            game.cursor_x = new_len

def move_down(game):
    if game.cursor_y < game.height() - 1:
        game.cursor_y += 1
        new_len = len(game.environment()[game.cursor_y])
        if game.cursor_x > new_len:
            game.cursor_x = new_len

def move_word_or_line(game, c):
    """Handle 'w', 'b', '0', '$' in a basic way."""
    lines = game.environment()
    y = game.cursor_y
    x = game.cursor_x
    line = lines[y]

    if c == 'w':
        # naive approach: jump to next space or end of line
        next_space = line.find(' ', x)
        if next_space == -1:
            game.cursor_x = len(line)
        else:
            game.cursor_x = min(next_space + 1, len(line))

    elif c == 'b':
        # jump backward to previous space
        reverse_segment = line[:x]
        last_space = reverse_segment.rfind(' ')
        if last_space == -1:
            game.cursor_x = 0
        else:
            game.cursor_x = last_space

    elif c == '0':
        game.cursor_x = 0

    elif c == '$':
        game.cursor_x = len(line)

def insert_char(game, ch):
    """Insert a typed character at cursor in Creation Mode."""
    y = game.cursor_y
    x = game.cursor_x
    lines = game.environment()

    if 0 <= y < len(lines):
        line = lines[y]
        new_line = line[:x] + ch + line[x:]
        lines[y] = new_line
        game.cursor_x += 1

def delete_char_at_cursor(game):
    y = game.cursor_y
    x = game.cursor_x
    lines = game.environment()
    if 0 <= y < len(lines):
        line = lines[y]
        if 0 <= x < len(line):
            new_line = line[:x] + line[x+1:]
            lines[y] = new_line
            # Cursor stays in the same place

def yank_entire_line(game):
    """yy -> yank entire current line"""
    y = game.cursor_y
    lines = game.environment()
    if 0 <= y < len(lines):
        game.yank_buffer = [lines[y]]

def paste_line_below(game):
    """p -> paste the yanked line(s) below the current line."""
    y = game.cursor_y
    lines = game.environment()
    if game.yank_buffer:
        for idx, text in enumerate(game.yank_buffer):
            lines.insert(y + 1 + idx, text)

def delete_entire_line(game):
    """dd -> delete the entire current line."""
    y = game.cursor_y
    lines = game.environment()
    if 0 <= y < len(lines):
        del lines[y]
        if y >= len(lines):
            game.cursor_y = len(lines) - 1
        game.cursor_x = 0

def delete_word(game):
    """dw -> remove the rest of the word from cursor to the next space or end of line."""
    y = game.cursor_y
    x = game.cursor_x
    lines = game.environment()
    if 0 <= y < len(lines):
        line = lines[y]
        next_space = line.find(' ', x)
        if next_space == -1:
            new_line = line[:x]
        else:
            new_line = line[:x] + line[next_space:]
        lines[y] = new_line

def change_word(game):
    """cw -> delete_word, then enter CREATION mode."""
    delete_word(game)
    game.mode = "CREATION"

def open_new_line(game):
    """o -> open a new line below the current line, move cursor there in creation mode."""
    y = game.cursor_y
    lines = game.environment()
    if 0 <= y < len(lines):
        lines.insert(y+1, "")
        game.cursor_y += 1
        game.cursor_x = 0
        game.mode = "CREATION"

def perform_search(game, pattern):
    """
    Store the pattern in game.last_search, then jump to the first occurrence if found.
    A naive forward search from (cursor_y, cursor_x).
    """
    game.last_search = pattern
    y_start = game.cursor_y
    x_start = game.cursor_x

    lines = game.environment()
    found_y, found_x = -1, -1
    for yy in range(y_start, len(lines)):
        line = lines[yy]
        start_idx = x_start if yy == y_start else 0
        idx = line.find(pattern, start_idx)
        if idx != -1:
            found_y, found_x = yy, idx
            break

    if found_y != -1:
        game.cursor_y = found_y
        game.cursor_x = found_x

def search_next(game):
    """
    n -> jump to next occurrence of game.last_search, continuing forward.
    """
    pattern = game.last_search
    if not pattern:
        return
    lines = game.environment()
    y_start = game.cursor_y
    x_start = game.cursor_x + 1  # move past current match

    found_y, found_x = -1, -1
    for yy in range(y_start, len(lines)):
        line = lines[yy]
        start_idx = x_start if yy == y_start else 0
        idx = line.find(pattern, start_idx)
        if idx != -1:
            found_y, found_x = yy, idx
            break

    if found_y != -1:
        game.cursor_y = found_y
        game.cursor_x = found_x


################################################################################
# DISPLAY FUNCTIONS
################################################################################

def display_environment(game):
    """
    Renders the current environment and places the cursor.
    """
    screen = game.screen
    lines = game.environment()

    # Show chapter title at top
    title_str = f"[{game.current_chapter().title}] Mode: {game.mode}"
    screen.addstr(0, 0, title_str, curses.A_BOLD)

    # Print environment lines starting at row 1
    for i, line in enumerate(lines):
        screen.addstr(i+1, 0, line)

    # Move the cursor to reflect game.cursor_y + 1 offset
    screen.move(game.cursor_y + 1, game.cursor_x)


def display_instructions(screen, title, instructions):
    """
    Displays instructions or story text for the chapter. Press any key to continue.
    """
    screen.clear()

    # Print chapter title
    screen.addstr(0, 0, f"== {title} ==", curses.A_BOLD)
    row = 2

    # Wrap instructions text so it fits nicely
    for line in instructions:
        wrapped_lines = textwrap.wrap(line, width=70)
        for wline in wrapped_lines:
            screen.addstr(row, 0, wline)
            row += 1
        row += 1  # blank line

    screen.addstr(row, 0, "[Press any key to begin...]")
    screen.refresh()

def end_game_sequence(screen):
    """
    Display a simple 'victory' message after the final chapter.
    """
    screen.clear()
    msg = [
        "Congratulations, you have cleansed the Realm of Scriptoria!",
        "All Arcane Editor Spells are now at your command.",
        "You are the Master Scribe!"
    ]
    row = 0
    for line in msg:
        screen.addstr(row, 0, line)
        row += 2
    screen.addstr(row, 0, "Press any key to exit.")
    screen.refresh()
    screen.getch()


################################################################################
# PROGRAM ENTRY POINT
################################################################################

def start_game():
    curses.wrapper(main)

if __name__ == "__main__":
    start_game()
