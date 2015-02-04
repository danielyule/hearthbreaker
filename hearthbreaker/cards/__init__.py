from hearthbreaker.cards.minions import *
from hearthbreaker.cards.spells import *
from hearthbreaker.cards.weapons import *
import hearthbreaker.constants
from hearthbreaker.game_objects import Card

class TheCoin(Card):
    def __init__(self):
        super().__init__("The Coin", 0, hearthbreaker.constants.CHARACTER_CLASS.ALL,
                         hearthbreaker.constants.CARD_RARITY.SPECIAL)

    def use(self, player, game):
        super().use(player, game)
        if player.mana < 10:
            player.mana += 1