import os
import random
import pygame

class QuestionManager:
    def __init__(self, user_db):
        self.question_file = "questions/questions.txt"
        self.answer_file = "questions/answers.txt"
        self.password_file = "questions/password.txt"  # File to store the teacher password
        self.correct_answers_file = "questions/correct_answers.txt"  # File to store correct answers
        self.round_reward = 1  # Default rounds rewarded for correct answer
        self.user_db = user_db  # Integrating with the user database
        self.ensure_files_exist()
        self.password = self.load_password()

    def ensure_files_exist(self):
        os.makedirs(os.path.dirname(self.question_file), exist_ok=True)
        if not os.path.exists(self.question_file):
            with open(self.question_file, 'w') as f:
                pass
        if not os.path.exists(self.answer_file):
            with open(self.answer_file, 'w') as f:
                pass
        if not os.path.exists(self.password_file):
            # Set default password if the file doesn't exist
            with open(self.password_file, 'w') as f:
                f.write("999999")
        if not os.path.exists(self.correct_answers_file):
            # Create the correct answers file if it doesn't exist
            with open(self.correct_answers_file, 'w') as f:
                pass

    def load_password(self):
        if os.path.exists(self.password_file):
            with open(self.password_file, 'r') as p_file:
                password = p_file.read().strip()
                print(f"[DEBUG] Loaded password from file: {password}")
                return password  # Return the password from the file
        else:
            with open(self.password_file, 'w') as p_file:
                p_file.write("999999")
            return "999999"  # Default password

    def change_password(self, screen, font):
        new_password = self.text_input(screen, font, "Enter new password: ")
        if new_password:
            with open(self.password_file, 'w') as p_file:
                p_file.write(new_password)
            self.password = new_password  # Sync the in-memory password
            print("Password changed successfully and saved permanently.")

    def load_correctly_answered_questions(self, user_id=None):
        # Load previously answered questions from file or database for a user
        if user_id:
            return self.user_db.get_student_performance(user_id)  # Load from DB for the logged-in student
        else:
            if os.path.exists(self.correct_answers_file):
                with open(self.correct_answers_file, 'r') as f:
                    return [int(line.strip()) for line in f.readlines()]
            return []

    def save_correctly_answered_question(self, question_index, user_id=None):
        if user_id:
            # Ensure the correct `question_id` is saved to the database
            self.user_db.record_student_performance(user_id, question_index, "correct", 1)
        else:
            # Save the correctly answered question index to the file
            with open(self.correct_answers_file, 'a') as f:
                f.write(f"{question_index}\n")

    def get_questions(self):
        with open(self.question_file, 'r') as q_file:
            return q_file.readlines()

    def get_question_correct_percentage(self):
        """
        Get the percentage of students who answered each question correctly.
        """
        self.cursor.execute('''
            SELECT q.question,
                   COUNT(p.id) as total_answers,
                   SUM(CASE WHEN p.correct = 1 THEN 1 ELSE 0 END) as correct_answers,
                   CASE WHEN COUNT(p.id) > 0 
                        THEN (SUM(CASE WHEN p.correct = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(p.id)) 
                        ELSE 0 END as percentage_correct
            FROM questions q
            LEFT JOIN student_performance p ON q.id = p.question_id
            GROUP BY q.id
        ''')
        return self.cursor.fetchall()

    def ask_random_question(self, screen, font, questions_answered):
        """
        Ask a random question and check if the answer is correct.
        """
        questions = self.get_questions()  # Fetch the list of all questions
        available_questions = [i for i in range(len(questions)) if i not in questions_answered]

        if not available_questions:
            return None, None  # No more questions available

        question_index = random.choice(available_questions)  # Select a random question index
        question = questions[question_index].strip()  # Get the question text

        # Display the question and get player's answer
        player_answer = self.text_input(screen, font, question).lower().replace(" ", "")  # Normalize user input
        correct_answer = self.get_correct_answer(question_index)  # Get the correct answer

        return player_answer == correct_answer, question_index  # Return both the correctness and the question index

    def ask_specific_question(self, screen, font, question_index):
        questions = self.get_questions()
        question = questions[question_index].strip()
        correct_answer = self.get_correct_answer(question_index)

        player_answer = self.text_input(screen, font, question).lower().replace(" ", "")
        return player_answer == correct_answer, question_index

    def get_correct_answer(self, question_index):
        """
        Retrieve the correct answer for a given question from the answers file.
        """
        with open(self.answer_file, 'r') as file:
            answers = file.readlines()
        if 0 <= question_index < len(answers):
            return answers[question_index].strip().lower().replace(" ", "")  # Normalize the answer
        return None

    def add_question(self, screen, font):
        question = self.text_input(screen, font, "Enter the question: ")
        answer = self.text_input(screen, font, "Enter the answer: ")

        with open(self.question_file, 'a') as q_file:
            q_file.write(question + '\n')

        with open(self.answer_file, 'a') as a_file:
            a_file.write(answer.lower().replace(" ", "") + '\n')

        print("Question added successfully.")

    def remove_question(self, screen, font):
        questions = self.get_questions()
        if not questions:
            print("There are no questions to remove.")
            return

        print("Choose a question to remove:")
        for idx, question in enumerate(questions):
            print(f"{idx + 1}. {question.strip()}")

        choice = int(self.text_input(screen, font, "Enter the number of the question to remove: ")) - 1

        if 0 <= choice < len(questions):
            with open(self.question_file, 'w') as q_file:
                with open(self.answer_file, 'r') as a_file:
                    answers = a_file.readlines()

                with open(self.answer_file, 'w') as a_file:
                    for i in range(len(questions)):
                        if i != choice:
                            q_file.write(questions[i])
                            a_file.write(answers[i])
            print("Question removed successfully.")
        else:
            print("Invalid choice.")

    def set_round_reward(self, screen, font):
        reward = float(self.text_input(screen, font, "Set the reward rounds per correct answer (1, 2, 3, 4, 5): "))
        if reward in [1, 2, 3, 4, 5]:
            print(f"Round reward set to {reward} rounds per correct answer.")
            self.round_reward = reward
            return reward
        else:
            print("Invalid reward, setting to default (1 round).")
            return 1

    def text_input(self, screen, font, prompt):
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

    def draw_text(self, screen, font, text, color, x, y):
        img = font.render(text, True, color)
        screen.blit(img, (x, y))

