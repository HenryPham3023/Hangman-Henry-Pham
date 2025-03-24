import pygame
import math
import random

# Initialise Pygame
pygame.init()

# Screen Setup
WIDTH, HEIGHT = 1200, 800
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman Game!")

# Button variables
RADIUS = 20
GAP = 15
letters = []
def generate_letters():
    global letters
    letters = []
    startx = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)
    starty = 450
    A = 65
    for i in range(26):
        x = startx + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))
        y = starty + ((i // 13) * (GAP + RADIUS * 2))
        letters.append([x, y, chr(A + i), True])
generate_letters()

# Fonts
LETTER_FONT = pygame.font.SysFont('comicsans', 40)
WORD_FONT = pygame.font.SysFont('comicsans', 60)
TITLE_FONT = pygame.font.SysFont('comicsans', 70)
BUTTON_FONT = pygame.font.SysFont('comicsans', 30)

# Load images
images = [pygame.image.load(f"hangman{i}.png") for i in range(7)]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 223, 0)

# Difficulty Levels
word_lists = {
    "EASY": ["CAT", "DOG", "SUN", "CAR", "BALL"],
    "NORMAL": ["PYTHON", "REPLIT", "FAKER", "HANGMAN", "PYGAME"],
    "HARD": ["COMPLEXITY", "JAVASCRIPT", "ALGORITHM", "DEVELOPER", "FRAMEWORK"],
    "EXTREME": ["LEBRONJAMES", "FILIPVUJANIC", "MRZHUKOV", "HANGMANDEVELOPER"]
}

# Game Variables
win_count = 0  # Track consecutive wins
word = ""
hangman_status = 0
guessed = []

def select_difficulty():
    """ Displays difficulty selection screen and returns the chosen difficulty. """
    win.fill(WHITE)
    text = TITLE_FONT.render("Select Difficulty", 1, BLACK)
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))
    
    buttons = {
        "EASY": pygame.Rect(WIDTH // 2 - 100, 200, 200, 50),
        "NORMAL": pygame.Rect(WIDTH // 2 - 100, 270, 200, 50),
        "HARD": pygame.Rect(WIDTH // 2 - 100, 340, 200, 50),
        "EXTREME": pygame.Rect(WIDTH // 2 - 100, 410, 200, 50)
    }
    
    for level, rect in buttons.items():
        pygame.draw.rect(win, GRAY, rect)
        text = BUTTON_FONT.render(level.capitalize(), 1, BLACK)
        win.blit(text, (rect.x + 60, rect.y + 10))
    
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                for level, rect in buttons.items():
                    if rect.collidepoint((m_x, m_y)):
                        return level

def reset_game():
    """ Resets the game state, selects a new word, and restarts the game loop. """
    global hangman_status, word, guessed
    hangman_status = 0
    guessed = []
    generate_letters()

    difficulty = select_difficulty()
    if difficulty is None:
        pygame.quit()
        exit()

    word_list = word_lists.get(difficulty, [])
    if not word_list:
        print("Error: No words available for the selected difficulty.")
        pygame.quit()
        exit()

    word = random.choice(word_list)
    print(f"New word selected: {word}")  # Debugging output

def draw():
    """ Draws the game screen including letters, hangman, and stars. """
    win.fill(WHITE)
    text = TITLE_FONT.render("DEVELOPER HANGMAN", 1, BLACK)
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, 20))
    
    display_word = " ".join([letter if letter in guessed else "_" for letter in word])
    text = WORD_FONT.render(display_word, 1, BLACK)
    win.blit(text, (400, 250))
    
    for x, y, ltr, visible in letters:
        if visible:
            pygame.draw.circle(win, BLACK, (x, y), RADIUS, 3)
            text = LETTER_FONT.render(ltr, 1, BLACK)
            win.blit(text, (x - text.get_width() / 2, y - text.get_height() / 2))
    
    win.blit(images[hangman_status], (150, 120))
    
    # Draw stars
    for i in range(win_count):
        pygame.draw.polygon(win, YELLOW, [(50 + i * 50, 50), (60 + i * 50, 75), (40 + i * 50, 75)])

    pygame.display.update()

def main():
    """ Main game loop handling player input and game progression. """
    global hangman_status, win_count
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                for letter in letters:
                    x, y, ltr, visible = letter
                    if visible and math.sqrt((x - m_x) ** 2 + (y - m_y) ** 2) < RADIUS:
                        letter[3] = False
                        guessed.append(ltr)
                        if ltr not in word:
                            hangman_status += 1
        
        draw()
        
        if all(letter in guessed for letter in word):
            win_count = min(win_count + 1, 5)
            if win_count == 5:
                display_end_message("You Win the Game!")
                pygame.quit()
                exit()
            return "win"
        
        if hangman_status == 6:
            win_count = 0
            return "lose"

def display_end_message(message):
    """ Displays the end message and waits for user input to restart or exit. """
    win.fill(WHITE)
    text = WORD_FONT.render(message, 1, BLACK)
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
    pygame.display.update()
    pygame.time.delay(2000)
    reset_game()

# Start the Game
reset_game()
while True:
    result = main()
    if result:
        display_end_message("You " + result.upper() + "!")
