import pygame

class Fighter:
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):# y and y is the location at which characters are displayed, data is a tuple containing 3 things. data[0] (size): The size of each frame in the fighter’s animation in spritesheet, this is different for all characters. data[1] (image_scale): How much the sprite should be scaled up or down when displayed, currently im not 100% sure about this. data[2] (offset): Offset values to correct the position when rendering the sprite. Unsure about this too, figured out values by trial and error

        # Initialize basic fighter properties
        self.player = player  # Player number (1 or 2), stores player number
        self.size = data[0]  # Size of each frame in the sprite sheet
        self.image_scale = data[1]  # Scale factor for the character's image
        self.offset = data[2]  # Offset for drawing the image correctly (to fix positioning issues).    self.size, self.image_scale, and self.offset: These define how big the fighter’s sprite is, how much to scale it, and how to adjust its position when drawn.
        self.flip = flip #This boolean tracks whether the sprite should be flipped to face the opposite direction to face the opponent
        self.animation_list = self.load_images(sprite_sheet, animation_steps) # Load the character's animation frames from the sprite sheet. self.animation_list will store these animations as a list of lists, where each sub-list corresponds to an action.
        self.action = 0  # Tracks the current action. this will change constantly from player input
        self.frame_index = 0  # The current frame of the animation being displayed
        self.image = self.animation_list[self.action][self.frame_index]  # holds the current frame image being displayed
        self.update_time = pygame.time.get_ticks()  # Timer to control animation speed. Tracks the time passed since the last frame update. This controls how fast the animation plays.
        self.rect = pygame.Rect((x, y, 80, 180))  # Rectangle size is constant, but can be adjusted. Creates a rectangle for the fighter's position and size (used for collision detection)
        self.vel_y = 0  # Vertical velocity (used for jumping)

        # Flags to manage movement states
        self.running = False  # Whether the fighter is running
        self.backing = False  # Whether the fighter is moving backward
        self.blocking = False  # Whether the fighter is blocking
        self.ducking_block = False  # Whether the fighter is blocking while ducking
        self.ducking = False  # Whether the fighter is ducking
        self.jump = False  # Whether the fighter is in the air (jumping)

        # Flags and variables for attacking
        self.attacking = False  # Whether the fighter is currently attacking
        self.attack_type = 0  # Which type of attack the fighter is using
        self.attack_cooldown = 0  # Cooldown timer to prevent spamming attacks
        self.attack_sound = sound  # Sound effect to play when an attack happens

        # Health and status flags
        self.hit = False  # Whether the fighter has been hit
        self.health = 100  # The fighter's health (starts at 100)
        self.alive = True  # Whether the fighter is still alive (health > 0)
        self.attack_applied = False  # Tracks whether attack damage has already been applied
        # Animation speed (controls how fast animations play)
        self.animation_speed = 150  # Default animation speed (in milliseconds)

    def load_images(self, sprite_sheet, animation_steps):
        """Load all the animation frames from the sprite sheet."""
        animation_list = []  #This list will hold all the animations for the fighters
        for y, animation in enumerate(animation_steps):  # Loop through each row index in the sprite sheet. each index of the specificic pixels stated in the character files has a seperate animation
            temp_img_list = []  # Temporarily holds the frames for the current animation
            for x in range(animation):  # Loops through the frames in the current row (x indexes each frame horizontally, unlike y).
                # Extract each frame using subsurface
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size) # Extracts a single frame from the sprite sheet using subsurface(), which takes a rectangular area starting at (x * self.size, y * self.size), different for each character. the x and  are stated in character files
                # Scale the frame image to the appropriate size
                temp_img = pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale))#Resizes the frame using the scale factor defined in image_scale
                temp_img_list.append(temp_img)  # Add the frame to the temp list
            animation_list.append(temp_img_list)  # Once all frames for the current action are loaded, they are added to animation_list
        return animation_list  # Return the complete animation list (all actions and frames)

    def move(self, screen_width, screen_height, surface, target, round_over, keys, round_timer, opponent_health): # Dimensions of the game window to keep the fighter inside the screen, surface (screen) where the fighter will be drawn, target: The opponent fighter, round_over: Boolean flag indicating if the current round has ended, keys: Tracks which keys are pressed, round_timer: Tracks the remaining time in the current round, opponent_health: The health of the opponent.
        """Handles fighter movement, jumping, attacking, and boundary checks."""
        # Define constants for movement and gravity
        SPEED = 10  # Movement speed for walking or running
        GRAVITY = 2  # Constant gravity value for the fighter's jump and fall

        # Initialize movement changes (displace ment x for horizontal, displacement y for vertical movement)
        dx = 0
        dy = 0
        # These flags are reset every frame to ensure that movement states are re-evaluated based on player input
        self.running = False
        self.backing = False
        self.ducking_block = False
        self.attack_type = 0  # Reset attack type unless a new attack happens

        # If the fighter is not currently attacking, alive, and the round isn't over, handle inputs
        if not self.attacking and self.alive and not round_over and not self.hit: # This checks if the fighter is allowed to move or attack. The fighter cannot move if they are attacking, dead, the round is over, or they’ve been hit.
            if self.player == 1:
                # Handle Player 1's movement and actions
                dx, dy = self.handle_player_one_movement(keys, target, dx, dy)
            elif self.player == 2:
                # Handle Player 2's movement and actions
                dx, dy = self.handle_player_two_movement(keys, target, dx, dy)
                # separate due to different controls

        # Apply gravity to make the fighter fall when jumping
        self.vel_y += GRAVITY# A positive self.vel_y value means the fighter is moving downward. Gravity (GRAVITY = 2): This is a constant force that pulls the fighter downwards. Each frame, gravity adds to self.vel_y, making the fighter fall faster over time, simulating real-world gravity. the y value here is -30 - you will see this when looking at player 1 and 2 controls, gravity is set to 2 and so will increment the y value until the y value goes to 0 and then positive to make the fighter fall back down until to the floor faster as the value is incremented further
        dy += self.vel_y

        # Ensure the fighter doesn't go out of screen bounds
        dx, dy = self.handle_screen_bounds(dx, dy, screen_width, screen_height)

        # Flip the fighter image based on the position of the target (whether facing left or right)
        self.flip = target.rect.centerx < self.rect.centerx #target.rect.centerx: The x-coordinate of the opponent’s (target’s) center. self.flip is a boolean that determines whether the fighter’s image should be flipped horizontally

        # Reduce the attack cooldown timer each frame
        if self.attack_cooldown > 0:# to prevent  attacks spamming
            self.attack_cooldown -= 1 #  Each frame, the cooldown value is decreased by 1 until it reaches 0. When self.attack_cooldown == 0, the fighter can attack again. Until then, attacks are disabled

        # Update the fighter's position based on the calculated movement (dx, dy)
        self.rect.x += dx
        self.rect.y += dy

        # Call the update method to handle animation and attacks
        self.update(round_timer, opponent_health)

    def handle_player_one_movement(self, keys, target, dx, dy):
        """Handle movement and attack input for Player 1."""
        SPEED = 10  # Speed at which Player 1 moves
        # Blocking logic: If 'E' is pressed, the player blocks
        if keys[pygame.K_e]:
            self.blocking = True
        else:
            self.blocking = False

        # If blocking, set block animation, otherwise check for other actions
        if self.blocking:
            self.update_action(8)  # Block animation is at index 8
        else:
            # Moving left
            if keys[pygame.K_a]:
                dx = -SPEED
                self.running = True#animation for going forward
                self.backing = False #animation for going backwards
            # Moving right
            if keys[pygame.K_d]:
                dx = SPEED
                self.running = True
                self.backing = False
            # Jumping
            if keys[pygame.K_w] and not self.jump:
                self.vel_y = -30  # Set velocity for jump, explained in another section
                self.jump = True
            # Attacking with 'R' or 'T'
            if keys[pygame.K_r] or keys[pygame.K_t]:
                self.attack_type = self.determine_attack_type(keys, pygame.K_r, pygame.K_t, 1, 2, 5)
                self.attack(target)
            # Ducking
            if keys[pygame.K_s]:
                self.ducking = True
            else:
                self.ducking = False
            # Ducking and attacking
            if self.ducking and (keys[pygame.K_r] or keys[pygame.K_t]):
                self.attack_type = self.determine_attack_type(keys, pygame.K_r, pygame.K_t, 3, 4, 6)
            # Combo attack with 'C'
            if keys[pygame.K_c]:
                if self.ducking:
                    self.attack_type = 6  # Ducking combo attack
                else:
                    self.attack_type = 5  # Standing combo attack
                self.attack(target)

            # Determine if backing (moving away from the target)
            if self.running and target.rect.centerx < self.rect.centerx and dx > 0:
                self.running = False
                self.backing = True
            if self.running and target.rect.centerx > self.rect.centerx and dx < 0:
                self.running = False
                self.backing = True
        return dx, dy

    def handle_player_two_movement(self, keys, target, dx, dy):
        """Handle movement and attack input for Player 2."""
        SPEED = 10  # Speed for Player 2's movement
        # Blocking logic: Player 2 blocks with 'I'
        if keys[pygame.K_i]:
            self.blocking = True
        else:
            self.blocking = False

        # If blocking, set block animation
        if self.blocking:
            self.update_action(8)  # Block animation is at index 8
        else:
            # Moving left
            if keys[pygame.K_LEFT]:
                dx = -SPEED
                self.running = True
                self.backing = False
            # Moving right
            if keys[pygame.K_RIGHT]:
                dx = SPEED
                self.running = True
                self.backing = False
            # Jumping
            if keys[pygame.K_UP] and not self.jump:
                self.vel_y = -30  # Set velocity for jump
                self.jump = True # so the fighter cant jump infinite times
            # Attacking with 'Y' or 'U'
            if keys[pygame.K_y] or keys[pygame.K_u]:
                self.attack_type = self.determine_attack_type(keys, pygame.K_y, pygame.K_u, 1, 2, 5)
                self.attack(target)
            # Ducking
            if keys[pygame.K_DOWN]:
                self.ducking = True
            else:
                self.ducking = False
            # Ducking and attacking
            if self.ducking and (keys[pygame.K_y] or keys[pygame.K_u]):
                self.attack_type = self.determine_attack_type(keys, pygame.K_y, pygame.K_u, 3, 4, 6)
            # Combo attack with 'Right Shift'
            if keys[pygame.K_RSHIFT]:
                if self.ducking:
                    self.attack_type = 6  # Ducking combo attack
                else:
                    self.attack_type = 5  # Standing combo attack
                self.attack(target)

            # Determine if backing (moving away from the target)
            if self.running and target.rect.centerx < self.rect.centerx and dx > 0:
                self.running = False
                self.backing = True
            if self.running and target.rect.centerx > self.rect.centerx and dx < 0:
                self.running = False
                self.backing = True
        return dx, dy

    def determine_attack_type(self, keys, attack_key1, attack_key2, type1, type2, combo_type):
        """Determine which attack type to use based on the keys pressed."""
        # If both attack keys are pressed, it's a combo attack
        if keys[attack_key1] and keys[attack_key2]:
            return combo_type
        # If only the first attack key is pressed, it's attack type 1
        if keys[attack_key1]:
            return type1
        # If only the second attack key is pressed, it's attack type 2
        if keys[attack_key2]:
            return type2
        return 0  # No attack

    def handle_screen_bounds(self, dx, dy, screen_width, screen_height):
        """Ensure the fighter stays within screen boundaries."""
        # Check horizontal boundaries (left and right)
        if self.rect.left + dx < 0: #self.rect.left + dx < 0: This checks if the fighter’s left edge would move past the left boundary (x=0)
            dx = -self.rect.left  # Prevent moving off the left edge
        if self.rect.right + dx > screen_width:#self.rect.right + dx > screen_width: This checks if the fighter’s right edge would move past the right boundary. havent hard coded the most right edge
            dx = screen_width - self.rect.right  # Prevent moving off the right edge

        # Check vertical boundaries (top and bottom)
        if self.rect.bottom + dy > screen_height - 110:  #This checks if the fighter’s bottom edge of rectangle is going below the ground. The ground level is set 110 pixels above the bottom of the screen.
            self.vel_y = 0  # Reset vertical velocity when on the ground so fighter doesnt fall below ground when gravity pulls him down
            self.jump = False  # Allow jumping again when on the ground
            dy = screen_height - 110 - self.rect.bottom  # Prevent falling through the ground
        return dx, dy  # Return the adjusted movement values

    def attack(self, target):
        """Perform an attack on the target."""
        if self.attack_cooldown == 0:  # The fighter can only attack if the cooldown is 0 (self.attack_cooldown == 0). This prevents attack spamming
            self.attacking = True  # Set the attacking flag
            self.attack_sound.play()  # Play the attack sound
            self.attack_frame = 0  # Track the frame at which the attack happens (second to last frame)
            self.attack_target = target  # The target being attacked
            self.attack_applied = False  # Reset the attack applied flag

    def update_action(self, new_action):
        """Update the current action to a new one (e.g., walking, attacking, etc.)."""
        if new_action != self.action:  # Only update if the action has changed
            self.action = new_action  # Set the new action
            self.frame_index = 0  # Reset the animation frame to the beginning
            self.update_time = pygame.time.get_ticks()  # Reset the time for controlling animation speed

    def update(self, round_timer, opponent_health):
        """Update the fighter's animations, actions, and cooldowns."""
        # Update the current image to the correct frame of the current action
        self.image = self.animation_list[self.action][self.frame_index] #This contains all the animation frames for the fighter, organized by vertical index. self.action: Represents the current action the fighter is performing. self.frame_index: Indicates the current frame of the current action
#Here, self.image is updated to the current frame in the animation sequence. This ensures the correct frame is displayed as the action (like attacking or walking) progresses

        # Handle animation frame updates
        if pygame.time.get_ticks() - self.update_time > self.animation_speed:  # pygame.time.get_ticks(): This function returns the time (in milliseconds) since the game started. checks if enough time has passed to proceed to the next frame. Controls how quickly the animation progresses (in milliseconds). Lower values result in faster animations
            self.frame_index += 1  # Move to the next frame
            self.update_time = pygame.time.get_ticks()   # Tracks the last time the frame was updated.
#Every frame, this block checks if enough time has passed since the last frame update (based on self.animation_speed). If the time difference exceeds self.animation_speed, the animation advances to the next frame by incrementing self.frame_index. self.update_time is then reset to the current time, ensuring that the animation speed remains consistent

        # If the animation has finished its frames, reset or continue based on action
        if self.frame_index >= len(self.animation_list[self.action]): # This checks if the animation has reached the last frame. this is a list of all frames of the current animation. len(self.animation_list[self.action]) returns the total number of frames for the current action. because the frame increments from 0, the last frame is len -1.for example, 10 frames is 0 to 9. so len-1 gives the 9th frame
            if not self.alive:  # If the fighter is dead, freeze on the last frame, which is the animation when dying, so he lies on the ground
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:  # Otherwise, reset the animation
                self.frame_index = 0#The animation resets to frame 0, so the animation will loop continuously as 0 index has the idle animation
                if self.action in [3, 4, 12, 13, 14, 15]:  # Attacking actions. each is an index in the sprite sheet
                    self.attacking = False  # End the attack to not loop atk animation
                    self.attack_cooldown = 20  # Set attack cooldown so the fighter cant spam attacks
                if self.action == 5:  # Hit taken animation
                    self.hit = False  # Reset hit flag
                    self.attacking = False  # cant attack while being hit
                    self.attack_cooldown = 20
                # Handle other special actions like ducking block or being hit
                if self.action in [10, 11, 16]:  # Ducking block, hit taken while ducking, ducking itself
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

        # Apply damage during the appropriate attack frame
        if self.attacking and not self.attack_applied and self.frame_index == len(self.animation_list[self.action]) - 2:#self.attacking: The fighter must be in an attacking state for the damage to be applied, not self.attack_applied: This ensures that damage is applied only once per attack. Once damage is dealt, self.attack_applied is set to True to prevent it from being applied again during the same attack, self.frame_index == len(self.animation_list[self.action]) - 2 to make sure the damage is applied to the enemy when on the 2nd last frame of the attacking animation for more realistic damage timing
            # Create a rectangle for the attack hitbox
            attacking_rect = pygame.Rect(
                self.rect.centerx - (2 * self.rect.width * self.flip),  # Position the hitbox based on fighter direction, will go left is facing left, rigt if facing right
                self.rect.y, 2 * self.rect.width, self.rect.height)  # Set the hitbox size to twice the fighter's width to the direction he is facing
            # Check if the attack hitbox collides with the target's hitbox and they're not blocking
            if attacking_rect.colliderect(self.attack_target.rect) and not self.attack_target.blocking: # cant attack while blocking. colliderect(): This function checks if the attack rectangle overlaps (collides) with the opponent’s hitbox
                self.attack_target.health -= 10  # Reduce target's health
                self.attack_target.hit = True  # The self.attack_target.hit flag is set to True, which triggers the opponent’s hit taken animation.
            self.attack_applied = True  # After the damage is applied, self.attack_applied is set to True to ensure that the attack doesn’t repeatedly apply damage during the same animation cycle

    def draw(self, surface):#surface: This parameter refers to the screen or any other surface where the fighter will be drawn. In this case, surface is the game window where all game objects are drawn
        """Draw the fighter on the screen."""
        # Flip the image based on the fighter's direction (facing left or right)
        img = pygame.transform.flip(self.image, self.flip, False) #self.image: This is the current frame of the fighter’s animation (the actual sprite that represents the fighter at a given moment). self.flip: This boolean flag determines if the image should be flipped horizontally. If True, the image will be flipped, and if False the image won’t be flipped. False: This third argument controls vertical flipping, which is irrelevant
        # Blit (draw) the image on the screen, with the correct offset for positioning
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale),
                           self.rect.y - (self.offset[1] * self.image_scale)))# this method is how Pygame draws one image (like the fighter) onto another surface (like the screen). img: This is the image of the fighter, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)): This tuple represents the position where the image should be drawn on the screen.
#self.rect.x: The x-coordinate of the fighter's rectangle (hitbox), representing the fighter’s current horizontal position on the screen
#self.rect.y: The y-coordinate of the fighter's rectangle, representing the fighter’s vertical position on the screen
#self.offset: This is a tuple (x_offset, y_offset) that helps adjust the positioning of the sprite relative to its hitbox.
#self.offset[0]: Horizontal offset (adjusts how far the sprite is shifted left or right).
#self.offset[1]: Vertical offset (adjusts how far the sprite is shifted up or down)
#self.image_scale: The scaling factor for the fighter’s sprite (e.g., 2x, 3x). This ensures that the offset is scaled correctly when the image is scaled so it doesnt look abnomormal
#The offset corrects any alignment issues, making sure the image is properly positioned relative to the hitbox. The offsets are multiplied by the image scale to ensure that any shifts in position are proportional to the size of the scaled sprite. (ask teacher for help on offset undertsnading)