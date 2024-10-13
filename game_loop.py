import pygame
import os
from geese import Geese
from jin import Jin
from pygame import mixer


def game_loop(self):
    try:
        while self.run:
            self.clock.tick(self.FPS)

            # Main Menu State
            if self.game_state == "menu":
                self.menu.draw_menu(self.rounds_available)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.run = False
                    self.menu.handle_events(event, self.rounds_available)

                if self.menu.is_selection_complete():
                    if self.menu.selected_mode == "Player vs Player":
                        if self.rounds_available >= 1:  # Require at least 1 full round
                            self.rounds_available -= 1  # Deduct one round unit when starting
                            self.game_state = "character_selection"
                        else:
                            print("Not enough rounds available!")
                    elif self.menu.selected_mode == "Teacher Login":
                        self.handle_teacher_login()
                    elif self.menu.selected_mode == "Student Login":
                        logged_in = self.student_login(self.screen, self.score_font)  # Handle student login
                        if logged_in:
                            print(f"[DEBUG] game_loop: Student logged in with user_id={self.logged_in_student}")
                    elif self.menu.selected_mode == "Question Time":
                        print(f"[DEBUG] game_loop: Starting Question Time for user_id={self.logged_in_student}")
                        self.handle_question_time()

                self.menu.selected_mode = None  # Reset menu selection after handling

            # Character Selection State
            elif self.game_state == "character_selection":
                self.char_select.draw_selection()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.run = False
                    self.char_select.handle_events(event)

                if self.char_select.is_selection_complete():
                    self.game_state = "stage_selection"

            # Stage Selection State
            elif self.game_state == "stage_selection":
                self.stage_select.draw_selection()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.run = False
                    self.stage_select.handle_events(event)

                if self.stage_select.is_selection_complete():
                    selected_stage = self.stage_select.determine_stage()
                    self.load_stage_music(selected_stage)
                    self.reset_fighters(self.char_select.p1_selection, self.char_select.p2_selection)
                    self.game_state = "fighting"
                    self.selected_bg = self.bg_images[selected_stage]

                    # Reset intro countdown
                    self.intro_count = 2
                    self.last_count_update = pygame.time.get_ticks()
                    self.round_start_time = 0

            # Fighting State
            elif self.game_state == "fighting":
                if self.paused:
                    self.pause_menu.draw_menu(self.rounds_available)
                    for event in pygame.event.get():
                        action = self.pause_menu.handle_events(event)
                        if action == "resume":
                            self.paused = False
                        elif action == "selection_screen":
                            self.game_state = "menu"
                            self.paused = False
                            self.reset_menu()
                            self.char_select.p1_selection = None
                            self.char_select.p2_selection = None
                            self.char_select.p1_index = 0
                            self.char_select.p2_index = 0
                            self.stage_select.p1_selection = None
                            self.stage_select.p2_selection = None
                            self.stage_select.p1_index = 0
                            self.stage_select.p2_index = 0
                        elif action == "quit":
                            self.run = False
                        else:
                            self.paused = True
                else:
                    keys = pygame.key.get_pressed()
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.paused = True

                    self.draw_bg(self.selected_bg)
                    self.draw_health_bar(self.fighter_1.health, 20, 20)
                    self.draw_health_bar(self.fighter_2.health, 580, 20)
                    self.draw_text(f"P1: {self.score[0]}", self.score_font, self.RED, 20, 60)
                    self.draw_text(f"P2: {self.score[1]}", self.score_font, self.RED, 580, 60)

                    # Display remaining rounds at the bottom-left corner
                    self.draw_text(f"Rounds Left: {self.rounds_available}", self.score_font, self.WHITE, 20, 550)

                    if self.intro_count > 0:
                        # Intro animations for fighters (Geese or others)
                        if isinstance(self.fighter_1, Geese):
                            if self.fighter_1.intro_played:
                                self.fighter_1.update_action(0)
                            else:
                                self.fighter_1.play_intro()
                        if isinstance(self.fighter_2, Geese):
                            if self.fighter_2.intro_played:
                                self.fighter_2.update_action(0)
                            else:
                                self.fighter_2.play_intro()

                        self.fighter_1.update(0, self.fighter_2.health)
                        self.fighter_2.update(0, self.fighter_1.health)

                        self.fighter_1.draw(self.screen)
                        self.fighter_2.draw(self.screen)
                        self.draw_text(str(self.intro_count), self.count_font, self.RED, self.SCREEN_WIDTH // 2,
                                       self.SCREEN_HEIGHT // 3)
                        if pygame.time.get_ticks() - self.last_count_update >= 1000:
                            self.intro_count -= 1
                            self.last_count_update = pygame.time.get_ticks()
                            if self.intro_count == 0:
                                self.round_start_time = pygame.time.get_ticks()  # Start the round timer
                                # Reset animation speed for the first round
                                if isinstance(self.fighter_1, Geese):
                                    self.fighter_1.animation_speed = self.fighter_1.standard_animation_speed
                                if isinstance(self.fighter_2, Geese):
                                    self.fighter_2.animation_speed = self.fighter_2.standard_animation_speed
                    else:
                        # Update the round timer
                        time_left = self.round_timer - (pygame.time.get_ticks() - self.round_start_time)
                        if time_left < 0:
                            time_left = 0
                        minutes = time_left // 60000
                        seconds = (time_left % 60000) // 1000
                        self.draw_text(f"{minutes:02}:{seconds:02}", self.score_font, self.WHITE,
                                       self.SCREEN_WIDTH // 2 - 30, 20)

                        self.fighter_1.move(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.screen, self.fighter_2,
                                            self.round_over, keys, time_left, self.fighter_2.health)
                        self.fighter_2.move(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.screen, self.fighter_1,
                                            self.round_over, keys, time_left, self.fighter_1.health)

                        self.fighter_1.update(time_left, self.fighter_2.health)
                        self.fighter_2.update(time_left, self.fighter_1.health)
                        self.fighter_1.draw(self.screen)
                        self.fighter_2.draw(self.screen)

                        if not self.round_over:
                            # Handle end of round scenarios (fighter death or time up)
                            if not self.fighter_1.alive:
                                self.score[1] += 1
                                self.round_over = True
                                self.round_over_time = pygame.time.get_ticks()
                                if isinstance(self.fighter_2, Geese):
                                    self.fighter_2.play_win_pose()
                                    self.fighter_2.win_pose_completed = True
                            elif not self.fighter_2.alive:
                                self.score[0] += 1
                                self.round_over = True
                                self.round_over_time = pygame.time.get_ticks()
                                if isinstance(self.fighter_1, Geese):
                                    self.fighter_1.play_win_pose()
                                    self.fighter_1.win_pose_completed = True
                            elif time_left <= 0:
                                self.round_over = True
                                self.round_over_time = pygame.time.get_ticks()
                                if self.fighter_1.health > self.fighter_2.health:
                                    self.score[0] += 1
                                    if isinstance(self.fighter_1, Geese):
                                        self.fighter_1.play_win_pose()
                                elif self.fighter_2.health > self.fighter_1.health:
                                    self.score[1] += 1
                                    if isinstance(self.fighter_2, Geese):
                                        self.fighter_2.play_win_pose()
                                else:
                                    if isinstance(self.fighter_1,
                                                  Geese) and self.fighter_1.health <= self.fighter_2.health:
                                        self.fighter_1.play_round_over_loss_animation()
                                    if isinstance(self.fighter_2,
                                                  Geese) and self.fighter_2.health <= self.fighter_1.health:
                                        self.fighter_2.play_round_over_loss_animation()
                        else:
                            # Handle post-round logic and check if there are rounds available
                            if self.rounds_available > 0:
                                # Reset the round if there are rounds left
                                if pygame.time.get_ticks() - self.round_over_time > self.ROUND_OVER_COOLDOWN + self.reset_delay:
                                    self.rounds_available -= 1  # Deduct 1 round after each fight
                                    self.round_over = False
                                    self.intro_count = 2  # Reset intro countdown for new round
                                    self.round_start_time = 0  # Reset the round timer
                                    self.reset_fighters(self.char_select.p1_selection,
                                                        self.char_select.p2_selection)
                                    # Reset win pose flags for new round
                                    if isinstance(self.fighter_1, Geese):
                                        self.fighter_1.win_pose_played = False
                                        self.fighter_1.win_pose_completed = False
                                    if isinstance(self.fighter_2, Geese):
                                        self.fighter_2.win_pose_played = False
                                        self.fighter_2.win_pose_completed = False
                            else:
                                # Show "study more" message when no rounds are left
                                self.draw_text("Study more to earn more round units.", self.score_font, self.RED,
                                               self.SCREEN_WIDTH // 2 - 200, self.SCREEN_HEIGHT // 2)
                                self.draw_text("Press Enter to return to menu.", self.score_font, self.RED,
                                               self.SCREEN_WIDTH // 2 - 200, self.SCREEN_HEIGHT // 2 + 50)
                                pygame.display.update()

                                keys = pygame.key.get_pressed()
                                if keys[pygame.K_RETURN]:
                                    self.game_state = "menu"
                                    self.reset_menu()

                    self.handle_fighting_events()

            # Teacher Options State
            elif self.game_state == "teacher_options":
                print("[DEBUG] In teacher options state.")
                self.handle_teacher_options()

            pygame.display.update()

    finally:
        self.cleanup()  # Make sure correct_answers.txt is deleted on exit

    pygame.quit()

