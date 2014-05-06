from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card
import hsgame.targetting
__author__ = 'Daniel'


class ArcaneMissiles(Card):
    def __init__(self):
        super().__init__("Arcane Missiles", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE, False)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, 3 + player.spell_power):
            targets = game.other_player.minions.copy()
            targets.append(game.other_player)
            target = targets[game.random(0, len(targets) -1)]
            target.spell_damage(1, self)


class IceLance(Card):
    def __init__(self):
        super().__init__("Ice Lance", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON, True, hsgame.targetting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if self.target.frozen:
            self.target.spell_damage(4, self)
        else:
            self.target.freeze()


class ArcaneExplosion(Card):
    def __init__(self):
        super().__init__("Arcane Explosion", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE, False)

    def use(self, player, game):
        super().use(player, game)
        for minion in game.other_player.minions.copy():
            minion.spell_damage(1 + player.spell_power, self)

