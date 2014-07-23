import copy
import random
from hsgame.targeting import *


class DoNothingBot:
    def __init__(self):
        self.game = None

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        pass

    def set_game(self, game):
        self.game = game

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card):
        return 0

    def choose_option(self, *options):
        return options[0]


class PredictableBot:
    def __init__(self):
        self.game = None

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        done_something = True

        if player.hero.power.can_use():
            player.hero.power.use()

        if player.hero.can_attack():
            player.hero.attack()

        while done_something:
            done_something = False
            for card in copy.copy(player.hand):
                if card.can_use(player, self.game):
                    self.game.play_card(card)
                    done_something = True

        for minion in copy.copy(player.minions):
            if minion.can_attack():
                minion.attack()

    def set_game(self, game):
        self.game = game

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card):
        return 0

    def choose_option(self, *options):
        return options[0]


class RandomBot:
    def __init__(self):
        self.game = None

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        def get_move_list():
            if player.hero.power.can_use():
                move_list.append(player.hero.power.use())

            if player.hero.can_attack():
                move_list.append(player.hero.attack())

            for minion in copy.copy(player.minions):
                if minion.can_attack():
                    move_list.append(minion.attack())

            for card in copy.copy(player.hand):
                if card.can_use(player, self.game):
                    move_list.append(self.game.play_card(card))

        move_list = []
        turn_ended = True
        while turn_ended:
            get_move_list()
            if len(move_list) == 0:
                turn_ended = False
            if random.randint(0, len(move_list)) == 0:
                turn_ended = False
            if len(move_list) > 0:
                move_list.pop(random.randint(0, len(move_list) - 1))

    def set_game(self, game):
        self.game = game

    def choose_target(self, targets):
        return targets[random.randint(0, len(targets) - 1)]

    def choose_index(self, card):
        return 0

    def choose_option(self, *options):
        return options[random.randint(0, len(targets) - 1)]