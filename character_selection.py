import pygame

class CharacterSelection:
    def __init__(self, screen):
        # Initialize character selection properties
        self.screen = screen
        self.font = pygame.font.Font(r"assets/fonts/turok.ttf", 30)
        self.characters = ["Geese", "Jin"]
        self.p1_selection = None
        self.p2_selection = None
        self.p1_index = 0
        self.p2_index = 0

    def draw_text(self, text, x, y, color=(255, 255, 255), center=False):
        # Draw text on the screen
        img = self.font.render(text, True, color)
        if center:
            rect = img.get_rect(center=(x, y))
            self.screen.blit(img, rect)
        else:
            self.screen.blit(img, (x, y))

    def draw_selection(self):
        # Draw the character selection screen
        self.screen.fill((0, 0, 0))

        # Display Player 1 and Player 2 character selection prompts
        self.draw_text("Player 1 Character Selection", 250, 100, color=(255, 255, 255), center=True)
        self.draw_text("Player 2 Character Selection", 750, 100, color=(255, 255, 255), center=True)

        # Display Player 1 and Player 2 selectable characters
        for i, char in enumerate(self.characters):
            p1_color = (0, 0, 139) if i == self.p1_index else (255, 255, 255) # Blue if selected, white if not
            p2_color = (139, 0, 0) if i == self.p2_index else (255, 255, 255) # Red if selected, white if not
            self.draw_text(char, 250, 200 + i * 50, color=p1_color, center=True)
            self.draw_text(char, 750, 200 + i * 50, color=p2_color, center=True) # explained in menu.py
    def handle_events(self, event):
        # Handle keyboard events for character selections
        if event.type == pygame.KEYDOWN:
            # Player 1 controls
            if event.key == pygame.K_w:
                self.p1_index = (self.p1_index - 1) % len(self.characters)
            elif event.key == pygame.K_s:
                self.p1_index = (self.p1_index + 1) % len(self.characters) # explained in menu.py
            elif event.key == pygame.K_TAB:
                self.p1_selection = self.characters[self.p1_index] # stores the player 1 selection

            # Player 2 controls
            if event.key == pygame.K_UP:
                self.p2_index = (self.p2_index - 1) % len(self.characters)
            elif event.key == pygame.K_DOWN:
                self.p2_index = (self.p2_index + 1) % len(self.characters)
            elif event.key == pygame.K_RETURN: # the enter key
                self.p2_selection = self.characters[self.p2_index] # stores the player 2 selection

    def is_selection_complete(self):
        # Check if both players have made their selections
        return self.p1_selection is not None and self.p2_selection is not None # checks if both players have confirmed their selection. return self.p1_selection is not None means return true if the selection is not None, because initially its sent to none. if its set to something, its definetely a character and so the user definetley picked someone4


