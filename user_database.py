import sqlite3

class UserDatabaseManager:
    def __init__(self, db_name="game_users.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Table for users: students and teachers
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question_id INTEGER,
                answer TEXT,
                correct INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # Table for storing each student's performance
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question_id INTEGER,
                answer TEXT,
                correct INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # Table for questions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                correct_answer TEXT
            )
        ''')

        self.connection.commit()

    def create_user(self, username, password, role="student"):
        try:
            self.cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                                (username, password, role))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

    def verify_login(self, username, password):
        # Fetch the user record from the database where username and password match
        self.cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = self.cursor.fetchone()

        # Add debug statement to check what is returned
        print(f"[DEBUG] verify_login returned: {user}")

        return user

    def record_student_performance(self, user_id, question_id, answer, correct):
        """
        Record the student's performance for a particular question.
        """
        print(f"[DEBUG] Recording performance: user_id={user_id}, question_id={question_id}, correct={correct}")
        self.cursor.execute('''
            INSERT INTO student_performance (user_id, question_id, answer, correct)
            VALUES (?, ?, ?, ?)
        ''', (user_id, question_id, answer, correct))
        self.connection.commit()

    def get_student_performance(self, user_id):
        self.cursor.execute('''
            SELECT q.question, p.answer, p.correct 
            FROM student_performance p
            JOIN questions q ON p.question_id = q.id
            WHERE p.user_id = ?
        ''', (user_id,))
        return self.cursor.fetchall()

    def get_student_question_details(self, user_id):
        """
        Get details of which questions the student got correct or incorrect.
        """
        self.cursor.execute('''
            SELECT q.question, p.answer, p.correct
            FROM student_performance p
            JOIN questions q ON p.question_id = q.id
            WHERE p.user_id = ?
        ''', (user_id,))
        return self.cursor.fetchall()

    def get_all_students_performance(self):
        """
        Retrieve all students and their correct/incorrect answer counts.
        """
        self.cursor.execute('''
            SELECT u.username,
                   COALESCE(SUM(CASE WHEN p.correct = 1 THEN 1 ELSE 0 END), 0) AS correct_answers,
                   COALESCE(SUM(CASE WHEN p.correct = 0 THEN 1 ELSE 0 END), 0) AS incorrect_answers
            FROM users u
            LEFT JOIN student_performance p ON u.id = p.user_id
            WHERE u.role = 'student'
            GROUP BY u.id
        ''')
        results = self.cursor.fetchall()
        print(f"[DEBUG] Retrieved student performance: {results}")
        return results

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

    def delete_student(self, username):
        """
        Delete a student account permanently.
        """
        self.cursor.execute("DELETE FROM users WHERE username = ? AND role = 'student'", (username,))
        self.connection.commit()

    def close(self):
        self.connection.close()


