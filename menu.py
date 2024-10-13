import pygame

class Menu:
    def __init__(self, screen, user_db):
        # Initialize menu properties
        self.screen = screen
        self.font = pygame.font.Font(r"assets/fonts/turok.ttf", 30)
        self.selected_mode = None

        # Load background image and selection sound
        self.menu_background = pygame.image.load(r"assets/images/background/menu_background.png").convert_alpha()
        self.select_sound = pygame.mixer.Sound('assets/audio/select.mp3')

        # Track menu options and selection
        self.current_selection = 0
        self.options = ["Player vs Player", "Teacher Login", "Student Login", "Register", "Question Time"]
        self.confirm_quit = False
        self.confirm_quit_selection = 0

        # User database reference for login and registration
        self.user_db = user_db
        self.logged_in_user = None

    def draw_text(self, text, x, y, color=(255, 255, 255), center=False):
        # Draw text on the screen
        img = self.font.render(text, True, color)
        if center:
            rect = img.get_rect(center=(x, y))
            self.screen.blit(img, rect)
        else:
            self.screen.blit(img, (x, y))

    def draw_menu(self, rounds_available):
        self.screen.blit(self.menu_background, (0, 0))
        self.draw_text(f"Rounds Available: {rounds_available}", 50, 50)

        if self.confirm_quit:
            self.draw_text("Are you sure you want to quit?", 500, 300, center=True)
            self.draw_text("Yes", 500, 350,
                           color=(255, 255, 0) if self.confirm_quit_selection == 0 else (255, 255, 255), center=True)
            self.draw_text("No", 500, 400, color=(255, 255, 0) if self.confirm_quit_selection == 1 else (255, 255, 255),
                           center=True)
        else:
            self.draw_text("Select Game Mode", 500, 200, center=True)
            for i, option in enumerate(self.options):
                color = (255, 255, 0) if i == self.current_selection else (255, 255, 255)

                # Grey out "Question Time" if the student isn't logged in
                if option == "Question Time" and not self.logged_in_user:
                    color = (100, 100, 100)  # Grey out color
                    self.draw_text(option, 500, 250 + i * 50, color=color, center=True)
                else:
                    self.draw_text(option, 500, 250 + i * 50, color=color, center=True)

    def handle_events(self, event, rounds_available):
        if self.confirm_quit:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    self.confirm_quit_selection = 1 - self.confirm_quit_selection
                elif event.key == pygame.K_RETURN:
                    if self.confirm_quit_selection == 0:
                        pygame.quit()
                        exit()
                    else:
                        self.confirm_quit = False
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.current_selection = (self.current_selection + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.current_selection = (self.current_selection - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.options[self.current_selection] == "Player vs Player" and rounds_available == 0:
                        return  # Locked if no rounds available

                    # Handle each selection case
                    self.selected_mode = self.options[self.current_selection]
                    self.select_sound.play()

                    # Handle the "Student Login" case
                    if self.selected_mode == "Student Login":
                        logged_in = self.student_login(self.screen, self.font)
                        if logged_in:
                            print("Student logged in.")
                            self.options[4] = "Question Time"  # Enable Question Time when logged in

                    # Handle the "Register" case
                    elif self.selected_mode == "Register":
                        registered = self.register_user(self.screen, self.font)
                        if registered:
                            print("User registered successfully.")

                    elif self.selected_mode == "Question Time":
                        # Ensure user is logged in before allowing Question Time
                        if self.logged_in_user:
                            print("Starting Question Time")
                        else:
                            print("Please log in first.")

                elif event.key == pygame.K_ESCAPE:
                    self.confirm_quit = True

    def is_selection_complete(self):
        # Check if a game mode is selected
        return self.selected_mode is not None

    def student_login(self, screen, font):
        username = self.text_input(screen, font, "Enter Username: ")
        password = self.text_input(screen, font, "Enter Password: ")

        user = self.user_db.verify_login(username, password)
        if user and user[3] == "student":
            self.logged_in_user = user
            print(f"Student {username} logged in successfully.")
            return True
        else:
            print(f"Login failed for {username}. Check your credentials.")
            return False

    def register_user(self, screen, font):
        username = self.text_input(screen, font, "Create Username: ")
        password = self.text_input(screen, font, "Create Password: ")

        success = self.user_db.create_user(username, password, role="student")
        if success:
            print(f"Student {username} registered successfully.")
            return True
        else:
            print(f"Registration failed. Username {username} already exists.")
            return False

    def text_input(self, screen, font, prompt):
        # Function to handle text input in Pygame
        input_text = ""
        input_active = True

        while input_active:
            screen.fill((0, 0, 0))
            img = font.render(prompt, True, (255, 255, 255))
            screen.blit(img, (100, 200))
            input_img = font.render(input_text, True, (255, 255, 255))
            screen.blit(input_img, (100, 250))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

        return input_text

# How the selection traversal works:
# self.current_selection + 1: When the player presses the down arrow key, the current selection index is incremented by 1. This moves the selection to the next menu item
# self.current_selection - 1: When the player presses the up arrow key, the current selection index is decremented by 1. This moves the selection to the previous menu item

# drawing the menu:
# self.screen.blit(...): blit is short for "block transfer" and it’s used to draw one image onto another. In this case, self.screen.blit(self.menu_background, (0, 0)) draws the menu_background image onto the screen at the position (0, 0), which is the top-left corner of the screen.
# self.draw_text(f"Rounds Available: {rounds_available}", 50, 50): This draws the number of rounds available in the top-left corner of the screen. The draw_text() method renders the string f"Rounds Available: {rounds_available}" using the Font object created in __init__(). It then blits the rendered text image at position (50, 50)
# self.font.render(text, True, color): This turns the text string into an image (called a "surface" in pygame) that can be drawn on the screen. The True argument is for antialiasing (smoothing the text), and color defines the text color. I know this because the render method is bacially - Font.render(text, antialias, color, background=None). the background=none means by default if not set, background is none
# img.get_rect(center=(x, y)): get_rect() creates a rectangle (rect) that encloses the image. By passing center=(x, y), it places the center of the text at the (x, y) coordinates. This makes it easier to align text in the center of the screen.
#self.screen.blit(img, rect): Blits the rendered text image at the specified rectangle.
# the play method is from pygame mixer, used just for sounds
# Toggling Selection: The expression 1 - self.confirm_quit_selection toggles between 0 and 1. If the current selection is "Yes" (0), pressing the down/up arrow switches it to "No" (1), and vice versa. In handle_events(), if self.confirm_quit is True, the quit confirmation options ("Yes" or "No") are handled by switching between the two options when the player presses the up/down arrow keys, and confirming the selection when "Enter" is pressed.
# is_selection: This method simply checks if the player has made a valid selection. Initially, self.selected_mode is None. When the player presses "Enter" on a valid menu option, it is set to the selected option (e.g., "Player vs Player"). Thus, is_selection_complete() returns True once the player has chosen something.
# use of %: self.current_selection stores the index of the currently selected menu option. len(self.options) gives the total number of options in the menu (len(self.options) is 3 because the options are ["Player vs Player", "Teacher Login", "Question Time"]). The % operator ensures that the selection stays within the bounds of the available options.
# when cycling down, self.current_selection = (self.current_selection + 1) % len(options) executes. current selection is 0, which is player vs player. The code executes and self.current_selection + 1 = 0 + 1 = 1, 1 % 3 is 1 and so teacher login is selected. when going down again, 1+1=2 and 2 % 3 is 2, so question time is selected. when pressing down again, 2+1=3 and 3 % 3 is 0, bringing selection back to player vs player, never going out of the index.
# when cycling up, self.current_selection = (self.current_selection + 1) % len(options) executes. current selection is 0, so player vs player is selected. going up means the value of 0 is substracted by 1 so 0 - 1 = -1 and -1 % 3 is 2, so question time is selected. upwards again means 2-1=1 and 1 % 3 is 1, so teacher login is selected