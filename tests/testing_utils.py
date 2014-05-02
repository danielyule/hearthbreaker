import copy
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Deck, Game

__author__ = 'Daniel'
class StackedDeck(Deck):

    def __init__(self, card_pattern, character_class):
        cards = []
        while len(cards) + len(card_pattern) < 30:
            cards.extend(copy.deepcopy(card_pattern))

        cards.extend(card_pattern[:30 - len(cards)])
        super().__init__(cards, character_class)

    def draw(self, random):
        for card_index in range(0, 30):
            if not self.used[card_index]:
                self.used[card_index] = True
                self.left -= 1
                return self.cards[card_index]

        return None


def generate_game_for(card1, card2, first_agent_type, second_agent_type):

    card1 = card1()
    card2 = card2()
    if card1.character_class == CHARACTER_CLASS.ALL:
        class1 = CHARACTER_CLASS.MAGE
    else:
        class1 = card1.character_class

    if card2.character_class == CHARACTER_CLASS.ALL:
        class2 = CHARACTER_CLASS.MAGE
    else:
        class2 = card2.character_class

    deck1 = StackedDeck([card1], class1)
    deck2 = StackedDeck([card2], class2)
    game = Game([deck1, deck2], [first_agent_type(), second_agent_type()])
    game.current_player = game.players[1]
    game.pre_game()
    return game


def check_mana_cost(cost):
    def create_func(func):
        def run(self):
            game = func(self)
            self.assertEqual(game.current_player.mana, game.current_player.max_mana - cost,
                             "Mana cost was not correct in " + str(func))

        return run

    return create_func