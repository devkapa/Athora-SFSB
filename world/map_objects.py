import os.path

import pygame


class ObjectType:

    OBJECT_WIDTH, OBJECT_HEIGHT = 32, 32

    TEXTURE: pygame.Surface

    rect: pygame.Rect

    def __init__(self, pos_x, pos_y, texture, path=None):
        self.TEXTURE_IMG = pygame.image.load(os.path.join('assets', 'textures', 'tiles', texture) if path is None else path).convert_alpha()
        self.TEXTURE = pygame.transform.scale(self.TEXTURE_IMG, (self.OBJECT_WIDTH, self.OBJECT_HEIGHT))
        self.rect = pygame.Rect(pos_x*self.OBJECT_WIDTH, pos_y*self.OBJECT_HEIGHT, self.OBJECT_WIDTH, self.OBJECT_HEIGHT)

    def draw(self, surface):
        surface.blit(self.TEXTURE, (self.rect.x, self.rect.y))

    def set_size(self, x, y):
        self.TEXTURE = pygame.transform.scale(self.TEXTURE_IMG, (x, y))
        self.rect.width = x
        self.rect.height = y


class Floor(ObjectType):

    texture = 'floor.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class Air(ObjectType):

    texture = 'barrier.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


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


class Barrier(CollideType):

    texture = 'barrier.png'

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, self.texture)


class InteractiveType(ObjectType):

    TEXTURE: pygame.Surface
    EVENT: pygame.event.Event
    POPUP: str

    def __init__(self, event, popup, pos_x, pos_y, texture, path=None):
        super().__init__(pos_x, pos_y, texture, path)
        self.EVENT = event
        self.POPUP = popup

    def on_interact(self):
        pass


class ExitDoor(InteractiveType):

    POPUP = "'F' to enter"
    ENTER = pygame.USEREVENT + 2
    EVENT = pygame.event.Event(ENTER)
    TEXTURE = 'trapdoor.png'

    PORTAL_SOUND = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'portal.wav'))

    def __init__(self, pos_x, pos_y):
        super().__init__(self.EVENT, self.POPUP, pos_x, pos_y, self.TEXTURE)
        self.set_size(self.OBJECT_WIDTH, 64)

    def on_interact(self):
        self.PORTAL_SOUND.play()
        pygame.event.post(self.EVENT)


class Sign(InteractiveType):

    POPUP = "'F' to read Sign"
    READ = pygame.USEREVENT + 7
    EVENT = pygame.event.Event(READ)
    TEXTURE = 'signpost.png'
    CONTENTS: str

    def __init__(self, pos_x, pos_y, contents):
        super().__init__(self.EVENT, self.POPUP, pos_x, pos_y, self.TEXTURE)
        self.CONTENTS = contents

    def on_interact(self):
        self.EVENT.sign = self
        pygame.event.post(self.EVENT)


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

    def on_interact(self):
        pygame.event.post(self.EVENT)


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
        pygame.event.post(self.EVENT)

    def draw(self, surface):
        self.handle_movement(pygame.level)
        super().draw(surface)

    def handle_movement(self, level):
        x_change = 0
        y_change = 0
        if self.apply_gravity(level):
            y_change = self.GRAVITY
        self.rect.x += x_change
        self.rect.y += y_change

    def apply_gravity(self, level):
        if not self.check_collision(level, (self.rect.x, self.rect.y + self.GRAVITY)):
            return True
        return False

    def check_collision(self, level, change):
        potential_rect = pygame.Rect(change[0], change[1], self.OBJECT_WIDTH, self.OBJECT_HEIGHT)
        for map_object in level.map_objects:
            if isinstance(map_object, CollideType):
                if map_object.rect.colliderect(potential_rect):
                    return True
        return False


