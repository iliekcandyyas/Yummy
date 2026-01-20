import pygame
pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("i js copy pasted ts")

player = pygame.Rect(280, 180, 40, 40)
speed = 1
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= speed
    if keys[pygame.K_RIGHT]:
        player.x += speed
    if keys[pygame.K_UP]:
        player.y -= speed
    if keys[pygame.K_DOWN]:
        player.y += speed

    screen.fill((30, 30, 30))
    pygame.draw.rect(screen, (0, 200, 255), player)
    pygame.display.flip()

pygame.quit()

