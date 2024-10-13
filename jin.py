import pygame
from characters import Fighter

class Jin(Fighter):
    def __init__(self, player, x, y, flip, sound):
        # Initialize jin-specific data
        data = [140, 3.5, [85, 30]]
        sprite_sheet = pygame.image.load("assets/images/jin/Sprites/jin.png").convert_alpha()
        animation_steps = [4, 3, 2, 10, 3, 2, 6, 3, 1, 1, 1, 1, 3, 2, 2, 6, 6]
        super().__init__(player, x, y, flip, data, sprite_sheet, animation_steps, sound)

    def update(self, round_timer, opponent_health):
        # Update jin-specific actions
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
        else:
            self.update_action(0)  # Idle animation

        # Update the fighter (animation handling and position)
        super().update(round_timer, opponent_health)

    def handle_attacks(self):
        # Handle different attack animations
        if self.attack_type == 1:
            self.update_action(3)  # Attack 1 animation
        elif self.attack_type == 2:
            self.update_action(4)  # Attack 2 animation
        elif self.attack_type == 3:
            self.update_action(12) # Duck attack 1 animation
        elif self.attack_type == 4:
            self.update_action(13) # Duck attack 2 animation
        elif self.attack_type == 5:
            self.update_action(15) # Combo attack animation
        elif self.attack_type == 6:
            self.update_action(14) # Combo duck attack animation
