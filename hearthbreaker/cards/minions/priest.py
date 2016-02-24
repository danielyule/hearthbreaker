from hearthbreaker.cards.base import MinionCard
from hearthbreaker.game_objects import Minion
from hearthbreaker.tags.action import Heal, Draw, Steal, Give, Damage, SwapStats
from hearthbreaker.tags.base import Aura, Deathrattle, Effect, Battlecry, Buff, BuffUntil, ActionTag
from hearthbreaker.tags.condition import IsMinion, AttackLessThanOrEqualTo, IsType, IsDamaged, GreaterThan
from hearthbreaker.tags.event import TurnStarted, CharacterHealed, TurnEnded
from hearthbreaker.tags.selector import PlayerSelector, MinionSelector, CharacterSelector, BothPlayer, \
    EnemyPlayer, UserPicker, RandomPicker, CurrentPlayer, HeroSelector, SelfSelector, Count, CardSelector
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
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
        return Minion(0, 5, effects=[Effect(TurnStarted(), ActionTag(Heal(3),
                                                                     CharacterSelector(condition=IsDamaged(),
                                                                                       picker=RandomPicker())))])


class NorthshireCleric(MinionCard):
    def __init__(self):
        super().__init__("Northshire Cleric", 1, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(1, 3, effects=[Effect(CharacterHealed(condition=IsMinion(),
                                                            player=BothPlayer()), ActionTag(Draw(), PlayerSelector()))])


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


class ShadowOfNothing(MinionCard):
    def __init__(self):
        super().__init__("Shadow of Nothing", 0, CHARACTER_CLASS.PRIEST, CARD_RARITY.EPIC, False)

    def create_minion(self, p):
        return Minion(0, 1)


class DarkCultist(MinionCard):
    def __init__(self):
        super().__init__("Dark Cultist", 3, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 4, deathrattle=Deathrattle(Give(ChangeHealth(3)), MinionSelector(picker=RandomPicker())))


class Shrinkmeister(MinionCard):
    def __init__(self):
        super().__init__("Shrinkmeister", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give(BuffUntil(ChangeAttack(-2), TurnEnded(player=CurrentPlayer()))),
                                             MinionSelector(players=BothPlayer(), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(3, 2)


class UpgradedRepairBot(MinionCard):
    def __init__(self):
        super().__init__("Upgraded Repair Bot", 5, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE,
                         minion_type=MINION_TYPE.MECH,
                         battlecry=Battlecry(Give(ChangeHealth(4)), MinionSelector(IsType(MINION_TYPE.MECH),
                                                                                   picker=UserPicker())))

    def create_minion(self, player):
        return Minion(5, 5)


class Shadowbomber(MinionCard):
    def __init__(self):
        super().__init__("Shadowbomber", 1, CHARACTER_CLASS.PRIEST, CARD_RARITY.EPIC,
                         battlecry=Battlecry(Damage(3), HeroSelector(players=BothPlayer())))

    def create_minion(self, player):
        return Minion(2, 1)


class Shadowboxer(MinionCard):
    def __init__(self):
        super().__init__("Shadowboxer", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(CharacterHealed(player=BothPlayer()), ActionTag(Damage(1),
                                            CharacterSelector(players=EnemyPlayer(), picker=RandomPicker(),
                                                              condition=None)))])


class Voljin(MinionCard):
    def __init__(self):
        super().__init__("Vol'jin", 5, CHARACTER_CLASS.PRIEST, CARD_RARITY.LEGENDARY,
                         battlecry=Battlecry(SwapStats("health", "health", True), MinionSelector(players=BothPlayer(),
                                                                                                 picker=UserPicker())))

    def create_minion(self, player):
        return Minion(6, 2)


class TwilightWhelp(MinionCard):
    def __init__(self):
        super().__init__("Twilight Whelp", 1, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.DRAGON,
                         battlecry=(Battlecry(Give(Buff(ChangeHealth(2))), SelfSelector(),
                                              GreaterThan(Count(CardSelector(condition=IsType(MINION_TYPE.DRAGON))),
                                                          value=0))))

    def create_minion(self, player):
        return Minion(2, 1)
