from typing import List, Optional, Tuple, Dict, Union

from random import randrange
import asyncio
import pygame

from util import Direction
from object import Object

class Board:
    def __init__(self, boardSize: int):
        assert 3 <= boardSize <= 8, "Not proper board size"
        
        self.boardSize = boardSize
        
        self.width, self.height = pygame.display.get_window_size()
        self.blockSize = self.width // (self.boardSize + 1)
        
        self.margin = self.blockSize // 2
        self.Objects: List[List[Object]] = [
            [Object() for y in range(boardSize)]
            for x in range(boardSize)
        ]
        self.makeNewObj()
    
    async def _makeRect(self, x: int, y: int):
        realX =                self.margin + self.blockSize * y
        realY = self.height - (self.margin + self.blockSize * (self.boardSize - x))
        self.Objects[x][y].setRect(pygame.Rect(
            realX, realY,
            self.blockSize, self.blockSize
        ))
    
    async def loadRect(self):
        tasks = [
            self._makeRect(x, y)
            for x in range(self.boardSize)
            for y in range(self.boardSize)
        ]
        await asyncio.gather(*tasks)

    async def draw(self, screen: pygame.Surface):
        tasks = [
            self.Objects[x][y].draw(screen)
            for x in range(self.boardSize)
            for y in range(self.boardSize)
        ]
        await asyncio.gather(*tasks)
    
    def makeNewObj(self):
        while True:
            r = randrange(self.boardSize)
            c = randrange(self.boardSize)
            
            if self.Objects[r][c].value == 0:
                self.Objects[r][c].make()
                break
    
    def alignLeft(self):
        obj = self.Objects
        moved = False

        for rIdx in range(self.boardSize):
            topBlank = 0
            merged = False
            
            for cIdx in range(self.boardSize):
                if obj[rIdx][cIdx].value == 0:
                    continue
                if cIdx != topBlank:
                    obj[rIdx][topBlank].value = obj[rIdx][cIdx].value
                    obj[rIdx][cIdx].remove()
                    print(f"({rIdx}, {cIdx}) -> ({rIdx}, {topBlank})")

                if topBlank != 0 and \
                    obj[rIdx][topBlank-1].value == obj[rIdx][topBlank].value and\
                    obj[rIdx][topBlank-1].value != 0:
                    if not merged:
                        obj[rIdx][topBlank-1].value *= 2
                        obj[rIdx][topBlank].remove()
                        topBlank -= 1
                    merged = not merged
                
                topBlank += 1
                moved = True
        return moved
