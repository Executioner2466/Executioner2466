import pygame
import random

class StageSelection:
    def __init__(self, screen):
        # Initialize stage selection properties
        self.screen = screen
        self.font = pygame.font.Font(r"assets/fonts/turok.ttf", 30)
        self.stages = ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Random"]
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
        # Draw the stage selection screen
        self.screen.fill((0, 0, 0))
        self.draw_text("Player 1 Stage Selection", 250, 100, color=(255, 255, 255), center=True)
        self.draw_text("Player 2 Stage Selection", 750, 100, color=(255, 255, 255), center=True)

        for i, stage in enumerate(self.stages):
            p1_color = (0, 0, 139) if i == self.p1_index else (255, 255, 255)
            p2_color = (139, 0, 0) if i == self.p2_index else (255, 255, 255)
            self.draw_text(stage, 250, 200 + i * 50, color=p1_color, center=True)
            self.draw_text(stage, 750, 200 + i * 50, color=p2_color, center=True)

    def handle_events(self, event):
        # Handle keyboard events for stage selections
        if event.type == pygame.KEYDOWN:
            # Player 1 controls
            if event.key == pygame.K_w:
                self.p1_index = (self.p1_index - 1) % len(self.stages)
            elif event.key == pygame.K_s:
                self.p1_index = (self.p1_index + 1) % len(self.stages)
            elif event.key == pygame.K_TAB:
                self.p1_selection = self.stages[self.p1_index]

            # Player 2 controls
            if event.key == pygame.K_UP:
                self.p2_index = (self.p2_index - 1) % len(self.stages)
            elif event.key == pygame.K_DOWN:
                self.p2_index = (self.p2_index + 1) % len(self.stages)
            elif event.key == pygame.K_RETURN:
                self.p2_selection = self.stages[self.p2_index]

    def is_selection_complete(self):
        # Check if both players have made their selections
        return self.p1_selection is not None and self.p2_selection is not None

    def determine_stage(self):
        # Determine the final stage based on player selections
        stage_mapping = {
            "Stage 1": "stage1",
            "Stage 2": "stage2",
            "Stage 3": "stage3",
            "Stage 4": "stage4",
        }

        # If one player selects random and the other selects a specific stage, use the specific stage
        if self.p1_selection == "Random" and self.p2_selection in stage_mapping:
            return stage_mapping[self.p2_selection]
        if self.p2_selection == "Random" and self.p1_selection in stage_mapping:
            return stage_mapping[self.p1_selection]

        # If both select random, choose a random stage
        if self.p1_selection == "Random" and self.p2_selection == "Random":
            return random.choice(list(stage_mapping.values()))

        # If both select the same stage, use that stage
        if self.p1_selection == self.p2_selection:
            return stage_mapping[self.p1_selection]

        # If they select different stages, choose randomly between their choices
        return stage_mapping[random.choice([self.p1_selection, self.p2_selection])]







