import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card, Minion, MinionCard


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
                minion.summon(player, game, len(player.minions))

            old_death_rattle = minion.deathrattle
            minion.deathrattle = resurrection

        super().use(player, game)

        apply_deathrattle(self.target)


class Bloodlust(Card):
    def __init__(self):
        super().__init__("Bloodlust", 5, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for minion in player.minions:
            minion.temp_attack += 3


class EarthShock(Card):
    def __init__(self):
        super().__init__("Earth Shock", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.silence()
        self.target.damage(player.effective_spell_damage(1), self)


class FarSight(Card):
    def __init__(self):
        super().__init__("Far Sight", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.EPIC)

    def use(self, player, game):
        class Filter:
            def __init__(self, card):
                self.amount = 3
                self.filter = lambda c: c is card
                self.min = 0

        def reduce_cost(card):
            nonlocal filter
            filter = Filter(card)
            player.unbind("card_drawn", reduce_cost)

        super().use(player, game)

        filter = None
        player.bind("card_drawn", reduce_cost)
        player.draw()
        player.mana_filters.append(filter)


class FeralSpirit(Card):
    def __init__(self):
        super().__init__("Feral Spirit", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE, overload=2)

    def use(self, player, game):
        super().use(player, game)

        class SpiritWolf(MinionCard):
            def __init__(self):
                super().__init__("Spirit Wolf", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.SPECIAL)

            def create_minion(self, p):
                minion = Minion(2, 3)
                minion.taunt = True
                return minion

        for i in range(0, 2):
            spirit_wolf = SpiritWolf()
            spirit_wolf.summon(player, game, len(player.minions))
