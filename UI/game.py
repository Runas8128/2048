from typing import Tuple
import pygame

class Game:
    def __init__(
        self, *,
        res: Tuple[int] = (480, 640),
        seed: int = 0,
        size: int = 8, debug: bool = False
    ):
        pygame.init()
        self.scr = pygame.display.set_mode(res)

        import random ; random.seed(seed)

        from .board import Board
        self.board = Board(boardSize=size, debug=debug)
        self.board.loadRect()

        from .util import makeText
        self.title = makeText("2048", "nanumgothicbold", 50, (320, 80))
        
        self.clock = pygame.time.Clock()
        self.looping = True

    def tick(self):
        event = pygame.event.poll()

        if event.type == pygame.QUIT:
            self.looping = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.looping = False
            
            self.board.tryAlign(event.key)
            self.board.checkOver()

        # Draw Things
        self.scr.fill((255, 255, 255))
        self.scr.blit(*self.title)
        self.board.draw(self.scr)

        # Update Screen
        self.clock.tick(60)
        pygame.display.update()
    
    def exit(self):
        pygame.quit()
    
    def run(self):
        try:
            while self.looping:
                self.tick()
        finally:
            self.exit()
