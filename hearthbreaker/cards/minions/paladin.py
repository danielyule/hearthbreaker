from hearthbreaker.cards.base import MinionCard, WeaponCard
from hearthbreaker.game_objects import Weapon, Minion
from hearthbreaker.tags.action import Equip, Give, Heal, Damage, GiveAura
from hearthbreaker.tags.base import Deathrattle, Battlecry, Effect, Buff, ActionTag, AuraUntil
from hearthbreaker.tags.selector import PlayerSelector, MinionSelector, SelfSelector, EnemyPlayer, HeroSelector, \
    BothPlayer, CardSelector
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.tags.status import SetAttack, DivineShield, ChangeHealth, ChangeAttack, ManaChange
from hearthbreaker.tags.condition import IsType, HasCardName, MinionHasDeathrattle
from hearthbreaker.tags.event import MinionSummoned, MinionDied, CardPlayed


class AldorPeacekeeper(MinionCard):
    def __init__(self):
        super().__init__("Aldor Peacekeeper", 3, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE,
                         battlecry=Battlecry(Give(SetAttack(1)), MinionSelector(condition=None, players=EnemyPlayer())))

    def create_minion(self, player):
        return Minion(3, 3)


class ArgentProtector(MinionCard):
    def __init__(self):
        super().__init__("Argent Protector", 2, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Give(DivineShield()), MinionSelector()))

    def create_minion(self, player):
        return Minion(2, 2)


class DefenderMinion(MinionCard):
    def __init__(self):
        super().__init__("Defender", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def create_minion(self, p):
        return Minion(2, 1)


class GuardianOfKings(MinionCard):
    def __init__(self):
        super().__init__("Guardian of Kings", 7, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Heal(6), HeroSelector()))

    def create_minion(self, player):
        return Minion(5, 6)


class Ashbringer(WeaponCard):
    def __init__(self):
        super().__init__("Ashbringer", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.LEGENDARY, False)

    def create_weapon(self, player):
        weapon = Weapon(5, 3)
        return weapon


class TirionFordring(MinionCard):
    def __init__(self):
        super().__init__("Tirion Fordring", 8, CHARACTER_CLASS.PALADIN, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(6, 6, divine_shield=True, taunt=True,
                      deathrattle=Deathrattle(Equip(Ashbringer()), PlayerSelector()))


class CobaltGuardian(MinionCard):
    def __init__(self):
        super().__init__("Cobalt Guardian", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(6, 3, effects=[Effect(MinionSummoned(IsType(MINION_TYPE.MECH)), ActionTag(Give(DivineShield()),
                                            SelfSelector()))])


class SilverHandRecruit(MinionCard):
    def __init__(self):
        super().__init__("Silver Hand Recruit", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.FREE, False)

    def create_minion(self, player):
        return Minion(1, 1)


class ShieldedMinibot(MinionCard):
    def __init__(self):
        super().__init__("Shielded Minibot", 2, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(2, 2, divine_shield=True)


class Quartermaster(MinionCard):
    def __init__(self):
        super().__init__("Quartermaster", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.EPIC,
                         battlecry=Battlecry(Give([Buff(ChangeAttack(2)), Buff(ChangeHealth(2))]),
                                             MinionSelector(HasCardName("Silver Hand Recruit"))))

    def create_minion(self, player):
        return Minion(2, 5)


class ScarletPurifier(MinionCard):
    def __init__(self):
        super().__init__("Scarlet Purifier", 3, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE,
                         battlecry=Battlecry(Damage(2), MinionSelector(MinionHasDeathrattle(), BothPlayer())))

    def create_minion(self, player):
        return Minion(4, 3)


class BolvarFordragon(MinionCard):
    def __init__(self):
        super().__init__("Bolvar Fordragon", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.LEGENDARY,
                         effects=[Effect(MinionDied(), ActionTag(Give(ChangeAttack(1)), SelfSelector()))])

    def create_minion(self, player):
        return Minion(1, 7)


class DragonConsort(MinionCard):
    def __init__(self):
        super().__init__("Dragon Consort", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE,
                         minion_type=MINION_TYPE.DRAGON,
                         battlecry=Battlecry(GiveAura([AuraUntil(ManaChange(-3),
                                                                 CardSelector(condition=IsType(MINION_TYPE.DRAGON)),
                                                                 CardPlayed(IsType(MINION_TYPE.DRAGON)), False)]),
                                             PlayerSelector()))

    def create_minion(self, player):
        return Minion(5, 5)
