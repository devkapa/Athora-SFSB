import pygame

from user.inv_objects import Potion, Gun
from user.player import Player
from world.map_objects import ObjectType, Floor, Wall, ExitDoor, Air, Barrier, Grass, Dirt, DroppedItem, Sign, Lava
from world.npc import RobotEnemy, NPC, Bullet


class Map:

    layout: str

    map_objects: list[ObjectType]
    spawn_point: ObjectType

    map_npc: list[NPC]
    map_bullets: list[Bullet]

    rect: pygame.Rect
    title: str

    def __init__(self, title, layout):
        split_layout = layout.split("\n")

        self.rect = pygame.Rect((0, 0), (832, 640))
        self.title = title
        self.layout = layout
        self.map_objects = []
        self.map_npc = []
        self.map_bullets = []

        for line_index, line in enumerate(split_layout):
            for char_index, char in enumerate(line):
                if char == "-":
                    self.map_objects.append(Floor(char_index, line_index))
                if char == "W":
                    self.map_objects.append(Wall(char_index, line_index))
                if char == "S":
                    spawn = Air(char_index, line_index)
                    self.spawn_point = spawn
                    self.map_objects.append(spawn)
                if char == "T":
                    self.map_objects.append(ExitDoor(char_index, line_index))
                if char == "H":
                    self.map_objects.append(DroppedItem(char_index, line_index, Potion(10)))
                if char == "P":
                    self.map_objects.append(DroppedItem(char_index, line_index, Gun()))
                if char == "B":
                    self.map_objects.append(Barrier(char_index, line_index))
                if char == "G":
                    self.map_objects.append(Grass(char_index, line_index))
                if char == "D":
                    self.map_objects.append(Dirt(char_index, line_index))
                if char == "L":
                    self.map_objects.append(Lava(char_index, line_index))
                if char == "E":
                    self.map_npc.append(RobotEnemy(char_index*32, line_index*32))
                if char == "R":
                    self.map_npc.append(RobotEnemy(char_index*32, line_index*32, health=3))
                if char == "!":
                    self.map_objects.append(Sign(char_index, line_index,
                                                 "Welcome to Athora!\nPress 'A' & 'D' or '←' & '→'\nto move!"))
                if char == "@":
                    self.map_objects.append(Sign(char_index, line_index,
                                                 "Excellent work! Try jumping\nover this wall by pressing\n'SPACE'!"))
                if char == "#":
                    self.map_objects.append(Sign(char_index, line_index,
                                                 "Nice! Here, take this gun.\nTry shooting this robot\nby pressing 'M'!"))
                if char == "$":
                    self.map_objects.append(Sign(char_index, line_index,
                                                 "Whew, that was close! This\npotion will heal you up.\nPress 'M' to use."))
                if char == "%":
                    self.map_objects.append(Sign(char_index, line_index,
                                                 "Use '1' and '2' to switch\nbetween your inventory\nslots!"))
                if char == "^":
                    self.map_objects.append(Sign(char_index, line_index,
                                                 "Good job finishing the\ntutorial. Enter this portal\nto begin your journey!"))

    def draw(self, surface):
        for obj in self.map_objects:
            if 0 - obj.OBJECT_WIDTH < obj.rect.x < surface.get_width() and 0 - obj.OBJECT_HEIGHT < obj.rect.y < surface.get_height():
                obj.draw(surface)
        for npc in self.map_npc:
            if 0 - npc.NPC_WIDTH < npc.rect.x < surface.get_width() and 0 - npc.NPC_HEIGHT < npc.rect.y < surface.get_height():
                npc.draw(surface)

    def scroll(self, vel_x, vel_y):
        for obj in self.map_objects:
            obj.rect.x += vel_x
            obj.rect.y += vel_y
        for npc in self.map_npc:
            npc.rect.x += vel_x
            npc.rect.y += vel_y
        for bullet in self.map_bullets:
            bullet.rect.x += vel_x
            bullet.rect.y += vel_y

    def get_spawn_point(self):
        return self.spawn_point


class Maps:

    maps: list = []
    current: Map
    player: Player

    def __init__(self, maps, player):
        self.maps = maps
        self.current = self.maps[0]
        self.player = player
        self.spawn_player()

    def __add__(self, other):
        if isinstance(other, int):
            if self.maps[self.maps.index(self.current) + other] is not None:
                self.current = self.maps[self.maps.index(self.current) + other]
                self.spawn_player()

    def spawn_player(self):
        self.player.rect.x = self.current.spawn_point.rect.x
        self.player.rect.y = self.current.spawn_point.rect.y - self.player.PLAYER_WIDTH / 2
