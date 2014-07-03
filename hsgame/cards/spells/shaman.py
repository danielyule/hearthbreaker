import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
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


class ForkedLightning(Card):
    def __init__(self):
        super().__init__("Forked Lightning", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON, overload=2)

    def use(self, player, game):
        super().use(player, game)

        targets = game.other_player.minions.copy()
        for i in range(0, 2):
            target = targets.pop(game.random(0, len(targets) - 1))
            target.damage(player.effective_spell_damage(2), self)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 2


class FrostShock(Card):
    def __init__(self):
        super().__init__("Frost Shock", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         hsgame.targeting.find_enemy_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(1), self)
        self.target.freeze()


class Hex(Card):
    def __init__(self):
        super().__init__("Hex", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE, hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        class Frog(MinionCard):
            def __init__(self):
                super().__init__("Frog", 0, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

            def create_minion(self, p):
                minion = Minion(0, 1, MINION_TYPE.BEAST)
                minion.taunt = True
                return minion

        frog = Frog()
        minion = frog.create_minion(None)
        minion.index = self.target.index
        minion.card = frog
        self.target.player.minions[minion.index] = minion


class LavaBurst(Card):
    def __init__(self):
        super().__init__("Lava Burst", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE, hsgame.targeting.find_spell_target,
                         overload=2)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(5), self)


class LightningBolt(Card):
    def __init__(self):
        super().__init__("Lightning Bolt", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         hsgame.targeting.find_spell_target, overload=1)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(3), self)
