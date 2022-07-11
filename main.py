import pygame
pygame.init()

import random
random.seed(0)
import asyncio

from board import Board
from util import makeText

# Setup screen mode
screen = pygame.display.set_mode((640, 740))

# Title text
title, titleRect = makeText("2048", "nanumgothicbold", 50, (320, 80))

board = Board(8, debug=True)
board.loadRect()

# Game loop
while True:
    # Proceed events
    event = pygame.event.poll()

    if event.type == pygame.QUIT:
        break
    
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            break
        
        board.tryAlign(event.key)

    # Draw Things
    screen.fill((255, 255, 255))
    screen.blit(title, titleRect)
    board.draw(screen)

    # Update Screen
    pygame.time.Clock().tick(60)
    pygame.display.update()

# Safe-exit
pygame.quit()
