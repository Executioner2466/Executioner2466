import pygame

class PauseMenu:
    def __init__(self, screen):
        # Initialize pause menu properties
        self.screen = screen
        self.font = pygame.font.Font(r"assets/fonts/turok.ttf", 30)
        self.current_selection = 0
        self.confirm_quit = False
        self.confirm_quit_selection = 0
        self.options = ["Resume Game", "Go to Selection Screen", "Quit Game"]

    def draw_text(self, text, x, y, color=(255, 255, 255), center=False):
        # Draw text on the screen
        img = self.font.render(text, True, color)
        if center:
            rect = img.get_rect(center=(x, y))
            self.screen.blit(img, rect)
        else:
            self.screen.blit(img, (x, y))

    def draw_menu(self, rounds_available):
        # Draw the pause menu with options and the correct rounds available
        self.screen.fill((0, 0, 0))

        # Display the number of available rounds (units)
        self.draw_text(f"Rounds Available: {rounds_available}", 20, 20, color=(255, 255, 255))

        if self.confirm_quit:
            self.draw_text("Are you sure you want to quit?", 500, 300, color=(255, 255, 255), center=True)
            self.draw_text("Yes", 500, 350, color=(255, 255, 0) if self.confirm_quit_selection == 0 else (255, 255, 255), center=True)
            self.draw_text("No", 500, 400, color=(255, 255, 0) if self.confirm_quit_selection == 1 else (255, 255, 255), center=True)
        else:
            for i, option in enumerate(self.options):
                color = (255, 255, 0) if i == self.current_selection else (255, 255, 255)
                self.draw_text(option, 500, 200 + i * 50, color=color, center=True)

    def handle_events(self, event):
        # Handle keyboard events for pause menu selections
        if self.confirm_quit:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    self.confirm_quit_selection = 1 - self.confirm_quit_selection  # Toggle between Yes (0) and No (1)
                elif event.key == pygame.K_RETURN:
                    if self.confirm_quit_selection == 0:  # Yes, quit the game
                        pygame.quit()
                        exit()
                    else:  # No, return to the pause menu
                        self.confirm_quit = False
                        return "pause"  # Return to the pause menu

        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.current_selection = (self.current_selection + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.current_selection = (self.current_selection - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.current_selection == 0:  # Resume Game
                        return "resume"
                    elif self.current_selection == 1:  # Go to Selection Screen
                        return "selection_screen"
                    elif self.current_selection == 2:  # Quit Game
                        self.confirm_quit = True
                elif event.key == pygame.K_ESCAPE:
                    return "resume"
        return None
