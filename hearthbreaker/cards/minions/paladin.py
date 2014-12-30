from hearthbreaker.tags.action import Equip, Give, Heal
from hearthbreaker.tags.base import Deathrattle, Battlecry, Effect
from hearthbreaker.tags.selector import PlayerSelector, MinionSelector, SelfSelector, EnemyPlayer, HeroSelector
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import MinionCard, Minion, WeaponCard, Weapon
from hearthbreaker.tags.status import SetAttack, DivineShield
from hearthbreaker.tags.condition import IsType
from hearthbreaker.tags.event import MinionSummoned


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


class GuardianOfKings(MinionCard):
    def __init__(self):
        super().__init__("Guardian of Kings", 7, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Heal(6), HeroSelector()))

    def create_minion(self, player):
        return Minion(5, 6)


class Ashbringer(WeaponCard):
    def __init__(self):
        super().__init__("Ashbringer", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.LEGENDARY)

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
        super().__init__("Cobalt Guardian", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE, MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(6, 3, effects=[Effect(MinionSummoned(IsType(MINION_TYPE.MECH)), Give(DivineShield()),
                                            SelfSelector())])
