from hsgame.constants import CHARACTER_CLASS, CARD_STATUS
from hsgame.game_objects import Card

__author__ = 'Daniel'


class AvengingWrath(Card):
    def __init__(self):
        super().__init__("Avenging Wrath", 6, CHARACTER_CLASS.PALADIN, CARD_STATUS.EXPERT, False)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, 8):
            targets = game.other_player.minions.copy()
            targets.append(game.other_player)
            target = targets[game.random(0, len(targets) - 1)]
            target.spell_damage(1, self)
