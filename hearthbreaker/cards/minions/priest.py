import copy
from hearthbreaker.effects import HealAsDamage
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import MinionCard, Minion
from hearthbreaker.cards.battlecries import take_control_of_minion, give_three_health


class AuchenaiSoulpriest(MinionCard):
    def __init__(self):
        super().__init__("Auchenai Soulpriest", 4, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 5, effects=[HealAsDamage()])


class CabalShadowPriest(MinionCard):
    def __init__(self):
        super().__init__("Cabal Shadow Priest", 6, CHARACTER_CLASS.PRIEST, CARD_RARITY.EPIC,
                         targeting_func=hearthbreaker.targeting.find_enemy_minion_battlecry_target,
                         filter_func=lambda target: target.calculate_attack() <= 2)

    def create_minion(self, player):
        return Minion(4, 5, battlecry=take_control_of_minion)


class Lightspawn(MinionCard):
    def __init__(self):
        super().__init__("Lightspawn", 4, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def attack_equal_to_health():
            return minion.health

        def silence():
            minion.calculate_attack = old_calculate

        minion = Minion(0, 5)
        old_calculate = minion.calculate_attack
        minion.calculate_attack = attack_equal_to_health
        minion.bind_once("silenced", silence)
        return minion


class Lightwell(MinionCard):
    def __init__(self):
        super().__init__("Lightwell", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE)

    def create_minion(self, player):
        def heal_damaged_friendly_character():
            targets = hearthbreaker.targeting.find_friendly_spell_target(
                player.game, lambda character: character.health != character.calculate_max_health())
            if len(targets) != 0:
                targets[player.game.random(0, len(targets) - 1)].heal(player.effective_heal_power(3), minion)

        minion = Minion(0, 5)
        player.bind("turn_started", heal_damaged_friendly_character)
        minion.bind_once("silenced", lambda: player.unbind("turn_started", heal_damaged_friendly_character))
        return minion


class NorthshireCleric(MinionCard):
    def __init__(self):
        super().__init__("Northshire Cleric", 1, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.FREE)

    def create_minion(self, player):
        def draw_card():
            player.draw()

        minion = Minion(1, 3)
        player.game.bind("minion_healed", draw_card)
        minion.bind_once("silenced", lambda: player.game.unbind("minion_healed", draw_card))
        return minion


class ProphetVelen(MinionCard):
    def __init__(self):
        super().__init__("Prophet Velen", 7, CHARACTER_CLASS.PRIEST, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def silence():
            player.heal_multiplier //= 2
            player.spell_multiplier //= 2

        minion = Minion(7, 7)
        minion.bind_once("silenced", silence)
        player.heal_multiplier *= 2
        player.spell_multiplier *= 2
        return minion


class TempleEnforcer(MinionCard):
    def __init__(self):
        super().__init__("Temple Enforcer", 6, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(6, 6, battlecry=give_three_health)


class DarkCultist(MinionCard):
    def __init__(self):
        super().__init__("Dark Cultist", 3, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def give_3_health(minion):
            targets = copy.copy(minion.player.minions)
            if len(targets) > 0:
                targets[minion.game.random(0, len(targets) - 1)].increase_health(3)
        return Minion(3, 4, deathrattle=give_3_health)
