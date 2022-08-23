from typing import List, Optional, Tuple, Dict, Union, Callable

from random import randrange
import asyncio
import pygame

from .object import Object

class Board:
    def __init__(self, boardSize: int, debug: bool):
        assert 3 <= boardSize <= 8, "Not proper board size"
        
        self.boardSize = boardSize
        
        self.width, self.height = pygame.display.get_window_size()
        self.blockSize = self.width // (self.boardSize + 1)
        self.over = False
        
        self.Objects: List[List[Object]] = [
            [Object() for y in range(boardSize)]
            for x in range(boardSize)
        ]

        asyncio.run(self.makeNewObj())
        self.loadRect()

        self.keyMap = {
            pygame.K_LEFT:  self.alignLeft,
            pygame.K_RIGHT: self.alignRight,
            pygame.K_UP:    self.alignUp,
            pygame.K_DOWN:  self.alignDown
        }

        self.debug = debug
    
    def logBoard(self):
        for ls in self.Objects:
            for obj in ls:
                print(obj.value, end=' ')
            print()
        print('--------------------')

    async def doForCell(self, coro):
        """|coro|
        helper function for independent cell-by-cell works
        """
        tasks = [
            coro(x, y)
            for x in range(self.boardSize)
            for y in range(self.boardSize)
        ]
        return await asyncio.gather(*tasks)
    
    def loadRect(self):
        """load Rectangle object for each cell"""
        async def _makeRect(x: int, y: int):
            margin = self.blockSize // 2

            realX =                margin + self.blockSize * y
            realY = self.height - (margin + self.blockSize * (self.boardSize - x))

            self.Objects[x][y].setRect(pygame.Rect(
                realX, realY,
                self.blockSize, self.blockSize
            ))
        asyncio.run(self.doForCell(_makeRect))

    def draw(self, screen: pygame.Surface):
        """draw each cells to `screen`"""
        async def _draw(x: int, y: int):
            self.Objects[x][y].draw(screen)
        asyncio.run(self.doForCell(_draw))

        if self.over:
            screen.fill((255, 255, 255, 128))
    
    async def _makeNewObj(self):
        """|coro|
        try to make new object forever
        """
        while True:
            r = randrange(self.boardSize)
            c = randrange(self.boardSize)
            
            if self.Objects[r][c].value == 0:
                self.Objects[r][c].make()
                break
    
    async def makeNewObj(self):
        """|coro|
        try to make new object with timeout

        Raise gameover flag if timeout
        """
        try:
            await asyncio.wait_for(self._makeNewObj(), 1.0)
        except asyncio.TimeoutError:
            self.over = True
    
    def isCellEmpty(self, rIdx: int, cIdx: int):
        """Return if Cell at (rIdx, cIdx) is empty"""
        return self.Objects[rIdx][cIdx].value == 0
    
    def safeMove(self, tarPos: Tuple[int, int], dstPos: Tuple[int, int]):
        """Move cell from dstPos to tarPos
        Returns True if cell moved successfully, else False
        """

        # reject move if position is same
        if tarPos == dstPos: return False

        tar = self.Objects[tarPos[0]][tarPos[1]]
        dst = self.Objects[dstPos[0]][dstPos[1]]
        tar.value = dst.value
        dst.remove()
        if self.debug:
            print(f"safely moved: {dstPos} -> {tarPos}")
        return True
    
    def merge(self, tarPos: Tuple[int, int], dstPos: Tuple[int, int]):
        """Merge cells (dstPos -> tarPos), if can
        Returns True if merged successfully, else False
        """

        # reject merge if position is same
        if tarPos == dstPos:
            if self.debug:
                print(f'reject merge: {tarPos} == {dstPos}')
            return False

        tar = self.Objects[tarPos[0]][tarPos[1]]
        dst = self.Objects[dstPos[0]][dstPos[1]]

        # reject merge if cell is already merged
        if tar.dirty:
            if self.debug:
                print(f'reject merge: {tarPos} is dirty')
            return False

        # reject merge if value is different
        if tar.value != dst.value:
            if self.debug:
                print(f'reject merge: {tar.value}@{tarPos} != {dst.value}@{dstPos}')
            return False

        # reject merge if one of cells is zero
        if tar.value * dst.value == 0:
            if self.debug:
                print(f'reject merge: one of cells is zero')
            return False

        tar.value *= 2
        tar.dirty = True
        dst.remove()
        if self.debug:
            print(f'safely merged: {dstPos} -> {tarPos}')
        return True
    
    def cleanBoard(self):
        """clean all cells after merging"""
        async def _clean(x: int, y: int):
            self.Objects[x][y].dirty = False
        asyncio.run(self.doForCell(_clean))
    
    def align_base(
        self,
        target: Tuple[int, int],
        move: Tuple[int, int],
        merge_pred: bool,
        merge: Tuple[int, int]
    ):
        """This provides basic move/merge logic"""

        if self.isCellEmpty(*target): return False

        moved = self.safeMove(move, target)
        merged = merge_pred and self.merge(merge, target)
        moved |= merged
        return moved, merged
    
    def moveAll_synced(self, reverse_second: bool, ):
        # Step 1. Set variables/aliases
        moved = False

        # Step 2. Run for each column
        for cIdx in range(self.boardSize):
            # Step 2-1. Set temp variables
            topBlank = self.boardSize - 1
            
            # Step 2-2. Run sequentially for each row
            for rIdx in range(self.boardSize - 1, -1, -1):
                # Step 2-2-1. simply move and merge block at (rIdx, cIdx)
                _moved, _merged = self.align_base((rIdx, cIdx), (topBlank, cIdx), topBlank < self.boardSize - 1, (topBlank+1, cIdx))
                moved |= _merged

                # Step 2-2-2. inc/dec top-blank index if merge failed
                if not _merged: topBlank -= 1

    def alignLeft(self):
        moved = False

        for rIdx in range(self.boardSize):
            topBlank = 0

            for cIdx in range(self.boardSize):
                _moved, _merged = self.align_base((rIdx, cIdx), (rIdx, topBlank), topBlank > 0, (rIdx, topBlank-1))
                moved |= _moved
                if not _merged: topBlank += 1
        
        # Step 3. clean all cells
        self.cleanBoard()
        
        # Step 4. if not moved, return False
        return moved
    
    def alignRight(self):
        moved = False

        for rIdx in range(self.boardSize):
            topBlank = self.boardSize - 1
            
            for cIdx in range(self.boardSize - 1, -1, -1):
                _moved, _merged = self.align_base((rIdx, cIdx), (rIdx, topBlank), topBlank < self.boardSize - 1, (rIdx, topBlank+1))
                moved |= merged
                if not merged: topBlank -= 1
        
        # Step 3. clean all cells
        self.cleanBoard()
        
        # Step 4. if not moved, return False
        return moved
    
    def alignUp(self):
        moved = False

        for cIdx in range(self.boardSize):
            topBlank = 0
            
            for rIdx in range(self.boardSize):
                _moved, _merged = self.align_base((rIdx, cIdx), (topBlank, cIdx), topBlank > 0, (topBlank-1, cIdx))
                moved |= merged
                if not merged: topBlank += 1
        
        # Step 3. clean all cells
        self.cleanBoard()
        
        # Step 4. if not moved, return False
        return moved
    
    def alignDown(self):
        # Step 1. Set variables/aliases
        moved = False

        # Step 2. Run for each column
        for cIdx in range(self.boardSize):
            # Step 2-1. Set temp variables
            topBlank = self.boardSize - 1
            
            # Step 2-2. Run sequentially for each row
            for rIdx in range(self.boardSize - 1, -1, -1):
                # Step 2-2-1. simply move and merge block at (rIdx, cIdx)
                _moved, _merged = self.align_base((rIdx, cIdx), (topBlank, cIdx), topBlank < self.boardSize - 1, (topBlank+1, cIdx))
                moved |= _merged

                # Step 2-2-2. inc/dec top-blank index if merge failed
                if not _merged: topBlank -= 1
        
        # Step 3. clean all cells
        self.cleanBoard()
        
        # Step 4. if not moved, return False
        return moved

    def tryAlign(self, key: int):
        if key not in self.keyMap.keys():
            return
        
        if self.keyMap[key]():
            asyncio.run(self.makeNewObj())
        
        if self.debug:
            self.logBoard()
    
    def checkOver(self):
        async def checkIfCellNotBlank(x: int, y: int):
            return self.Objects[x][y].value != 0
        if all(asyncio.run(self.doForCell(checkIfCellNotBlank))):
            self.over = True
