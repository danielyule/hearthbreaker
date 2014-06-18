import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import Card

__author__ = 'randomflyingtaco'

class MortalCoil(Card):
    def __init__(self):
        super().__init__("Mortal Coil", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE, hsgame.targeting.find_minion_spell_target)

        def use(self, player, game):
            target.spell_damage(1 + player.spell_power, wrath)
            if minion.health <= 1 +player.spell_power:
              player.draw()
