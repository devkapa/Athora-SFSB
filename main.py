import os.path

import pygame

from world.map import Map
from player.player import Player

pygame.font.init()


WHITE = (255, 255, 255)
AQUA = (0, 255, 255)
PINK = (255, 225, 225)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (168, 168, 168)

WIDTH, HEIGHT = 832, 640
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Athora: SpaceF Strikes Back")

FPS = 144
PAUSED, CONTINUE = 0, 1
DEDUCT, NONE, GAIN = -1, 0, 1


def render_font(text, px):
    font = pygame.font.Font(os.path.join('assets', 'fonts', 'pressstart.ttf'), px)
    return font.render(text, True, WHITE)


def create_overlay_surface(colour, alpha=180):
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.set_alpha(alpha)
    surface.fill(colour)
    return surface


def draw_window(player, global_map):
    WIN.fill(AQUA)
    global_map.draw(WIN)
    player.draw(WIN)


def draw_overlay(colour, title, subheading):
    WIN.blit(create_overlay_surface(colour), (0, 0))
    title_text = render_font(title, 40)
    subheading_text = render_font(subheading, 30)
    WIN.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - title_text.get_height()//2))
    WIN.blit(subheading_text,
             (WIDTH//2 - subheading_text.get_width()//2, HEIGHT//2 - subheading_text.get_height()//2 + 45))


def draw_damage(damage, damage_frames):
    if damage > NONE:
        WIN.blit(create_overlay_surface(GREEN, alpha=180-(damage_frames*6)), (0, 0))
    if damage < NONE:
        WIN.blit(create_overlay_surface(RED, alpha=180-(damage_frames*6)), (0, 0))


def main():

    clock = pygame.time.Clock()
    running = True

    state = CONTINUE

    global_map = Map()

    player = Player(spawn_x=WIDTH//2 - Player.PLAYER_WIDTH//2, spawn_y=HEIGHT//2 - Player.PLAYER_HEIGHT//2)
    damage = NONE
    damage_frames = 0

    while running:

        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            if state == PAUSED:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_r and player.HEALTH < 1:
                        running = False

                    if event.key == pygame.K_p and player.HEALTH > 0:
                        state = CONTINUE
                        continue

            if state == CONTINUE:

                if event.type == pygame.KEYDOWN:

                    # DEBUG
                    if event.key == pygame.K_h:
                        player.change_hp(-1)

                    # DEBUG
                    if event.key == pygame.K_j:
                        player.change_hp(1)

                    if event.key == pygame.K_p:
                        state = PAUSED
                        continue

                if event.type == player.DAMAGE:
                    if event.hp > 0:
                        damage = GAIN
                    if event.hp < 0:
                        damage = DEDUCT

                player.process_event(event)

        if state == CONTINUE:
            keys_pressed = pygame.key.get_pressed()
            player.handle_movement(WIN, keys_pressed, global_map)

        draw_window(player, global_map)

        if damage != NONE:
            damage_frames += 1

        if damage_frames > 30:
            damage_frames = 0
            damage = NONE

        if damage_frames > 0:
            draw_damage(damage, damage_frames)

        if state == PAUSED and player.HEALTH > 0:
            draw_overlay(GRAY, "Game Paused", "Press P to unpause")

        if player.HEALTH <= 0:
            draw_overlay(RED, "You died!", "Press R to restart")
            state = PAUSED

        pygame.display.update()


if __name__ == '__main__':
    while True:
        main()
