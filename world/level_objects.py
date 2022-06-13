import os.path

import pygame


# A structure for a 32x32 object that will appear on the level
class ObjectType:

    # Dimensions of the object
    OBJECT_WIDTH, OBJECT_HEIGHT = 32, 32

    # Texture to be displayed
    TEXTURE: pygame.Surface

    # Rectangle around the object
    rect: pygame.Rect

    # Initialise the texture for the object and resize it
    def __init__(self, pos_x, pos_y, texture, path=None):
        self.TEXTURE_IMG = pygame.image.load(os.path.join('assets', 'textures', 'tiles', texture) if path is None else path).convert_alpha()
        self.TEXTURE = pygame.transform.scale(self.TEXTURE_IMG, (self.OBJECT_WIDTH, self.OBJECT_HEIGHT))
        self.rect = pygame.Rect(pos_x*self.OBJECT_WIDTH, pos_y*self.OBJECT_HEIGHT, self.OBJECT_WIDTH, self.OBJECT_HEIGHT)

    # Draw the object at it's position in the level
    def draw(self, surface):
        surface.blit(self.TEXTURE, (self.rect.x, self.rect.y))

    # Function used to resize some textures if they are not 32x32
    def set_size(self, x, y):
        self.TEXTURE = pygame.transform.scale(self.TEXTURE_IMG, (x, y))
        self.rect.width = x
        self.rect.height = y


# The following classes are common ObjectTypes with predefined textures
class Background(ObjectType):

    texture = 'floor.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Air(ObjectType):

    texture = 'barrier.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Water(ObjectType):

    texture = "water.jpg"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Glass(ObjectType):

    texture = "glass.png"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Bush(ObjectType):

    texture = "bush.png"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)
        self.set_size(64, 32)


class Tree(ObjectType):

    texture = "tree.png"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)
        self.set_size(128, 138)


class DirtBkg(ObjectType):

    texture = "dirtbkg.png"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class GroundBkg(ObjectType):

    texture = "groundbkg.png"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)



# An extension of the ObjectType class that the player cannot walk past
# Structurally, it is the same as an ObjectType
class CollideType(ObjectType):

    def __init__(self, pos_x, pos_y, texture):
        super().__init__(pos_x, pos_y, texture)


class Wall(CollideType):

    texture = 'wall.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Grass(CollideType):

    texture = 'grass.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Dirt(CollideType):

    texture = 'dirt.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class StairLeft(CollideType):

    texture = 'stair_left.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class StairRight(CollideType):

    texture = 'stair_right.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Sand(CollideType):

    texture = 'sand.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Barrier(CollideType):

    texture = 'barrier.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Board(ObjectType):

    texture = 'todo.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)
        self.set_size(192, 64)


# An extension of the ObjectType that, when collided with, allows for players to interact with
class InteractiveType(ObjectType):

    TEXTURE: pygame.Surface

    # InteractiveTypes have an Event that is posted when interacted with
    # They also have a text POPUP that is shown when the player collides with it
    EVENT: pygame.event.Event
    POPUP: str

    def __init__(self, event, popup, pos_x, pos_y, texture, path=None):
        super().__init__(pos_x, pos_y, texture, path)
        self.EVENT = event
        self.POPUP = popup

    def on_interact(self):
        pygame.event.post(self.EVENT)


class Sign(InteractiveType):

    POPUP = "'F' to read Sign"
    READ = pygame.USEREVENT + 7
    EVENT = pygame.event.Event(READ)
    TEXTURE = 'signpost.png'
    CONTENTS: str

    READ_SOUND = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'tiles', 'pop.ogg'))

    def __init__(self, pos_x, pos_y, contents, texture=TEXTURE, popup=POPUP):
        super().__init__(self.EVENT, popup, pos_x, pos_y, texture)
        self.CONTENTS = contents

    def on_interact(self):
        self.EVENT.sign = self
        super().on_interact()


class ExitDoor(InteractiveType):

    POPUP = "'F' to enter"
    ENTER = pygame.USEREVENT + 2
    EVENT = pygame.event.Event(ENTER)
    TEXTURE = 'trapdoor.png'

    NO_LEVEL = Sign(0, 0, "This portal doesn't lead\nanywhere.")
    PORTAL_SOUND = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'tiles', 'portal.wav'))

    def __init__(self, pos_x, pos_y, texture=TEXTURE):
        super().__init__(self.EVENT, self.POPUP, pos_x, pos_y, texture)
        self.set_size(self.OBJECT_WIDTH, 64)


class ExitHelicopter(ExitDoor):

    TEXTURE = 'helicopter.png'

    NO_LEVEL = Sign(0, 0, "This helicopter doesn't lead\nanywhere.")
    PORTAL_SOUND = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'tiles', 'helicopter.wav'))

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, texture=self.TEXTURE)
        self.set_size(300, 128)


class Printer(Sign):

    POPUP = "'F' to turn on"
    TEXTURE = 'printer.png'

    def __init__(self, pos_x, pos_y, contents):
        super().__init__(pos_x, pos_y, contents, texture=self.TEXTURE, popup=self.POPUP)
        self.CONTENTS = contents
        self.set_size(32, 44)


class Lava(InteractiveType):

    POPUP = "Ow!"
    BURN = pygame.USEREVENT + 8
    EVENT = pygame.event.Event(BURN)
    TEXTURE = 'lava.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(self.EVENT, self.POPUP, pos_x, pos_y, self.TEXTURE)

    def draw(self, surface):
        super().draw(surface)
        if pygame.player.rect.colliderect(self.rect):
            self.on_interact()


# An extension of the InteractiveType which represents an item that can be picked up
# These items are affected by gravity and 'stores' the InventoryItem equivalent within its structure
class DroppedItem(InteractiveType):

    GRAVITY = 2

    POPUP = "'F' to pickup "
    PICKUP = pygame.USEREVENT + 6
    EVENT = pygame.event.Event(PICKUP)
    INV_OBJECT = None

    def __init__(self, pos_x, pos_y, inv_obj):
        super().__init__(self.EVENT, self.POPUP, pos_x, pos_y, None, path=os.path.join('assets', 'textures', 'items', inv_obj.TEXTURE_FILE))
        self.set_size(40, 40)
        self.INV_OBJECT = inv_obj
        self.POPUP += self.INV_OBJECT.NAME

    def on_interact(self):
        self.EVENT.item = self
        super().on_interact()

    def draw(self, surface):
        self.handle_movement(pygame.level)
        super().draw(surface)

    def handle_movement(self, level):
        if self.apply_gravity(level):
            self.rect.y += self.GRAVITY

    def apply_gravity(self, level):
        if not self.check_collision(level, (self.rect.x, self.rect.y + self.GRAVITY)):
            return True
        return False

    def check_collision(self, level, change):
        potential_rect = pygame.Rect(change[0], change[1], self.OBJECT_WIDTH, self.OBJECT_HEIGHT)
        for level_object in level.level_objects:
            if isinstance(level_object, CollideType):
                if level_object.rect.colliderect(potential_rect):
                    return True
        return False


