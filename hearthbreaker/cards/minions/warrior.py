from hearthbreaker.tags.action import Charge, ChangeAttack, IncreaseArmor, Damage, Give, Equip
from hearthbreaker.tags.base import Effect, Battlecry
from hearthbreaker.tags.condition import AttackLessThanOrEqualTo, IsMinion
from hearthbreaker.tags.event import MinionPlaced, CharacterDamaged
from hearthbreaker.tags.selector import BothPlayer, SelfSelector, TargetSelector, HeroSelector, MinionSelector, \
    PlayerSelector
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import MinionCard, Minion, WeaponCard, Weapon


class BattleAxe(WeaponCard):
    def __init__(self):
        super().__init__("Battle Axe", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.SPECIAL)

    def create_weapon(self, player):
        return Weapon(2, 2)


class ArathiWeaponsmith(MinionCard):
    def __init__(self):
        super().__init__("Arathi Weaponsmith", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Equip(BattleAxe()), PlayerSelector()))

    def create_minion(self, player):
        return Minion(3, 3)


class Armorsmith(MinionCard):
    def __init__(self):
        super().__init__("Armorsmith", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(1, 4, effects=[Effect(CharacterDamaged(condition=IsMinion()), IncreaseArmor(), HeroSelector())])


class CruelTaskmaster(MinionCard):
    def __init__(self):
        super().__init__("Cruel Taskmaster", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         battlecry=Battlecry([Damage(1), Give(ChangeAttack(2))], MinionSelector(players=BothPlayer())))

    def create_minion(self, player):

        return Minion(2, 2)


class FrothingBerserker(MinionCard):
    def __init__(self):
        super().__init__("Frothing Berserker", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def create_minion(self, player):
        minion = Minion(2, 4, effects=[Effect(CharacterDamaged(player=BothPlayer(),
                                                               condition=IsMinion()), ChangeAttack(1), SelfSelector())])
        return minion


class GrommashHellscream(MinionCard):
    def __init__(self):
        super().__init__("Grommash Hellscream", 8, CHARACTER_CLASS.WARRIOR, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(4, 9, charge=True, enrage=[ChangeAttack(6)])


class KorkronElite(MinionCard):
    def __init__(self):
        super().__init__("Kor'kron Elite", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 3, charge=True)


class WarsongCommander(MinionCard):
    def __init__(self):
        super().__init__("Warsong Commander", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(MinionPlaced(AttackLessThanOrEqualTo(3)), Charge(), TargetSelector())])
