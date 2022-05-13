import pygame
import pygame_gui
from player.player import Player


def main():
    pygame.init()

    pygame.display.set_caption("Athora: SpaceF Strikes Back")
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#00FFFF'))

    manager = pygame_gui.UIManager((800, 600))

    play = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text='Play!', manager=manager)

    clock = pygame.time.Clock()

    running = True

    player = Player()
    player.rect.x = 0
    player.rect.y = 0
    movement = 10
    player_list = pygame.sprite.Group()

    while running:
        tick = clock.tick(60)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == play:
                    print("Play")
                    player_list.add(player)

            if event.type == pygame.KEYDOWN:
                if event.key == ord('w') or event.key == pygame.K_UP:
                    player.move(0, -movement)
                if event.key == ord('a') or event.key == pygame.K_LEFT:
                    player.move(-movement, 0)
                if event.key == ord('s') or event.key == pygame.K_DOWN:
                    player.move(0, movement)
                if event.key == ord('d') or event.key == pygame.K_RIGHT:
                    player.move(movement, 0)

            if event.type == pygame.KEYUP:
                if event.key == ord('w') or event.key == pygame.K_UP:
                    player.move(0, movement)
                if event.key == ord('a') or event.key == pygame.K_LEFT:
                    player.move(movement, 0)
                if event.key == ord('s') or event.key == pygame.K_DOWN:
                    player.move(0, -movement)
                if event.key == ord('d') or event.key == pygame.K_RIGHT:
                    player.move(-movement, 0)

            manager.process_events(event)

        manager.update(tick)

        window_surface.blit(background, (0, 0))
        player_list.draw(window_surface)
        player.update()

        manager.draw_ui(window_surface)

        pygame.display.update()
        pygame.display.flip()


if __name__ == '__main__':
    main()
