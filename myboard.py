
from tkinter import *
from core import Game as Game
from core import Player as Player
from time import sleep


def play():
    players = (Player(),Player())
    game = Game(15,15)

    while True:
        for player in players:
            move = player.random_search(game)
            game.make_move(move)
            game.display()

            if game.terminal_test():
                print("Game over")
                return

            sleep(1)

play()