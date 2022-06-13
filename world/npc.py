import os

import pygame

from world.level_objects import CollideType


class Bullet:

    # Set bullet pixel dimensions and load the bullet texture
    BULLET_WIDTH, BULLET_HEIGHT = 10, 5
    BULLET_TEXTURE = pygame.image.load(os.path.join('assets', 'textures', 'npc', 'bullet.png')).convert_alpha()

    # Enum values for bullet direction
    RIGHT, LEFT = 0, 1

    # Load the bullet shoot sound
    SHOOT_SOUND = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'misc', 'shoot.wav'))

    # Set the bullet speed per frame
    SPEED = 4

    # Initialise a variable to store the entity which shot the bullet
    ORIGIN = None

    rect: pygame.Rect
    facing: int

    def __init__(self, x, y, facing, origin):
        self.rect = pygame.Rect(x, y, self.BULLET_WIDTH, self.BULLET_HEIGHT)
        self.facing = facing
        self.ORIGIN = origin
        self.SHOOT_SOUND.play()

    def draw(self, surface):
        surface.blit(self.BULLET_TEXTURE, (self.rect.x, self.rect.y))

    def origin(self):
        return self.ORIGIN


class NPC:

    # Set variables to store the health of the NPC
    HEALTH: int
    MAX_HEALTH: int

    # Load the images to be used for the health bar
    HEALTH_BAR = pygame.image.load(os.path.join('assets', 'textures', 'npc', 'health_bkg.png')).convert_alpha()
    HEALTH_OVERLAY = 34

    DEATH = pygame.USEREVENT + 3
    DEATH_EVENT = pygame.event.Event(DEATH)

    GRAVITY = 2

    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)

    TEXTURE: pygame.Surface
    NPC_WIDTH, NPC_HEIGHT = 32, 56

    RIGHT, LEFT = 0, 1
    FACING = RIGHT

    rect: pygame.Rect
    inventory: list

    # Initialise NPC textures, rectangle and health
    def __init__(self, pos_x, pos_y, health, texture, inventory=None):
        self.TEXTURE_IMG = pygame.image.load(os.path.join('assets', 'sprites', 'npc', texture)).convert_alpha()
        self.TEXTURE_NORMAL = pygame.transform.scale(self.TEXTURE_IMG, (self.NPC_WIDTH, self.NPC_HEIGHT))
        self.TEXTURE_FLIPPED = pygame.transform.flip(self.TEXTURE_NORMAL, True, False)
        self.TEXTURE = self.TEXTURE_NORMAL
        self.rect = pygame.Rect(pos_x, pos_y, self.NPC_WIDTH, self.NPC_HEIGHT)
        self.HEALTH = health
        self.MAX_HEALTH = health
        self.inventory = [] if inventory is None else inventory

    # Draw NPC to the window surface, and draw a health bar beneath it if health is lost
    def draw(self, window):
        self.update(window)
        window.blit(self.TEXTURE, (self.rect.x, self.rect.y))
        if self.HEALTH < self.MAX_HEALTH:
            window.blit(self.HEALTH_BAR, (self.rect.x + self.rect.width / 2 - self.HEALTH_BAR.get_width() / 2,
                                          self.rect.y + self.rect.height))
            percent = self.HEALTH / self.MAX_HEALTH
            ovl_width = self.HEALTH_OVERLAY
            new_width = round(ovl_width*percent)
            ovl = pygame.Rect(self.rect.x + self.rect.width / 2 - self.HEALTH_OVERLAY / 2,
                              self.rect.y + self.rect.height, new_width, 4)
            if percent < 0.35:
                pygame.draw.rect(window, self.RED, ovl)
            elif percent < 0.65:
                pygame.draw.rect(window, self.YELLOW, ovl)
            elif percent < 1:
                pygame.draw.rect(window, self.GREEN, ovl)

    # Returns if gravity should be applied to the NPC
    def apply_gravity(self, level):
        if not self.check_collision(level, (self.rect.x, self.rect.y + self.GRAVITY)):
            return True
        return False

    # Check if the NPC is going to collide with a CollideType
    def check_collision(self, level, change):
        potential_rect = pygame.Rect(change[0], change[1], self.NPC_WIDTH, self.NPC_HEIGHT)
        for level_object in level.level_objects:
            if isinstance(level_object, CollideType):
                if level_object.rect.colliderect(potential_rect):
                    return True
        return False

    # Apply gravity
    def handle_movement(self, level):
        if self.apply_gravity(level):
            self.rect.y += self.GRAVITY

    # Function to be called when NPC is drawn to apply movement rules
    def update(self, window):
        self.handle_movement(pygame.level)

    def change_health(self, amt):
        self.HEALTH += amt

    def facing(self):
        return self.FACING


class RobotEnemy(NPC):

    texture = 'robot.png'

    # Variables to be used to store if and how long the NPC is alerted
    alerted = False
    alerted_time = 0
    ALERTED_IMAGE = pygame.image.load(os.path.join('assets', 'textures', 'npc', 'exclamation.png')).convert_alpha()
    ALERTED_SOUND = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'npc', 'alert.mp3'))

    # Dimensions of the 'range' rectangle centered around the NPC
    RADIUS_WIDTH, RADIUS_HEIGHT = 500, NPC.NPC_HEIGHT
    viewing_radius: pygame.Rect

    OFFSET: int

    # Initialise the base class and 'range' rectangle around the NPC
    def __init__(self, pos_x, pos_y, health=10, texture=texture, inventory=None):
        super().__init__(pos_x, pos_y, health, texture, inventory=inventory)
        self.viewing_radius = pygame.Rect(self.rect.x - (self.RADIUS_WIDTH / 2 + self.NPC_WIDTH / 2),
                                          self.rect.y - (self.RADIUS_HEIGHT / 2 + self.NPC_HEIGHT / 2),
                                          self.RADIUS_WIDTH, self.RADIUS_HEIGHT)
        self.OFFSET = 0

    # Update the position of the 'range' rectangle if the NPC moves
    # If the player is in the rectangle, alert the NPC and start shooting
    def update(self, window):
        super().update(window)

        # Update x and y position of the 'range' rectangle
        self.viewing_radius.x = self.rect.x - self.RADIUS_WIDTH / 2 + self.NPC_WIDTH / 2
        self.viewing_radius.y = self.rect.y - self.RADIUS_HEIGHT / 2 + self.NPC_HEIGHT / 2

        # Check for player collision with 'range' rectangle
        if pygame.player.rect.colliderect(self.viewing_radius) and pygame.player.HEALTH > 0:
            if not self.alerted:
                self.alerted = True
                self.ALERTED_SOUND.play()
            if pygame.player.rect.x + pygame.player.rect.width / 2 < self.viewing_radius.x + self.viewing_radius.width / 2:
                self.FACING = self.LEFT
                self.TEXTURE = self.TEXTURE_NORMAL
            if pygame.player.rect.x + pygame.player.rect.width / 2 > self.viewing_radius.x + self.viewing_radius.width / 2:
                self.FACING = self.RIGHT
                self.TEXTURE = self.TEXTURE_FLIPPED
        else:
            self.alerted = False
            self.alerted_time = 0

        # While alerted, draw an exclamation above the NPC
        if self.alerted_time > 0:
            window.blit(self.ALERTED_IMAGE, (self.rect.x + self.rect.width / 2 - self.ALERTED_IMAGE.get_width() / 2,
                                             self.rect.y - self.ALERTED_IMAGE.get_height()))

        # Once been alerted for more than one second, start shooting
        if self.alerted_time > 1:
            x = 0
            y = self.rect.y + (self.rect.h / 2) + self.OFFSET
            if self.FACING == self.LEFT:
                x = self.rect.x
            if self.FACING == self.RIGHT:
                x = self.rect.x + self.rect.w

            own_bullets = 0
            for bullet in pygame.level.level_bullets:
                if bullet.origin() == self:
                    own_bullets += 1
            if own_bullets < 3:
                pygame.level.level_bullets.append(Bullet(x, y, self.FACING, self))
                self.alerted_time = 0


class RobotBoss(RobotEnemy):

    texture = 'boss.png'
    NPC_WIDTH, NPC_HEIGHT = 85, 128
    RADIUS_WIDTH, RADIUS_HEIGHT = 500, NPC_HEIGHT

    # Initialise the base class and 'range' rectangle around the NPC
    def __init__(self, pos_x, pos_y, health=10, inventory=None):
        super().__init__(pos_x, pos_y, health, texture=self.texture, inventory=inventory)
        self.OFFSET = 50

    def update(self, window):
        super().update(window)

        # Update x and y position of the 'range' rectangle
        self.viewing_radius.x = self.rect.x - self.RADIUS_WIDTH / 2 + self.NPC_WIDTH / 2
        self.viewing_radius.y = self.rect.y - self.RADIUS_HEIGHT / 2 + self.NPC_HEIGHT / 2

