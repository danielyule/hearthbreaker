import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import Card

__author__ = 'randomflyingtaco'

class MortalCoil(Card):
    def __init__(self):
        super().__init__("Mortal Coil", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE, hsgame.targeting.find_minion_spell_target)

        def use(self, player, game):
            target.spell_damage(1 + player.spell_power, self)
            if minion.health <= 1 + player.spell_power:
                player.draw()

class Hellfire(Card):
    def __init__(self):
        super().__init__("Hellfire", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        targets = game.other_player.minions.copy()
        targets.extend(game.current_player.minions)
        targets.append(game.other_player.hero)
        targets.append(game.current_player.hero)
        for minion in targets:
            minion.spell_damage(3 + player.spell_power, self)

class ShadowBolt(Card):
    def __init__(self):
        super().__init__("Shadow Bolt", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.spell_damage(4 + player.spell_power, self)

