import pygame
import math
import random
import sys
import time

# Initialize Pygame with error handling
try:
    pygame.init()
except pygame.error as e:
    print(f"Failed to initialize pygame: {e}")
    sys.exit(1)

# Screen setup
WIDTH, HEIGHT = 1200, 800
try:
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hangman Game!")
except pygame.error as e:
    print(f"Failed to set up display: {e}")
    sys.exit(1)

# Game constants
RADIUS = 20
GAP = 15
MAX_ATTEMPTS = 6

class GameState:
    def __init__(self):
        self.letters = []
        self.word = ""
        self.hint = ""
        self.hangman_status = 0
        self.guessed = []
        self.hint_used = False
        self.generate_letters()
        
    def generate_letters(self):
        """Generate letter buttons for the keyboard."""
        self.letters = []
        start_x = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)
        start_y = 600
        for i in range(26):
            x = start_x + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))
            y = start_y + ((i // 13) * (GAP + RADIUS * 2))
            self.letters.append([x, y, chr(65 + i), True])

    def reset(self, difficulty):
        """Reset game state for a new round."""
        self.hangman_status = 0
        self.guessed = []
        self.hint_used = False
        self.generate_letters()
        word_options = WORD_LISTS.get(difficulty, [])
        if not word_options:
            print(f"No words found for difficulty: {difficulty}")
            word_options = WORD_LISTS["EASY"]  # Fallback to easy
        self.word, self.hint = random.choice(word_options)

# Font setup with fallbacks
try:
    LETTER_FONT = pygame.font.SysFont('comicsans', 30)
    WORD_FONT = pygame.font.SysFont('comicsans', 50)
    TITLE_FONT = pygame.font.SysFont('comicsans', 60)
    BUTTON_FONT = pygame.font.SysFont('comicsans', 25)
except pygame.error as e:
    print(f"Font loading error: {e}")
    # Fallback to default fonts
    LETTER_FONT = pygame.font.Font(None, 30)
    WORD_FONT = pygame.font.Font(None, 50)
    TITLE_FONT = pygame.font.Font(None, 60)
    BUTTON_FONT = pygame.font.Font(None, 25)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 128, 0)

# Complete word lists with all difficulties
WORD_LISTS = {
    "EASY": [("CAT", "A small domesticated feline"),
             ("DOG", "Man's best friend"),
             ("SUN", "Provides light and heat"),
             ("CAR", "A common vehicle"),
             ("BALL", "Used in many sports"),
             ("HAT", "Worn on the head"),
             ("FISH", "Swims in water"),
             ("CAKE", "Sweet dessert"),
             ("BOOK", "Contains pages to read"),
             ("TREE", "Has leaves and branches")],
    
    "NORMAL": [("PYTHON", "Popular programming language"),
               ("REPLIT", "Online coding platform"),
               ("SPEAKER", "Amplifies sound"),
               ("HANGMAN", "Name of this game"),
               ("PYGAME", "Python library for games"),
               ("WINDOW", "Glass pane in a wall"),
               ("BOTTLE", "Holds liquids"),
               ("GARDEN", "Where plants grow"),
               ("PENCIL", "Writing instrument"),
               ("ROCKET", "Space vehicle")],
    
    "HARD": [("COMPLEXITY", "Measure of computational difficulty"),
             ("JAVASCRIPT", "Web programming language"),
             ("ALGORITHM", "Step-by-step procedure"),
             ("DEVELOPER", "Writes code"),
             ("FRAMEWORK", "Software structure"),
             ("QUINTESSENCE", "Purest essence of something"),
             ("KALEIDOSCOPE", "Optical instrument with patterns"),
             ("XENOPHOBIA", "Fear of foreigners"),
             ("ZYGOMORPHIC", "Bilaterally symmetrical"),
             ("QUIZMASTER", "Host of a quiz game")],
    
    "EXTREME": [("LEBRONJAMES", "Basketball legend"),
                ("INTELLIGENCE", "Acquiring knowledge"),
                ("STEVEJOBS", "Apple co-founder"),
                ("DEVELOPER", "Creates software"),
                ("QUINTILLION", "A very large number"),
                ("ANTIDISESTABLISHMENTARIANISM", "Opposition to church-state connection"),
                ("PNEUMONOULTRAMICROSCOPICSILICOVOLCANOCONIOSIS", "A lung disease"),
                ("SUPERCALIFRAGILISTICEXPIALIDOCIOUS", "Extraordinarily good"),
                ("PSEUDOPSEUDOHYPOPARATHYROIDISM", "Inherited disorder"),
                ("FLOCCINAUCINIHILIPILIFICATION", "Estimating something as worthless")]
}

def draw_hangman(status):
    """Draw the hangman figure based on current status."""
    base_x, base_y = 150, 150
    # Gallows
    pygame.draw.line(win, BLACK, (base_x-50, base_y+300), (base_x+150, base_y+300), 5)
    pygame.draw.line(win, BLACK, (base_x+50, base_y+300), (base_x+50, base_y), 5)
    pygame.draw.line(win, BLACK, (base_x+50, base_y), (base_x+200, base_y), 5)
    pygame.draw.line(win, BLACK, (base_x+200, base_y), (base_x+200, base_y+50), 5)
    
    if status >= 1:  # Head
        pygame.draw.circle(win, BLACK, (base_x+200, base_y+80), 30, 3)
    if status >= 2:  # Body
        pygame.draw.line(win, BLACK, (base_x+200, base_y+110), (base_x+200, base_y+250), 3)
    if status >= 3:  # Left arm
        pygame.draw.line(win, BLACK, (base_x+200, base_y+130), (base_x+150, base_y+180), 3)
    if status >= 4:  # Right arm
        pygame.draw.line(win, BLACK, (base_x+200, base_y+130), (base_x+250, base_y+180), 3)
    if status >= 5:  # Left leg
        pygame.draw.line(win, BLACK, (base_x+200, base_y+250), (base_x+150, base_y+300), 3)
    if status >= 6:  # Right leg
        pygame.draw.line(win, BLACK, (base_x+200, base_y+250), (base_x+250, base_y+300), 3)

def select_difficulty():
    """Show difficulty selection screen and return chosen level."""
    while True:
        win.fill(WHITE)
        text = TITLE_FONT.render("Select Difficulty", True, BLACK)
        win.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))
        
        buttons = {
            "EASY": pygame.Rect(WIDTH // 2 - 100, 200, 200, 50),
            "NORMAL": pygame.Rect(WIDTH // 2 - 100, 270, 200, 50),
            "HARD": pygame.Rect(WIDTH // 2 - 100, 340, 200, 50),
            "EXTREME": pygame.Rect(WIDTH // 2 - 100, 410, 200, 50)
        }
        
        for level, rect in buttons.items():
            color = LIGHT_BLUE if rect.collidepoint(pygame.mouse.get_pos()) else WHITE
            pygame.draw.rect(win, color, rect, border_radius=10)
            pygame.draw.rect(win, BLACK, rect, 2, border_radius=10)
            text = BUTTON_FONT.render(level.capitalize(), True, BLACK)
            win.blit(text, (rect.centerx - text.get_width() // 2, 
                           rect.centery - text.get_height() // 2))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for level, rect in buttons.items():
                    if rect.collidepoint(mouse_pos):
                        return level

def draw_game(state):
    """Draw all game elements on the screen."""
    win.fill(WHITE)
    
    # Draw title
    text = TITLE_FONT.render("HANGMAN", True, BLACK)
    win.blit(text, (WIDTH//2 - text.get_width()//2, 20))
    
    # Draw word display with wrapping for long words
    display_word = " ".join([letter if letter in state.guessed else "_" for letter in state.word])
    
    # Split into multiple lines if needed
    max_line_width = WIDTH - 200
    word_surface = WORD_FONT.render(display_word, True, BLACK)
    
    if word_surface.get_width() > max_line_width:
        # Split into two lines
        words = display_word.split()
        line1 = " ".join(words[:len(words)//2])
        line2 = " ".join(words[len(words)//2:])
        
        text1 = WORD_FONT.render(line1, True, BLACK)
        text2 = WORD_FONT.render(line2, True, BLACK)
        
        win.blit(text1, (WIDTH//2 - text1.get_width()//2, 400))
        win.blit(text2, (WIDTH//2 - text2.get_width()//2, 460))
    else:
        win.blit(word_surface, (WIDTH//2 - word_surface.get_width()//2, 450))
    
    # Draw hint button
    hint_button = pygame.Rect(WIDTH - 150, 20, 120, 40)
    pygame.draw.rect(win, LIGHT_BLUE, hint_button, border_radius=5)
    pygame.draw.rect(win, BLACK, hint_button, 2, border_radius=5)
    hint_text = BUTTON_FONT.render("SHOW HINT", True, BLACK)
    win.blit(hint_text, (hint_button.centerx - hint_text.get_width()//2,
                         hint_button.centery - hint_text.get_height()//2))
    
    # Draw hint if used
    if state.hint_used:
        # Split hint into multiple lines if needed
        hint_words = state.hint.split()
        hint_lines = []
        current_line = ""
        
        for word in hint_words:
            test_line = f"{current_line} {word}" if current_line else word
            if BUTTON_FONT.size(test_line)[0] < WIDTH - 100:
                current_line = test_line
            else:
                hint_lines.append(current_line)
                current_line = word
        
        if current_line:
            hint_lines.append(current_line)
        
        for i, line in enumerate(hint_lines):
            hint_surface = BUTTON_FONT.render(line, True, BLACK)
            win.blit(hint_surface, (WIDTH//2 - hint_surface.get_width()//2, 520 + i*30))
    
    # Draw letters with hover effect
    mouse_pos = pygame.mouse.get_pos()
    for x, y, ltr, visible in state.letters:
        if visible:
            # Hover effect
            hover = math.sqrt((x - mouse_pos[0])**2 + (y - mouse_pos[1])**2) < RADIUS
            color = GREEN if hover else LIGHT_BLUE
            
            pygame.draw.circle(win, color, (x, y), RADIUS)
            pygame.draw.circle(win, BLACK, (x, y), RADIUS, 2)
            text = LETTER_FONT.render(ltr, True, BLACK)
            win.blit(text, (x - text.get_width()//2, y - text.get_height()//2))
    
    # Draw hangman
    draw_hangman(state.hangman_status)
    
    # Draw attempts remaining
    attempts_text = BUTTON_FONT.render(f"Attempts left: {MAX_ATTEMPTS - state.hangman_status}", True, BLACK)
    win.blit(attempts_text, (50, 20))
    
    pygame.display.update()

def show_message(message, duration=2000):
    """Display a message on screen."""
    win.fill(WHITE)
    text = TITLE_FONT.render(message, True, BLACK)
    win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
    pygame.display.update()
    time.sleep(duration / 1000)

def ask_to_play_again():
    """Prompt to play again and return user choice."""
    while True:
        win.fill(WHITE)
        text = TITLE_FONT.render("Play Again?", True, BLACK)
        win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))
        
        buttons = {
            "YES": pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 120, 50),
            "NO": pygame.Rect(WIDTH//2 + 30, HEIGHT//2, 120, 50)
        }
        
        mouse_pos = pygame.mouse.get_pos()
        for text, rect in buttons.items():
            color = GREEN if rect.collidepoint(mouse_pos) else LIGHT_BLUE
            pygame.draw.rect(win, color, rect, border_radius=10)
            pygame.draw.rect(win, BLACK, rect, 2, border_radius=10)
            btn_text = BUTTON_FONT.render(text, True, BLACK)
            win.blit(btn_text, (rect.centerx - btn_text.get_width()//2,
                               rect.centery - btn_text.get_height()//2))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if buttons["YES"].collidepoint(mouse_pos):
                    return True
                if buttons["NO"].collidepoint(mouse_pos):
                    return False

def main_game_loop(state):
    """Main game logic loop."""
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check hint button
                if WIDTH - 150 <= mouse_pos[0] <= WIDTH - 30 and 20 <= mouse_pos[1] <= 60:
                    state.hint_used = True
                
                # Check letter buttons
                for letter in state.letters:
                    x, y, ltr, visible = letter
                    if visible and math.sqrt((x - mouse_pos[0])**2 + (y - mouse_pos[1])**2) < RADIUS:
                        letter[3] = False
                        state.guessed.append(ltr)
                        if ltr not in state.word:
                            state.hangman_status += 1
            
            if event.type == pygame.KEYDOWN:
                key_pressed = event.unicode.upper()
                if key_pressed.isalpha() and key_pressed not in state.guessed:
                    state.guessed.append(key_pressed)
                    for letter in state.letters:
                        if letter[2] == key_pressed:
                            letter[3] = False
                    if key_pressed not in state.word:
                        state.hangman_status += 1
        
        draw_game(state)
        
        # Check win condition
        if all(letter in state.guessed for letter in state.word):
            show_message("YOU WON!")
            return
        
        # Check lose condition
        if state.hangman_status >= MAX_ATTEMPTS:
            win.fill(WHITE)
            text = TITLE_FONT.render("YOU LOST!", True, RED)
            win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
            
            word_text = WORD_FONT.render(f"The word was: {state.word}", True, BLACK)
            win.blit(word_text, (WIDTH//2 - word_text.get_width()//2, HEIGHT//2 + 20))
            
            pygame.display.update()
            time.sleep(3)
            return

def main():
    """Main game execution function."""
    state = GameState()
    
    while True:
        difficulty = select_difficulty()
        state.reset(difficulty)
        main_game_loop(state)
        
        if not ask_to_play_again():
            break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()