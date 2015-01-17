from hearthbreaker.tags.action import Heal, Draw, Steal, Give
from hearthbreaker.tags.base import Aura, Deathrattle, Effect, Battlecry, Buff, BuffUntil
from hearthbreaker.tags.condition import IsMinion, AttackLessThanOrEqualTo
from hearthbreaker.tags.event import TurnStarted, CharacterHealed, TurnEnded
from hearthbreaker.tags.selector import PlayerSelector, MinionSelector, CharacterSelector, BothPlayer, \
    EnemyPlayer, UserPicker, RandomPicker
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import MinionCard, Minion
from hearthbreaker.tags.status import ChangeHealth, HealAsDamage, AttackEqualsHealth, MultiplySpellDamage, \
    MultiplyHealAmount, ChangeAttack


class AuchenaiSoulpriest(MinionCard):
    def __init__(self):
        super().__init__("Auchenai Soulpriest", 4, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 5, auras=[Aura(HealAsDamage(), PlayerSelector())])


class CabalShadowPriest(MinionCard):
    def __init__(self):
        super().__init__("Cabal Shadow Priest", 6, CHARACTER_CLASS.PRIEST, CARD_RARITY.EPIC,
                         battlecry=Battlecry(Steal(),
                                             MinionSelector(AttackLessThanOrEqualTo(2),
                                                            players=EnemyPlayer(),
                                                            picker=UserPicker())))

    def create_minion(self, player):
        return Minion(4, 5)


class Lightspawn(MinionCard):
    def __init__(self):
        super().__init__("Lightspawn", 4, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(0, 5, buffs=[Buff(AttackEqualsHealth())])


class Lightwell(MinionCard):
    def __init__(self):
        super().__init__("Lightwell", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(0, 5, effects=[Effect(TurnStarted(), Heal(3), CharacterSelector(picker=RandomPicker()))])


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
        return Minion(7, 7, auras=[Aura(MultiplySpellDamage(2), PlayerSelector()),
                                   Aura(MultiplyHealAmount(2), PlayerSelector())])


class TempleEnforcer(MinionCard):
    def __init__(self):
        super().__init__("Temple Enforcer", 6, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give(ChangeHealth(3)), MinionSelector(picker=UserPicker())))

    def create_minion(self, player):
        return Minion(6, 6)


class DarkCultist(MinionCard):
    def __init__(self):
        super().__init__("Dark Cultist", 3, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 4, deathrattle=Deathrattle(Give(ChangeHealth(3)), MinionSelector(picker=RandomPicker())))


class Shrinkmeister(MinionCard):
    def __init__(self):
        super().__init__("Shrinkmeister", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give(BuffUntil(ChangeAttack(-2), TurnEnded())),
                                             MinionSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(3, 2)
