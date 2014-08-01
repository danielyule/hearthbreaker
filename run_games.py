import re
from hsgame.agents.basic_agents import RandomAgent
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Game, card_lookup, Deck
from hsgame.cards import *
import timeit


def load_deck(filename):
    deck_file = open(filename, "r")
    contents = deck_file.read()
    items = re.split('\s*,\s*', contents)
    char_class = CHARACTER_CLASS.from_str(items[0])
    cards = []
    for line in items[1:]:
        line = line.strip(" \n,")
        card = card_lookup(line)
        cards.append(card)

    deck_file.close()

    return Deck(cards, char_class)


def do_stuff():
    def play_game():
        new_game = game.copy()
        new_game.start()

    deck1 = load_deck("example.hsdeck")
    deck2 = load_deck("example.hsdeck")
    game = Game([deck1, deck2], [RandomAgent(), RandomAgent()])
    game.start()

    print(timeit.timeit(play_game, 'gc.enable()', number=100000))

if __name__ == "__main__":
    do_stuff()