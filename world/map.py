import pygame

from player.player import Player
from world.map_objects import ObjectType, Floor, Wall, ExitDoor, Air, Barrier, Grass, Dirt


class Map:

    layout: str

    map_objects: list[ObjectType]
    spawn_point: ObjectType

    rect: pygame.Rect
    title: str

    def __init__(self, title, layout):
        split_layout = layout.split("\n")

        self.rect = pygame.Rect((0, 0), (832, 640))
        self.title = title
        self.layout = layout
        self.map_objects = []

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
                if char == "B":
                    self.map_objects.append(Barrier(char_index, line_index))
                if char == "G":
                    self.map_objects.append(Grass(char_index, line_index))
                if char == "D":
                    self.map_objects.append(Dirt(char_index, line_index))

    def draw(self, surface):
        for obj in self.map_objects:
            obj.draw(surface)

    def scroll(self, vel_x, vel_y):
        for obj in self.map_objects:
            obj.rect.x += vel_x
            obj.rect.y += vel_y

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
