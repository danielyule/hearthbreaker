import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card


__author__ = 'Daniel'


class AncestralHealing(Card):
    def __init__(self):
        super().__init__("Ancestral Healing", 0, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.heal(self.target.max_health - self.target.health, self)
        self.target.taunt = True


class AncestralSpirit(Card):
    def __init__(self):
        super().__init__("Ancestral Spirit", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        def apply_deathrattle(minion):
            def resurrection(*args):
                if old_death_rattle is not None:
                    old_death_rattle(*args)

                minion = self.target.card
                minion.create_minion(player).add_to_board(minion, game, player, 0)

            old_death_rattle = minion.deathrattle
            minion.deathrattle = resurrection

        super().use(player, game)

        apply_deathrattle(self.target)
