__author__ = 'Daniel'


class Observer:

    def __init__(self, writer):
        self.game = None
        self.writer = writer

    def observe(self, game):
        self.game = game
        game.players[0].bind("turn_started", self.turn_started, game.players[0])
        game.players[0].bind("turn_ended", self.turn_ended, game.players[0])
        game.players[0].bind("died", self.died, game.players[0])
        game.players[0].bind("card_drawn", self.card_drawn, game.players[0])
        game.players[0].bind("card_put back", self.card_put_back, game.players[0])
        game.players[0].bind("damaged", self.damaged, game.players[0])

        game.players[1].bind("turn_started", self.turn_started, game.players[1])
        game.players[1].bind("turn_ended", self.turn_ended, game.players[1])
        game.players[1].bind("died", self.died, game.players[1])
        game.players[1].bind("card_drawn", self.card_drawn, game.players[1])
        game.players[1].bind("card_put back", self.card_put_back, game.players[1])
        game.players[1].bind("damaged", self.damaged, game.players[1])

    def turn_started(self, player):
        self.writer.write("Turn started for " + str(player) + "\n")

    def turn_ended(self, player):
        self.writer.write("Turn ended for " + str(player) + "\n")

    def died(self, attacker, player):
        self.writer.write(str(player) + " died!\n")

    def card_drawn(self, card, player):
        self.writer.write(str(player) + " drew card " + str(card) + "\n")

    def card_put_back(self, card, player):
        self.writer.write(str(player) + " put back card " + str(card) + "\n")

    def damaged(self, amount, what, player):
        if what is None:
            what = "fatigue"
        self.writer.write(str(player) + " was damaged " + str(amount) + " by " + str(what) + "\n")
