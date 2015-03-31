from hearthbreaker.cards.base import MinionCard, WeaponCard
from hearthbreaker.cards.spells.warrior import BurrowingMine
from hearthbreaker.game_objects import Weapon, Minion
from hearthbreaker.tags.action import IncreaseArmor, Damage, Give, Equip, AddCard
from hearthbreaker.tags.base import Effect, Battlecry, Buff, Aura, ActionTag
from hearthbreaker.tags.condition import AttackLessThanOrEqualTo, IsMinion, IsType
from hearthbreaker.tags.event import MinionPlaced, CharacterDamaged, ArmorIncreased, Damaged
from hearthbreaker.tags.selector import BothPlayer, SelfSelector, TargetSelector, HeroSelector, MinionSelector, \
    PlayerSelector, EnemyPlayer, UserPicker
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.tags.status import ChangeAttack, Charge, ChangeHealth


class BattleAxe(WeaponCard):
    def __init__(self):
        super().__init__("Battle Axe", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON, False)

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
        return Minion(1, 4, effects=[Effect(CharacterDamaged(condition=IsMinion()), ActionTag(IncreaseArmor(),
                                                                                              HeroSelector()))])


class CruelTaskmaster(MinionCard):
    def __init__(self):
        super().__init__("Cruel Taskmaster", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         battlecry=Battlecry([Damage(1), Give(ChangeAttack(2))], MinionSelector(players=BothPlayer(),
                                                                                                picker=UserPicker())))

    def create_minion(self, player):
        return Minion(2, 2)


class FrothingBerserker(MinionCard):
    def __init__(self):
        super().__init__("Frothing Berserker", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(2, 4, effects=[Effect(CharacterDamaged(player=BothPlayer(),
                                                             condition=IsMinion()), ActionTag(Give(ChangeAttack(1)),
                                                                                              SelfSelector()))])


class GrommashHellscream(MinionCard):
    def __init__(self):
        super().__init__("Grommash Hellscream", 8, CHARACTER_CLASS.WARRIOR, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(4, 9, charge=True, enrage=[Aura(ChangeAttack(6), SelfSelector())])


class KorkronElite(MinionCard):
    def __init__(self):
        super().__init__("Kor'kron Elite", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 3, charge=True)


class WarsongCommander(MinionCard):
    def __init__(self):
        super().__init__("Warsong Commander", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(2, 3, effects=[Effect(MinionPlaced(AttackLessThanOrEqualTo(3)),
                                            ActionTag(Give(Charge()), TargetSelector()))])


class Warbot(MinionCard):
    def __init__(self):
        super().__init__("Warbot", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(1, 3, enrage=[Aura(ChangeAttack(1), SelfSelector())])


class Shieldmaiden(MinionCard):
    def __init__(self):
        super().__init__("Shieldmaiden", 6, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE,
                         battlecry=Battlecry(IncreaseArmor(5), HeroSelector()))

    def create_minion(self, player):
        return Minion(5, 5)


class SiegeEngine(MinionCard):
    def __init__(self):
        super().__init__("Siege Engine", 5, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(5, 5, effects=[Effect(ArmorIncreased(), ActionTag(Give(ChangeAttack(1)), SelfSelector()))])


class IronJuggernaut(MinionCard):
    def __init__(self):
        super().__init__("Iron Juggernaut", 6, CHARACTER_CLASS.WARRIOR, CARD_RARITY.LEGENDARY,
                         minion_type=MINION_TYPE.MECH,
                         battlecry=Battlecry(AddCard(BurrowingMine(), add_to_deck=True), PlayerSelector(EnemyPlayer())))

    def create_minion(self, player):
        return Minion(6, 5)


class ScrewjankClunker(MinionCard):
    def __init__(self):
        super().__init__("Screwjank Clunker", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE,
                         minion_type=MINION_TYPE.MECH,
                         battlecry=Battlecry(Give([Buff(ChangeHealth(2)), Buff(ChangeAttack(2))]),
                                             MinionSelector(IsType(MINION_TYPE.MECH), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(2, 5)


class AxeFlinger(MinionCard):
    def __init__(self):
        super().__init__("Axe Flinger", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(2, 5, effects=[Effect(Damaged(), ActionTag(Damage(2), HeroSelector(EnemyPlayer())))])
