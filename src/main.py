import pygame
import sys
import game

# Initialize Pygame
pygame.init()

# Main game loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #user selects a tile
        if event.type == pygame.MOUSEBUTTONDOWN:
            #return tile coordinates
            mousePos = pygame.mouse.get_pos()
            #identify tile at those coordinates
            tile_obj = game.snap_to_tile(mousePos)
            #handle the selection
            game.moveManagement(tile_obj)
                
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()


    