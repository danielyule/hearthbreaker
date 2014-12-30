import json
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.game_objects import Game, card_lookup, Deck
from hearthbreaker.cards import *
import timeit


def load_deck(filename):
    cards = []
    character_class = CHARACTER_CLASS.MAGE

    with open(filename, "r") as deck_file:
        contents = deck_file.read()
        items = contents.splitlines()
        for line in items[0:]:
            parts = line.split(" ", 1)
            count = int(parts[0])
            for i in range(0, count):
                card = card_lookup(parts[1])
                if card.character_class != CHARACTER_CLASS.ALL:
                    character_class = card.character_class
                cards.append(card)

    if len(cards) > 30:
        pass

    return Deck(cards, character_class)


def do_stuff():
    _count = 0

    def play_game():
        nonlocal _count
        _count += 1
        new_game = game.copy()
        try:
            new_game.start()
        except Exception as e:
            print(json.dumps(new_game.__to_json__(), default=lambda o: o.__to_json__()))
            print(new_game._all_cards_played)
            raise e

        del new_game

        if _count % 100 == 0:
            print("---- game #{} ----".format(_count))

    deck1 = load_deck("hunter.hsdeck")
    deck2 = load_deck("paladin.hsdeck")
    game = Game([deck1, deck2], [RandomAgent(), RandomAgent()])

    print(timeit.timeit(play_game, 'gc.enable()', number=10000))

if __name__ == "__main__":
    do_stuff()
