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
    player_list = pygame.sprite.Group()

    font = pygame.font.SysFont('Comic Sans MS', 30)

    while running:
        tick = clock.tick(60)
        text = font.render(f"X: {player.rect.x} Y: {player.rect.y}", True, '#000000', None)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == play:
                    print("Game started")
                    play.hide()
                    player_list.add(player)

            if event.type == pygame.KEYDOWN:
                player.move(event, 1)

            if event.type == pygame.KEYUP:
                player.move(event, 0)

            manager.process_events(event)

        manager.update(tick)

        window_surface.blit(background, (0, 0))

        player_list.draw(window_surface)
        player.update()

        window_surface.blit(text, (0, 0))

        manager.draw_ui(window_surface)

        pygame.display.update()
        pygame.display.flip()


if __name__ == '__main__':
    main()
