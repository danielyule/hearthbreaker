from hsgame.constants import CHARACTER_CLASS, CARD_STATUS
from hsgame.game_objects import Card

__author__ = 'Daniel'


class ArcaneMissiles(Card):
    def __init__(self):
        super().__init__("Arcane Missiles", 1, CHARACTER_CLASS.MAGE, CARD_STATUS.BASIC, False)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, 3 + player.spell_power):
            targets = game.other_player.minions.copy()
            targets.append(game.other_player)
            target = targets[game.random(0, len(targets) -1)]
            target.spell_damage(1, self)


