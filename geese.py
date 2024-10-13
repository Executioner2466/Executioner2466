# geese.py
import pygame
from characters import Fighter

class Geese(Fighter):
    def __init__(self, player, x, y, flip, sound):
        # Initialize Geese-specific attributes
        data = [140, 3, [85, 30]]  # Health, speed, and size
        sprite_sheet = pygame.image.load("assets/images/geese/Sprites/geese.png").convert_alpha()
        # Define the number of frames for each animation (index corresponds to action number)
        animation_steps = [3, 3, 1, 3, 3, 2, 6, 3, 1, 1, 1, 2, 1, 2, 3, 5, 5, 2, 7, 6]
        super().__init__(player, x, y, flip, data, sprite_sheet, animation_steps, sound)
        self.intro_played = False  # Track if the intro has been played
        self.intro_counter = 0  # Counter for intro animation loops
        self.standard_animation_speed = 150  # Standard animation speed
        self.animation_speed = self.standard_animation_speed  # Initialize animation speed
        self.round_over_loss_played = False  # Track if the round-over loss animation has been played
        self.win_pose_played = False  # Track if the win pose animation has started
        self.win_pose_completed = False  # Track if the win pose animation has completed

    def update(self, round_timer, opponent_health):
        """
        Update Geese's actions based on current state.
        """
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(16 if self.ducking else 6)  # Death animation
        elif self.hit:
            self.update_action(11 if self.ducking else 5)  # Hit animation
        elif self.attacking:
            self.handle_attacks()
        elif self.jump:
            self.update_action(2)  # Jump animation
        elif self.running:
            self.update_action(1)  # Run animation
        elif self.backing:
            self.update_action(7)  # Backing animation
        elif self.blocking:
            self.update_action(10 if self.ducking else 8)  # Block animation
        elif self.ducking:
            self.update_action(9)  # Duck animation
        elif not self.intro_played:
            self.play_intro()
        elif round_timer <= 0 and (self.health <= opponent_health):
            self.play_round_over_loss_animation()
        elif self.win_pose_completed:
            # Keep Geese in the final frame of the win pose animation
            self.frame_index = len(self.animation_list[18]) - 1
            self.update_action(18)  # Win pose animation
        elif self.win_pose_played:
            self.play_win_pose()
        else:
            self.update_action(0)  # Idle animation

        # Call the parent class update method
        super().update(round_timer, opponent_health)

    def handle_attacks(self):
        """
        Handle attack animations based on the attack type.
        """
        if self.attack_type == 1:
            self.update_action(3)  # Attack 1 animation
        elif self.attack_type == 2:
            self.update_action(4)  # Attack 2 animation
        elif self.attack_type == 3:
            self.update_action(12)  # Duck attack 1 animation
        elif self.attack_type == 4:
            self.update_action(13)  # Duck attack 2 animation
        elif self.attack_type == 5:
            self.update_action(15)  # Combo attack animation
        elif self.attack_type == 6:
            self.update_action(14)  # Combo duck attack animation

    def play_intro(self):
        """
        Play the intro animation for Geese. The animation speed is intentionally slowed down.
        """
        if self.action != 17:
            self.update_action(17)  # Intro animation
            self.animation_speed = 400  # Slow down the intro animation

        # Update the animation frame
        if pygame.time.get_ticks() - self.update_time > self.animation_speed:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        # Check if the intro animation has completed its cycles
        if self.frame_index >= len(self.animation_list[17]):
            self.intro_counter += 1
            self.frame_index = 0  # Reset the frame index for another cycle

            # After two complete cycles, mark the intro as played
            if self.intro_counter >= 2:
                self.intro_played = True
                self.animation_speed = self.standard_animation_speed  # Reset animation speed to normal
                self.update_action(0)  # Switch to idle animation

    def play_win_pose(self):
        """
        Play the win pose animation for Geese.
        """
        if not self.win_pose_played:
            self.update_action(18)  # Win animation
            self.animation_speed = 300  # Slow down the win animation
            self.win_pose_played = True  # Mark the win pose as started

        # Update the animation frame
        if pygame.time.get_ticks() - self.update_time > self.animation_speed:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        # Check if the win pose animation has completed
        if self.frame_index >= len(self.animation_list[18]):
            self.frame_index = len(self.animation_list[18]) - 1  # Hold the last frame
            self.win_pose_completed = True  # Mark the win pose as completed

    def play_round_over_loss_animation(self):
        """
        Play the animation for losing at the end of a round.
        """
        if self.action != 19:
            self.update_action(19)  # Loss animation
            self.animation_speed = 300  # Slow down the loss animation

        # Update the animation frame
        if pygame.time.get_ticks() - self.update_time > self.animation_speed:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        # Check if the loss animation has completed
        if self.frame_index >= len(self.animation_list[19]):
            self.frame_index = len(self.animation_list[19]) - 1  # Hold the last frame
            self.round_over_loss_played = True  # Mark the loss animation as played
