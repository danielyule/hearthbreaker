from hearthbreaker.tags.action import Taunt, Give, ChangeHealth, ChangeAttack, Damage, Silence, Transform, Draw, Heal, \
    Summon
from hearthbreaker.tags.base import Aura, Choice
from hearthbreaker.tags.selector import SelfSelector, CharacterSelector, MinionSelector, UserPicker, BothPlayer, \
    PlayerSelector, HeroSelector
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import MinionCard, Minion, Card


class Moonfire(Card):
    def __init__(self):
        super().__init__("Moonfire", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL, ref_name="moonfire_keeper")


class Dispel(Card):
    def __init__(self):
        super().__init__("Dispel", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class KeeperOfTheGrove(MinionCard):
    def __init__(self):
        super().__init__("Keeper of the Grove", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE, choices=[
            Choice(Moonfire(), Damage(2), CharacterSelector(players=BothPlayer(), picker=UserPicker())),
            Choice(Dispel(), Silence(), MinionSelector(players=BothPlayer(), picker=UserPicker()))
        ])

    def create_minion(self, player):
        return Minion(2, 4)


class CatDruid(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL,
                         ref_name="Druid of the Claw (cat)")

    def create_minion(self, p):
        return Minion(4, 4, charge=True)


class BearDruid(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL,
                         ref_name="Druid of the Claw (bear)")

    def create_minion(self, p):
        return Minion(4, 6, taunt=True)


class CatForm(Card):
    def __init__(self):
        super().__init__("Cat Form", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class BearForm(Card):
    def __init__(self):
        super().__init__("Bear Form", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class DruidOfTheClaw(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, choices=[
            Choice(CatForm(), Transform(CatDruid()), SelfSelector()),
            Choice(BearForm(), Transform(BearDruid()), SelfSelector())
        ])

    def create_minion(self, player):
        return Minion(4, 4)


class AncientSecrets(Card):
    def __init__(self):
        super().__init__("Ancient Secrets", 0, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.SPECIAL)


class AncientTeachings(Card):
    def __init__(self):
        super().__init__("Ancient  Teachings", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class AncientOfLore(MinionCard):
    def __init__(self):

        super().__init__("Ancient of Lore", 7, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC, choices=[
            Choice(AncientSecrets(), Heal(5), HeroSelector()),
            Choice(AncientTeachings(), Draw(3), PlayerSelector())
        ])

    def create_minion(self, player):
        return Minion(5, 5)


class Health(Card):
    def __init__(self):
        super().__init__("+5 Health and Taunt", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class Attack(Card):
    def __init__(self):
        super().__init__("+5 Attack", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class AncientOfWar(MinionCard):
    def __init__(self):

        super().__init__("Ancient of War", 7, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC, choices=[
            Choice(Health(), Give([Aura(ChangeHealth(5), SelfSelector()), Aura(Taunt(), SelfSelector())]),
                   SelfSelector()),
            Choice(Attack(), Give([Aura(ChangeAttack(5), SelfSelector())]), SelfSelector()),
        ])

    def create_minion(self, player):
        return Minion(5, 5)


class IronbarkProtector(MinionCard):
    def __init__(self):
        super().__init__("Ironbark Protector", 8, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(8, 8, taunt=True)


class Treant(MinionCard):
    def __init__(self):
        super().__init__("Treant", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, ref_name="Treant (taunt)")

    def create_minion(self, p):
        return Minion(2, 2, taunt=True)


class IncreaseStats(Card):
    def __init__(self):
        super().__init__("Give your other minions +2/+2 and taunt", 0,
                         CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class SummonTreants(Card):
    def __init__(self):
        super().__init__("Summon two 2/2 Treants with taunt", 0,
                         CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class Cenarius(MinionCard):
    def __init__(self):
        super().__init__("Cenarius", 9, CHARACTER_CLASS.DRUID, CARD_RARITY.LEGENDARY, choices=[
            Choice(IncreaseStats(), Give([Aura(ChangeAttack(2), SelfSelector()),
                                          Aura(ChangeHealth(2), SelfSelector()),
                                          Aura(Taunt(), SelfSelector())]), MinionSelector()),
            Choice(SummonTreants(), Summon(Treant(), 2), PlayerSelector())
        ])

    def create_minion(self, player):
        return Minion(5, 8)


class AttackMode(Card):
    def __init__(self):
        super().__init__("Attack Mode", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class TankMode(Card):
    def __init__(self):
        super().__init__("Tank Mode", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)


class AnodizedRoboCub(MinionCard):
    def __init__(self):
        super().__init__("Anodized Robo Cub", 2, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.MECH,
                         choices=[Choice(AttackMode(), Give([Aura(ChangeAttack(1), SelfSelector())]), SelfSelector()),
                                  Choice(TankMode(), Give([Aura(ChangeHealth(1), SelfSelector())]), SelfSelector())])

    def create_minion(self, player):
        return Minion(2, 2, taunt=True)
