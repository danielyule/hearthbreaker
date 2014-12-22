from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import Card
import hearthbreaker.targeting


class ArmorPlating(Card):
    def __init__(self):
        super().__init__("Armor Plating", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.increase_health(1)
