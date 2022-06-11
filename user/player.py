import os.path
import random

import pygame.image

from world.level_objects import CollideType, DroppedItem


class Player:

    # The speed, in pixels per frame, that the player moves
    VELOCITY = 2

    # Starting health of the player, and a custom event that is posted when the health changes
    HEALTH = 10
    MAX_HEALTH = HEALTH
    DAMAGE = pygame.USEREVENT + 1
    DAMAGE_EVENT = pygame.event.Event(DAMAGE)

    # The speed, in pixels per frame, that the player falls
    GRAVITY = 6

    # Dimensions of the player and placeholder spawn coordinates
    PLAYER_WIDTH, PLAYER_HEIGHT = 32, 56
    SPAWN_X, SPAWN_Y = 0, 0

    # All sprite images of the player
    PLAYER_STILL = pygame.image.load(os.path.join('assets', 'sprites', 'player', 'hero_still.png')).convert_alpha()
    PLAYER_WALK_1 = pygame.image.load(os.path.join('assets', 'sprites', 'player', 'hero_walk_1.png')).convert_alpha()
    PLAYER_WALK_2 = pygame.image.load(os.path.join('assets', 'sprites', 'player', 'hero_walk_2.png')).convert_alpha()

    PLAYER_LEFT = pygame.transform.scale(PLAYER_STILL, (PLAYER_WIDTH, PLAYER_HEIGHT))
    PLAYER_LEFT_WALK_1 = pygame.transform.scale(PLAYER_WALK_1, (PLAYER_WIDTH, PLAYER_HEIGHT))
    PLAYER_LEFT_WALK_2 = pygame.transform.scale(PLAYER_WALK_2, (PLAYER_WIDTH, PLAYER_HEIGHT))

    PLAYER_RIGHT = pygame.transform.flip(PLAYER_LEFT, True, False)
    PLAYER_RIGHT_WALK_1 = pygame.transform.flip(PLAYER_LEFT_WALK_1, True, False)
    PLAYER_RIGHT_WALK_2 = pygame.transform.flip(PLAYER_LEFT_WALK_2, True, False)

    PLAYER_LEFT_WALKING = [PLAYER_LEFT_WALK_1, PLAYER_LEFT, PLAYER_LEFT_WALK_2, PLAYER_LEFT]
    PLAYER_RIGHT_WALKING = [PLAYER_RIGHT_WALK_1, PLAYER_RIGHT, PLAYER_RIGHT_WALK_2, PLAYER_RIGHT]
    ANIMATION_SPEED = 15
    animation_frame_count = 0

    # All sound effects made by the player
    JUMP_NOISE_CHANNEL = pygame.mixer.Channel(4)
    JUMP_NOISE = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'player', 'jump.wav'))
    COLLECT_NOISE = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'player', 'collect.wav'))
    DEATH_NOISE = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'player', 'death.flac'))

    # Load images of hearts to show player health in game
    HEART_WIDTH, HEART_HEIGHT = 36, 36

    FULL_HEART_IMG = pygame.image.load(os.path.join('assets', 'textures', 'player', 'full_heart.png')).convert_alpha()
    EMPTY_HEART_IMG = pygame.image.load(os.path.join('assets', 'textures', 'player', 'empty_heart.png')).convert_alpha()

    FULL_HEART = pygame.transform.scale(FULL_HEART_IMG, (HEART_WIDTH, HEART_HEIGHT))
    EMPTY_HEART = pygame.transform.scale(EMPTY_HEART_IMG, (HEART_WIDTH, HEART_HEIGHT))

    # A rectangle to surround the player, and the current sprite being drawn
    rect: pygame.Rect
    current_img: pygame.Surface

    # A list of sounds played in a random order when damage is taken,
    # and a custom sound channel so that only one sound is played per damage tick
    DAMAGE_NOISES: list
    DAMAGE_CHANNEL = pygame.mixer.Channel(5)

    # Enum values for the player's direction
    RIGHT, LEFT, UP, DOWN = 0, 1, 2, 3

    # Variables to store the last known position of the player
    prev_pos_x: int
    prev_pos_y: int

    # The starting direction the player is moving in
    direction = (True, False, False, False)

    # Variables to store the player's jump status
    jumping = False
    jump_height = 12
    jumps = sorted([-i for i in range(jump_height + 1)])
    jump_index = 0

    # All images and variables for the player's inventory
    INVENTORY_SIZE = 2
    INVENTORY_SLOT_SIZE = INVENTORY_SLOT_WIDTH, INVENTORY_SLOT_HEIGHT = 80, 80
    INVENTORY_SLOT_IMG = pygame.image.load(os.path.join('assets', 'textures', 'player', 'inventory_slot.png')).convert_alpha()
    INVENTORY_SLOT_SELECT = pygame.image.load(os.path.join('assets', 'textures', 'player', 'inventory_select.png')).convert_alpha()
    INVENTORY_SLOT = pygame.transform.scale(INVENTORY_SLOT_IMG, INVENTORY_SLOT_SIZE)
    inventory: list
    inventory_selected_slot = 0

    nearest_grav = 0

    def __init__(self, spawn_x=0, spawn_y=0):
        self.SPAWN_X = spawn_x
        self.SPAWN_Y = spawn_y
        self.rect = pygame.Rect(self.SPAWN_X, self.SPAWN_Y, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        self.current_img = self.PLAYER_RIGHT
        self.inventory = [None, None]
        self.init_damage_sounds()

    # Load all sounds that can be played while taking damage
    def init_damage_sounds(self):
        self.DAMAGE_NOISES = []
        sound_dir = os.path.join('assets', 'sounds', 'player', 'damage')
        sound_files = [f for f in os.listdir(sound_dir)
                       if os.path.isfile(os.path.join(sound_dir, f)) and f.lower().endswith(".flac")]
        for sound in sound_files:
            self.DAMAGE_NOISES.append(pygame.mixer.Sound(os.path.join(sound_dir, sound)))

    # Return a random sound in the damage noise list
    def play_damage_sound(self):
        return random.choice(self.DAMAGE_NOISES)

    # Change the rect position of the player based on gravity and keyboard inputs
    def handle_movement(self, window, keys_pressed, level):
        self.prev_pos_x = self.rect.x
        self.prev_pos_y = self.rect.y
        x_change = 0
        y_change = 0
        grav_check = self.apply_gravity(level)
        # If the player is not jumping, apply gravity and check if they jumped
        if not self.jumping:
            if grav_check[0]:
                if grav_check[1]:
                    y_change = self.GRAVITY
                    self.nearest_grav = self.GRAVITY
                if not grav_check[1]:
                    y_change = 1
                    self.nearest_grav = 1
                self.direction = (self.direction[self.RIGHT], self.direction[self.LEFT], False, True)
            else:
                self.nearest_grav = 0
                if keys_pressed[pygame.K_SPACE]:
                    if not self.JUMP_NOISE_CHANNEL.get_busy():
                        self.JUMP_NOISE_CHANNEL.play(self.JUMP_NOISE)
                    self.jumping = True
        else:
            # Change the y position of the player gradually
            if self.jump_index < len(self.jumps) - 1:
                if not self.check_collision(level, (self.rect.x, self.rect.y + self.jumps[self.jump_index])):
                    y_change = self.jumps[self.jump_index]
                    self.direction = (self.direction[self.RIGHT], self.direction[self.LEFT], True, False)
                    self.jump_index += 1
                else:
                    self.jump_index = 0
                    self.jumping = False
            else:
                self.jump_index = 0
                self.jumping = False

        # If 'A', 'D' or the arrow keys are pressed, move the player left or right accordingly
        # Restrict movement if the player collides with objects in the level
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            if not self.check_collision(level, (self.rect.x - self.VELOCITY, self.rect.y)):
                self.direction = (False, True, False, False)
                x_change -= self.VELOCITY
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            if not self.check_collision(level, (self.rect.x + self.VELOCITY, self.rect.y)):
                self.direction = (True, False, False, False)
                x_change += self.VELOCITY

        # If the player moves 3/4 across the screen, both vertically and horizontally,
        # cancel movement and move the map instead to create a scrolling effect
        if x_change != 0:
            if self.rect.x + x_change > window.get_width() * 0.75:
                level.scroll(-self.VELOCITY, 0)
                x_change = 0
                self.prev_pos_x -= 1
            if self.rect.x + x_change < window.get_width() * 0.25:
                level.scroll(self.VELOCITY, 0)
                x_change = 0
                self.prev_pos_x += 1

        if self.rect.y + y_change < window.get_height() * 0.25:
            level.scroll(0, self.GRAVITY)
            y_change = 0
            self.prev_pos_y += self.GRAVITY
        if self.rect.y + self.rect.h + y_change > window.get_height() * 0.75:
            y_change = -self.nearest_grav
            level.scroll(0, -self.nearest_grav)
            self.prev_pos_y -= self.nearest_grav

        self.rect.x += x_change
        self.rect.y += y_change

    # Returns a tuple in form (bool, int) where the boolean indicates if the player is moving
    # If they are, the second element indicates in which direction, as an enum
    def moving(self):
        if self.prev_pos_x - self.rect.x != 0:
            if self.prev_pos_x - self.rect.x < 0:
                return True, self.RIGHT
            else:
                return True, self.LEFT
        if self.prev_pos_y - self.rect.y != 0:
            if self.prev_pos_y - self.rect.y < 0:
                return True, self.UP
            else:
                return True, self.DOWN
        return False, None

    # Returns if gravity should be applied to the Player
    def apply_gravity(self, level):
        if not self.check_collision(level, (self.rect.x, self.rect.y + self.GRAVITY)):
            return True, True
        elif not self.check_collision(level, (self.rect.x, self.rect.y + 1)):
            return True, False
        return False, False

    # Check if the Player is going to collide with a CollideType
    def check_collision(self, level, change):
        potential_rect = pygame.Rect(change[0], change[1], self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        for level_object in level.level_objects:
            if isinstance(level_object, CollideType):
                if level_object.rect.colliderect(potential_rect):
                    return True
        for npc in level.level_npc:
            if npc.rect.colliderect(potential_rect):
                return True
        return False

    # If the event passed indicates that the player took damage, alter health accordingly
    def process_event(self, event):
        if event.type == self.DAMAGE:
            if self.HEALTH + event.hp > self.MAX_HEALTH:
                self.HEALTH = self.MAX_HEALTH
                return
            self.HEALTH += event.hp

    # Post a DAMAGE event if the player's health is to be changed
    def change_hp(self, amount):
        self.DAMAGE_EVENT.hp = amount
        pygame.event.post(self.DAMAGE_EVENT)

    # Change the current image of the player if they are moving
    # The image is chosen based on how many frames the last image was shown for
    def walking_animation(self, direction, frame_list):
        per_frame = self.ANIMATION_SPEED
        if self.moving()[1] == direction:
            for index, frame in enumerate(frame_list):
                if self.animation_frame_count < per_frame * len(frame_list):
                    if self.animation_frame_count < per_frame * (index + 1):
                        self.current_img = frame
                        break
                    continue
                self.animation_frame_count = 0
                break

    # Assign an inventory slot to an item, then remove that item from the current level
    def pickup(self, item, where=None):
        where = self.inventory_selected_slot if where is None else where
        self.COLLECT_NOISE.play()
        self.inventory[where] = item.INV_OBJECT
        pygame.level.level_objects.remove(item)

    # Add an item to the player's inventory to the next free slot
    # If there is no free slot, the current item is dropped and new one is put in its place
    def add_to_inventory(self, item):
        x = 0
        if self.direction[self.RIGHT]:
            x = self.rect.x + self.rect.width
        if self.direction[self.LEFT]:
            x = self.rect.x - self.rect.width
        if self.inventory[self.inventory_selected_slot] is not None:
            if self.inventory[1 - self.inventory_selected_slot] is not None:
                current_item = self.inventory[self.inventory_selected_slot]
                dropped_current_item = DroppedItem(x/DroppedItem.OBJECT_WIDTH,
                                                   self.rect.y/DroppedItem.OBJECT_HEIGHT, current_item)
                self.pickup(item)
                pygame.level.level_objects.append(dropped_current_item)
            else:
                self.pickup(item, where=1 - self.inventory_selected_slot)
                self.inventory_selected_slot = 1 - self.inventory_selected_slot
        else:
            self.pickup(item)

    # If there is an item in the current slot, drop it
    def remove_from_inventory(self):
        if self.inventory[self.inventory_selected_slot] is not None:
            current_item = self.inventory[self.inventory_selected_slot]
            x = 0
            if self.direction[self.RIGHT]:
                x = self.rect.x + self.rect.width
            if self.direction[self.LEFT]:
                x = self.rect.x - self.rect.width
            dropped_current_item = DroppedItem(x/DroppedItem.OBJECT_WIDTH,
                                               self.rect.y/DroppedItem.OBJECT_HEIGHT, current_item)
            pygame.level.level_objects.append(dropped_current_item)
            self.inventory[self.inventory_selected_slot] = None

    # Draw the player onto the window surface
    def draw(self, surface):
        # Player Walking Animation
        if self.moving()[0]:
            self.walking_animation(self.RIGHT, self.PLAYER_RIGHT_WALKING)
            self.walking_animation(self.LEFT, self.PLAYER_LEFT_WALKING)
            self.animation_frame_count += 1
        else:
            self.animation_frame_count = 0
            if self.direction[self.RIGHT]:
                self.current_img = self.PLAYER_RIGHT
            if self.direction[self.LEFT]:
                self.current_img = self.PLAYER_LEFT
        surface.blit(self.current_img, (self.rect.x, self.rect.y))
        # Player Hearts
        last_heart = 5
        for heart in range(self.HEALTH):
            surface.blit(self.FULL_HEART, (last_heart, 5))
            last_heart += self.HEART_WIDTH + 5
        for heart in range(10 - self.HEALTH):
            if heart < 10:
                surface.blit(self.EMPTY_HEART, (last_heart, 5))
                last_heart += self.HEART_WIDTH + 5
        # Player Inventory
        last_slot = 15 + self.INVENTORY_SLOT.get_width()
        for slot in range(self.INVENTORY_SIZE):
            surface.blit(self.INVENTORY_SLOT, (surface.get_width() - last_slot,
                                               surface.get_height() - self.INVENTORY_SLOT.get_height() - 20))
            if self.inventory[slot] is not None:
                self.inventory[slot].draw(surface, slot, (surface.get_width() - last_slot,
                                                          surface.get_height() - self.INVENTORY_SLOT.get_height() - 20))
            if slot == self.inventory_selected_slot:
                surface.blit(self.INVENTORY_SLOT_SELECT, (surface.get_width() - last_slot + self.INVENTORY_SLOT.get_width() / 2 - self.INVENTORY_SLOT_SELECT.get_width() / 2,
                                                          surface.get_height() - 15))
            last_slot += self.INVENTORY_SLOT.get_width() + self.INVENTORY_SLOT.get_width() / 4
