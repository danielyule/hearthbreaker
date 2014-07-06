import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card


class Backstab(Card):
    def __init__(self):
        super().__init__("Backstab", 0, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE,
                         hsgame.targeting.find_minion_spell_target,
                         lambda target: target.health == target.calculate_max_health())

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(2), self)
