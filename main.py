import pygame
from pygame import mixer
import os
from geese import Geese
from jin import Jin
from menu import Menu
from pause_menu import PauseMenu
from character_selection import CharacterSelection
from stage_selection import StageSelection
from question_manager import QuestionManager  # Importing new QuestionManager class
from user_database import UserDatabaseManager  # Handles student and teacher accounts

class Game:
    def __init__(self):
        # Initialize Pygame and mixer
        mixer.init()
        pygame.init()

        # Create game window
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Proj")

        # Set framerate
        self.clock = pygame.time.Clock()
        self.FPS = 50

        # Define colours
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.WHITE = (255, 255, 255)

        # Initialize rounds and rewards
        self.rounds_available = 0
        self.round_reward = 1  # Default rounds rewarded for correct answer

        # Initialize the user database and question manager
        self.user_db = UserDatabaseManager()  # Manages student and teacher accounts
        self.question_manager = QuestionManager(self.user_db)  # Link question manager to user database

        # Define game variables
        self.intro_count = 2
        self.last_count_update = pygame.time.get_ticks()
        self.score = [0, 0]  # Player scores. [P1, P2]
        self.round_over = False
        self.ROUND_OVER_COOLDOWN = 2000
        self.reset_delay = 1000  # Delay before resetting fighters after Geese's win pose
        self.round_timer = 60 * 1000  # 60 seconds in milliseconds
        self.round_start_time = 0

        # Load music and sounds
        pygame.mixer.music.load(r"assets/audio/music2.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, 0.0, 5000)
        self.sword_fx = pygame.mixer.Sound(r"assets/audio/sword.wav")
        self.sword_fx.set_volume(0.5)
        self.magic_fx = pygame.mixer.Sound(r"assets/audio/magic.wav")
        self.magic_fx.set_volume(0.75)

        # Load background images
        self.bg_images = {
            "stage1": pygame.image.load(r"assets/images/background/background.jpg").convert_alpha(),
            "stage2": pygame.image.load(r"assets/images/background/background2.jpg").convert_alpha(),
            "stage3": pygame.image.load(r"assets/images/background/background3.gif").convert_alpha(),
            "stage4": pygame.image.load(r"assets/images/background/background4.png").convert_alpha(),
        }

        # Load victory image
        self.victory_img = pygame.image.load(r"assets/images/icons/victory.png").convert_alpha()

        # Define font
        self.count_font = pygame.font.Font(r"assets/fonts/turok.ttf", 80)
        self.score_font = pygame.font.Font(r"assets/fonts/turok.ttf", 30)

        # Initialize menus and selection screens
        self.menu = Menu(self.screen, self.user_db)
        self.pause_menu = PauseMenu(self.screen)
        self.char_select = CharacterSelection(self.screen)
        self.stage_select = StageSelection(self.screen)

        # Initialize question manager for question handling
        self.teacher_password = self.question_manager.password  # Load teacher password

        # Game state and other settings
        self.game_state = "menu"
        self.fighter_1, self.fighter_2 = None, None
        self.run = True
        self.selected_bg = self.bg_images["stage1"]
        self.paused = False
        self.password_attempts = 0
        self.logged_in_student = None  # Track the currently logged-in student

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def draw_bg(self, background):
        scaled_bg = pygame.transform.scale(background, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.screen.blit(scaled_bg, (0, 0))

    def draw_health_bar(self, health, x, y):
        ratio = health / 100
        pygame.draw.rect(self.screen, self.WHITE, (x - 2, y - 2, 404, 34))
        pygame.draw.rect(self.screen, self.RED, (x, y, 400, 30))
        pygame.draw.rect(self.screen, self.YELLOW, (x, y, 400 * ratio, 30))

    def reset_fighters(self, p1_character, p2_character):
        if p1_character == "Geese":
            self.fighter_1 = Geese(1, 200, 310, False, self.sword_fx)
        elif p1_character == "Jin":
            self.fighter_1 = Jin(1, 200, 310, False, self.magic_fx)
        if p2_character == "Geese":
            self.fighter_2 = Geese(2, 700, 310, True, self.sword_fx)
        elif p2_character == "Jin":
            self.fighter_2 = Jin(2, 700, 310, True, self.magic_fx)

        # Ensure intro_played is reset for new rounds
        if isinstance(self.fighter_1, Geese):
            self.fighter_1.intro_played = False
        if isinstance(self.fighter_2, Geese):
            self.fighter_2.intro_played = False

    def load_stage_music(self, stage):
        music_files = {
            "stage1": r"assets/audio/music4.mp3",
            "stage2": r"assets/audio/music.mp3",
            "stage3": r"assets/audio/music3.mp3",
            "stage4": r"assets/audio/music5.mp3",
        }
        pygame.mixer.music.load(music_files[stage])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, 0.0, 5000)

    def text_input(self, screen, font, prompt):
        """
        Function to handle text input in Pygame.
        """
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
                        input_active = False  # Exit the input loop on Enter
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]  # Delete last character
                    else:
                        input_text += event.unicode  # Add the pressed character

        return input_text  # Return the entered text

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            self.menu.handle_events(event)

    def handle_fighting_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

    def reset_menu(self):
        self.menu.selected_mode = None
        self.menu.current_selection = 0
        self.menu.confirm_quit = False
        self.menu.confirm_quit_selection = 0

    def load_teacher_password(self):
        # Load the password from file, or use default '999999' if file doesn't exist
        if os.path.exists("password.txt"):
            with open("password.txt", "r") as f:
                return f.read().strip()
        return "999999"  # Default password if no file exists

    def change_password(self, screen, font):
        # Ask for the new password once
        new_password = self.question_manager.text_input(screen, font, "Enter new password: ")

        if new_password:
            # Save the new password to password.txt
            with open(self.question_manager.password_file, 'w') as p_file:
                p_file.write(new_password)

            # Update the in-memory password
            self.teacher_password = new_password  # Sync with in-memory variable
            self.question_manager.password = new_password  # Sync with QuestionManager password

            print("Password changed successfully and saved permanently.")

    def handle_teacher_login(self):
        # Teacher login screen for password input
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 40)
        self.draw_text("Enter Teacher Password:", font, self.WHITE, 300, 250)

        password_input = ""
        input_active = True

        # Load or set the password (depending on whether password.txt exists)
        self.teacher_password = self.question_manager.load_password()

        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Check if the input matches the stored password
                        if password_input == self.teacher_password:
                            print("[DEBUG] Correct password entered. Switching to teacher options.")
                            self.game_state = "teacher_options"
                            input_active = False  # Exit the input loop and move to teacher options
                        else:
                            self.password_attempts += 1
                            if self.password_attempts >= 7:
                                self.draw_text("Give up, child!", font, self.RED, 300, 350)
                            password_input = ""  # Reset input
                    elif event.key == pygame.K_BACKSPACE:
                        password_input = password_input[:-1]
                    else:
                        password_input += event.unicode

            # Refresh screen with the current password input
            self.screen.fill((0, 0, 0))
            self.draw_text("Enter Teacher Password:", font, self.WHITE, 300, 250)
            self.draw_text(password_input, font, self.WHITE, 300, 300)
            pygame.display.update()

    def handle_teacher_options(self):
        options = [
            "Add Question",
            "Remove Question",
            f"Set Round Reward (Current: {self.round_reward} rounds per question)",
            "Change Password",
            "View Student Performance",
            "View Overall Question Stats",
            "Back to Selection Screen"  # This option will take the user back to the main menu
        ]

        selected_option = 0
        font = pygame.font.Font(None, 40)
        input_active = True

        while input_active:
            self.screen.fill((0, 0, 0))

            # Display the menu options
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == selected_option else (255, 255, 255)
                self.draw_text(option, font, color, 300, 150 + i * 50)

            self.draw_text("Press Enter to select an option.", font, self.WHITE, 100, 500)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # Add Question
                            self.question_manager.add_question(self.screen, font)
                        elif selected_option == 1:  # Remove Question
                            self.question_manager.remove_question(self.screen, font)
                        elif selected_option == 2:  # Set Round Reward
                            self.round_reward = self.question_manager.set_round_reward(self.screen, font)
                        elif selected_option == 3:  # Change Password
                            self.change_password(self.screen, font)
                        elif selected_option == 4:  # View Student Performance
                            self.show_student_performance(font)
                        elif selected_option == 5:  # View Overall Question Stats
                            self.show_question_stats(font)
                        elif selected_option == 6:  # Back to Selection Screen
                            self.game_state = "menu"  # This will take you back to the main menu
                            input_active = False
                            return  # Exit this loop and go back to main menu

    def show_student_performance(self, font):
        students_performance = self.user_db.get_all_students_performance()

        if not students_performance:
            self.screen.fill((0, 0, 0))
            self.draw_text("No student performance data available.", font, self.WHITE, 200, 300)
            pygame.display.update()
            pygame.time.wait(2000)
            return

        selected_student = 0
        input_active = True

        while input_active:
            self.screen.fill((0, 0, 0))

            # Display each student's performance with a selection option
            self.draw_text("Student Performance Summary", font, self.WHITE, 100, 100)
            for i, student in enumerate(students_performance):
                username, correct_answers, incorrect_answers = student
                color = self.YELLOW if i == selected_student else self.WHITE
                self.draw_text(f"{username}: {correct_answers} Correct, {incorrect_answers} Incorrect", font, color,
                               100, 150 + i * 50)

            self.draw_text("Press Enter to view details, D to delete, or ESC to go back.", font, self.WHITE, 100, 500)
            pygame.display.update()

            # Handle student selection
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_student = (selected_student + 1) % len(students_performance)
                    elif event.key == pygame.K_UP:
                        selected_student = (selected_student - 1) % len(students_performance)
                    elif event.key == pygame.K_RETURN:
                        # Get the selected student's user ID and display detailed performance
                        username = students_performance[selected_student][0]
                        self.show_student_details(username, font)
                    elif event.key == pygame.K_d:
                        # Delete selected student
                        username = students_performance[selected_student][0]
                        self.user_db.delete_student(username)
                        print(f"[DEBUG] Deleted student: {username}")
                        students_performance.pop(selected_student)  # Remove student from the list
                    elif event.key == pygame.K_ESCAPE:
                        input_active = False

    def student_login(self, screen, font):
        # Handle student login prompt
        username = self.text_input(screen, font, "Enter Username: ")
        password = self.text_input(screen, font, "Enter Password: ")

        user = self.user_db.verify_login(username, password)
        print(f"[DEBUG] verify_login returned: {user}")

        if user and user[3] == "student":  # Assuming user[3] is the role
            self.logged_in_student = user[0]  # Store the student's user_id
            print(f"Student {username} logged in successfully with user_id={self.logged_in_student}.")
            return True
        else:
            print(f"Login failed for {username}.")
            return False

    def show_student_details(self, username, font):
        # Get student ID from the username using the user database manager
        self.user_db.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = self.user_db.cursor.fetchone()

        if user:
            user_id = user[0]

            # Get detailed performance for the student
            question_details = self.user_db.get_student_question_details(user_id)

            input_active = True

            while input_active:
                self.screen.fill((0, 0, 0))
                self.draw_text(f"{username}'s Performance", font, self.WHITE, 100, 100)

                # Display each question and whether the student got it correct
                for i, (question, answer, correct) in enumerate(question_details):
                    result = "Correct" if correct == 1 else "Incorrect"
                    color = self.YELLOW if correct == 1 else self.RED
                    self.draw_text(f"Q{i + 1}: {question} | Your Answer: {answer} | {result}", font, color, 100,
                                   150 + i * 50)

                self.draw_text("Press Enter to go back.", font, self.WHITE, 100, 500)
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            input_active = False  # Go back to the previous menu
        else:
            print(f"No user found with username: {username}")

    def show_question_stats(self, font):
        question_stats = self.user_db.get_question_correct_percentage()

        if not question_stats or all(total_answers == 0 for _, total_answers, _, _ in question_stats):
            self.screen.fill((0, 0, 0))
            self.draw_text("No question statistics available.", font, self.WHITE, 200, 300)
            pygame.display.update()
            pygame.time.wait(2000)
            return

        input_active = True

        while input_active:
            self.screen.fill((0, 0, 0))
            self.draw_text("Overall Question Statistics", font, self.WHITE, 100, 100)

            # Display each question's stats
            for i, (question, total_answers, correct_answers, percentage_correct) in enumerate(question_stats):
                percentage_text = f"{percentage_correct:.2f}%" if total_answers > 0 else "No answers"
                self.draw_text(f"Q{i + 1}: {question} | {correct_answers}/{total_answers} Correct | {percentage_text}",
                               font, self.WHITE, 100, 150 + i * 50)

            self.draw_text("Press Enter to go back.", font, self.WHITE, 100, 500)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False

    def handle_question_time(self):
        font = pygame.font.Font(None, 40)

        # Debugging: Make sure `self.logged_in_student` is set before starting question time
        print(f"[DEBUG] handle_question_time: logged_in_student={self.logged_in_student}")

        # Load previously answered questions for the student
        questions_answered = self.question_manager.load_correctly_answered_questions(self.logged_in_student)
        current_question_index = None
        retry_question = False

        running_question_time = True

        while running_question_time:
            if not retry_question:
                # Ask a new random question
                correct_answer, question_index = self.question_manager.ask_random_question(self.screen, font,
                                                                                           questions_answered)
            else:
                # Ask the same question again if retrying
                correct_answer, question_index = self.question_manager.ask_specific_question(self.screen, font,
                                                                                             current_question_index)
                retry_question = False  # Reset retry flag

            # Debugging: Print current status of the answer, question index, and logged-in student
            print(
                f"[DEBUG] Correct Answer: {correct_answer}, Question Index: {question_index}, Logged in Student: {self.logged_in_student}")

            # If no more questions are available
            if correct_answer is None:
                self.screen.fill((0, 0, 0))
                self.draw_text("You have completed all questions.", font, self.WHITE, 200, 300)
                self.draw_text("Press Enter to exit.", font, self.WHITE, 200, 350)
                pygame.display.update()

                waiting_for_exit = True
                while waiting_for_exit:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            waiting_for_exit = False
                            self.game_state = "menu"
                            return

            # Record performance (whether correct or incorrect)
            if correct_answer:
                self.rounds_available += self.round_reward
                self.draw_text(f"Correct! You now have {self.rounds_available} rounds.", font, self.WHITE, 200, 300)
                questions_answered.append(question_index)
                self.question_manager.save_correctly_answered_question(self.logged_in_student, question_index)

                # Record correct answer in the database
                print(
                    f"[DEBUG] Recording correct answer for user_id={self.logged_in_student}, question_id={question_index}")
                self.user_db.record_student_performance(self.logged_in_student, question_index, "correct", 1)
            else:
                # Record incorrect attempt immediately
                print(
                    f"[DEBUG] Recording incorrect answer for user_id={self.logged_in_student}, question_id={question_index}")
                self.user_db.record_student_performance(self.logged_in_student, question_index, "incorrect", 0)
                self.draw_text("Incorrect!", font, self.RED, 200, 300)

            pygame.display.update()
            pygame.time.wait(2000)

            # Show options for retrying or proceeding
            current_selection = 0
            selecting_option = True

            # Retry if incorrect, otherwise allow proceeding or quitting
            options = ["Retry", "Proceed", "Quit"] if not correct_answer else ["Proceed", "Quit"]

            while selecting_option:
                self.screen.fill((0, 0, 0))
                self.draw_text("Select an option:", font, self.WHITE, 200, 300)

                for i, option in enumerate(options):
                    color = self.YELLOW if i == current_selection else self.WHITE
                    self.draw_text(option, font, color, 200, 350 + i * 50)

                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN:
                            current_selection = (current_selection + 1) % len(options)
                        elif event.key == pygame.K_UP:
                            current_selection = (current_selection - 1) % len(options)
                        elif event.key == pygame.K_RETURN:
                            if options[current_selection] == "Proceed":
                                selecting_option = False
                            elif options[current_selection] == "Retry":
                                retry_question = True
                                current_question_index = question_index  # Retry the same question
                                selecting_option = False
                            elif options[current_selection] == "Quit":
                                self.game_state = "menu"
                                return
                    pygame.display.update()

    from game_loop import game_loop

    def cleanup(self):
        # Function to delete the correct_answers.txt file on game exit
        correct_answers_file = self.question_manager.correct_answers_file
        if os.path.exists(correct_answers_file):
            os.remove(correct_answers_file)
            print(f"[DEBUG] {correct_answers_file} deleted on game exit.")


if __name__ == "__main__":
    game = Game()
    game.game_loop()



            