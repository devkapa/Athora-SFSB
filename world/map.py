import pygame

from world.map_objects import ObjectType, Floor, Wall


class Map:

    layout = "WWWWWWWWWWWWWWWWWWWWWWWWWW" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nW                        W" + \
             "\nWWWWWWWWWWWWWWWWWWWWWWWWWW"

    map_objects = []
    center_point: ObjectType

    rect: pygame.Rect

    def __init__(self, layout=layout):
        split_layout = layout.split("\n")

        self.rect = pygame.Rect((0, 0), (832, 640))

        for line_index, line in enumerate(split_layout):
            for char_index, char in enumerate(line):
                if char == "W":
                    self.map_objects.append(Wall(char_index, line_index))
                if char == " ":
                    self.map_objects.append(Floor(char_index, line_index))
                if char == "C":
                    center = Floor(char_index, line_index)
                    self.center_point = center
                    self.map_objects.append(center)

    def draw(self, surface):
        for obj in self.map_objects:
            obj.draw(surface)

    def get_center_point(self):
        return self.center_point

