import pygame

from player.player import Player

pygame.font.init()


WHITE = (255, 255, 255)
PINK = (255, 225, 225)

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Athora: SpaceF Strikes Back")

DAMAGE_SURFACE = pygame.Surface((800, 600))
DAMAGE_SURFACE.set_alpha(180)
DAMAGE_SURFACE.fill(PINK)

FPS = 60
PAUSED, CONTINUE = 0, 1


def draw_window(player):
    WIN.fill(WHITE)
    player.draw(WIN)


def draw_death():
    WIN.blit(DAMAGE_SURFACE, (0, 0))


def main():

    clock = pygame.time.Clock()
    running = True

    state = CONTINUE

    player = Player()

    while running:

        clock.tick(FPS)

        if state == CONTINUE:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()

                # DEBUG
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        player.HEALTH -= 1

                player.process_event(event)

            keys_pressed = pygame.key.get_pressed()
            player.handle_movement(keys_pressed)

            draw_window(player)

        if player.HEALTH <= 0:
            draw_death()
            state = PAUSED

        pygame.display.update()


if __name__ == '__main__':
    main()
