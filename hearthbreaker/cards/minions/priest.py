from hearthbreaker.tags.action import HealAsDamage, ChangeHealth, Heal, Draw, AttackEqualsHealth
from hearthbreaker.tags.base import Aura, Deathrattle, Effect
from hearthbreaker.tags.condition import IsMinion
from hearthbreaker.tags.event import TurnStarted, CharacterHealed
from hearthbreaker.tags.selector import PlayerSelector, RandomSelector, MinionSelector, CharacterSelector, BothPlayer, \
    SelfSelector
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import MinionCard, Minion
from hearthbreaker.cards.battlecries import take_control_of_minion, give_three_health


class AuchenaiSoulpriest(MinionCard):
    def __init__(self):
        super().__init__("Auchenai Soulpriest", 4, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 5, auras=[Aura(HealAsDamage(), PlayerSelector())])


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
        return Minion(0, 5, auras=[Aura(AttackEqualsHealth(), SelfSelector())])


class Lightwell(MinionCard):
    def __init__(self):
        super().__init__("Lightwell", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(0, 5, effects=[Effect(TurnStarted(), Heal(3), RandomSelector(CharacterSelector()))])


class NorthshireCleric(MinionCard):
    def __init__(self):
        super().__init__("Northshire Cleric", 1, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(1, 3, effects=[Effect(CharacterHealed(condition=IsMinion(),
                                                            player=BothPlayer()), Draw(), PlayerSelector())])


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
        return Minion(3, 4, deathrattle=Deathrattle(ChangeHealth(3), RandomSelector(MinionSelector())))
