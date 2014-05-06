import hsgame.targetting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card

__author__ = 'Daniel'


class CircleOfHealing(Card):
    def __init__(self):
        super().__init__("Circle of Healing", 0, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)
        
        targets = game.other_player.minions.copy()
        targets.extend(player.minions)

        for minion in targets:
            minion.heal(4 + player.spell_power)
