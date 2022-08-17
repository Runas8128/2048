import UI

game = UI.Game()

from threading import Thread
Thread(target=game.run).run()
