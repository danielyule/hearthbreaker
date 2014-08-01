import re
from hsgame.agents.basic_agents import RandomAgent
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Game, card_lookup, Deck
import hsgame.cards


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

if __name__ == "__main__":
    deck1 = load_deck("example.hsdeck")
    deck2 = load_deck("example.hsdeck")
    game = Game([deck1, deck2], [RandomAgent(), RandomAgent()])
    for i in range(0, 100):
        print("Copying Game")
        new_game = game.copy()
        print("Starting Game")
        new_game.start()
        print("Game Complete")