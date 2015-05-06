from hearthbreaker.cards.base import MinionCard, ChoiceCard
from hearthbreaker.game_objects import Minion
from hearthbreaker.tags.action import Give, Damage, Silence, Transform, Draw, Heal, \
    Summon, AddCard, GiveManaCrystal, Remove, Kill
from hearthbreaker.tags.base import Choice, Buff, Effect, CardQuery, CARD_SOURCE, Battlecry, Deathrattle, ActionTag
from hearthbreaker.tags.condition import IsType, GreaterThan
from hearthbreaker.tags.event import Damaged, TurnEnded
from hearthbreaker.tags.selector import CharacterSelector, MinionSelector, SelfSelector, UserPicker, BothPlayer, \
    PlayerSelector, HeroSelector, Count, DeadMinionSelector
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth, Taunt, ManaChange
from hearthbreaker.cards.spells.neutral import spare_part_list


class Moonfire(ChoiceCard):
    def __init__(self):
        super().__init__("Moonfire", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, ref_name="moonfire_keeper")


class Dispel(ChoiceCard):
    def __init__(self):
        super().__init__("Dispel", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


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
        super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False, MINION_TYPE.BEAST,
                         ref_name="Druid of the Claw (cat)")

    def create_minion(self, p):
        return Minion(4, 4, charge=True)


class BearDruid(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False, MINION_TYPE.BEAST,
                         ref_name="Druid of the Claw (bear)")

    def create_minion(self, p):
        return Minion(4, 6, taunt=True)


class CatForm(ChoiceCard):
    def __init__(self):
        super().__init__("Cat Form", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class BearForm(ChoiceCard):
    def __init__(self):
        super().__init__("Bear Form", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class DruidOfTheClaw(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, choices=[
            Choice(CatForm(), Transform(CatDruid()), SelfSelector()),
            Choice(BearForm(), Transform(BearDruid()), SelfSelector())
        ])

    def create_minion(self, player):
        return Minion(4, 4)


class AncientSecrets(ChoiceCard):
    def __init__(self):
        super().__init__("Ancient Secrets", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class AncientTeachings(ChoiceCard):
    def __init__(self):
        super().__init__("Ancient Teachings", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class AncientOfLore(MinionCard):
    def __init__(self):

        super().__init__("Ancient of Lore", 7, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC, choices=[
            Choice(AncientSecrets(), Heal(5), HeroSelector()),
            Choice(AncientTeachings(), Draw(3), PlayerSelector())
        ])

    def create_minion(self, player):
        return Minion(5, 5)


class Health(ChoiceCard):
    def __init__(self):
        super().__init__("Rooted", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class Attack(ChoiceCard):
    def __init__(self):
        super().__init__("Uproot", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class AncientOfWar(MinionCard):
    def __init__(self):

        super().__init__("Ancient of War", 7, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC, choices=[
            Choice(Health(), Give([Buff(ChangeHealth(5)), Buff(Taunt())]), SelfSelector()),
            Choice(Attack(), Give([Buff(ChangeAttack(5))]), SelfSelector()),
        ])

    def create_minion(self, player):
        return Minion(5, 5)


class IronbarkProtector(MinionCard):
    def __init__(self):
        super().__init__("Ironbark Protector", 8, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(8, 8, taunt=True)


class TauntTreant(MinionCard):
    def __init__(self):
        super().__init__("Treant", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, ref_name="Treant (taunt)")

    def create_minion(self, p):
        return Minion(2, 2, taunt=True)


class Treant(MinionCard):
    def __init__(self):
        super().__init__("Treant", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)

    def create_minion(self, _):
        return Minion(2, 2)


class ChargeTreant(MinionCard):
    def __init__(self):
        super().__init__("Treant", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False, ref_name="Treant (charge)")

    def create_minion(self, player):
        return Minion(2, 2, charge=True, effects=[Effect(TurnEnded(), ActionTag(Kill(), SelfSelector()))])


class PoisonSeedsTreant(MinionCard):
    def __init__(self):
        super().__init__("Treant", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False,
                         ref_name="Treant (poison seeds)")

    def create_minion(self, player):
        return Minion(2, 2)


class Panther(MinionCard):
    def __init__(self):
        super().__init__("Panther", 2, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False, MINION_TYPE.BEAST)

    def create_minion(self, _):
        return Minion(3, 2, MINION_TYPE.BEAST)


class IncreaseStats(ChoiceCard):
    def __init__(self):
        super().__init__("Give your other minions +2/+2 and taunt", 0,
                         CHARACTER_CLASS.DRUID, CARD_RARITY.LEGENDARY, False)


class SummonTreants(ChoiceCard):
    def __init__(self):
        super().__init__("Summon two 2/2 Treants with taunt", 0,
                         CHARACTER_CLASS.DRUID, CARD_RARITY.LEGENDARY, False)


class Cenarius(MinionCard):
    def __init__(self):
        super().__init__("Cenarius", 9, CHARACTER_CLASS.DRUID, CARD_RARITY.LEGENDARY, choices=[
            Choice(IncreaseStats(), Give([Buff(ChangeAttack(2)),
                                          Buff(ChangeHealth(2)),
                                          Buff(Taunt())]), MinionSelector()),
            Choice(SummonTreants(), Summon(TauntTreant(), 2), PlayerSelector())
        ])

    def create_minion(self, player):
        return Minion(5, 8)


class AttackMode(ChoiceCard):
    def __init__(self):
        super().__init__("Attack Mode", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class TankMode(ChoiceCard):
    def __init__(self):
        super().__init__("Tank Mode", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class AnodizedRoboCub(MinionCard):
    def __init__(self):
        super().__init__("Anodized Robo Cub", 2, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         minion_type=MINION_TYPE.MECH,
                         choices=[Choice(AttackMode(), Give([Buff(ChangeAttack(1))]), SelfSelector()),
                                  Choice(TankMode(), Give([Buff(ChangeHealth(1))]), SelfSelector())])

    def create_minion(self, player):
        return Minion(2, 2, taunt=True)


class MechBearCat(MinionCard):
    def __init__(self):
        super().__init__("Mech-Bear-Cat", 6, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE, minion_type=MINION_TYPE.MECH)

    def create_minion(self, player):
        return Minion(7, 6, effects=[Effect(Damaged(),
                                     ActionTag(AddCard(CardQuery(source=CARD_SOURCE.LIST, source_list=spare_part_list)),
                                     PlayerSelector()))])


class CobraForm(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Fang", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False, MINION_TYPE.BEAST,
                         ref_name="Druid of the Fang (cobra)")

    def create_minion(self, player):
        return Minion(7, 7)


class DruidOfTheFang(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Fang", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         battlecry=Battlecry(Transform(CobraForm()), SelfSelector(),
                                             GreaterThan(Count(MinionSelector(IsType(MINION_TYPE.BEAST))), value=0)))

    def create_minion(self, player):
        return Minion(4, 4)


class Malorne(MinionCard):
    def __init__(self):
        super().__init__("Malorne", 7, CHARACTER_CLASS.DRUID, CARD_RARITY.LEGENDARY, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(9, 7, deathrattle=[Deathrattle(AddCard(CardQuery(source=CARD_SOURCE.MINION,
                                                                       minion=SelfSelector()),
                                                             add_to_deck=True), PlayerSelector()),
                                         Deathrattle(Remove(), SelfSelector())])


class GiftOfMana(ChoiceCard):
    def __init__(self):
        super().__init__("Gift of Mana", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE)


class GiftOfCards(ChoiceCard):
    def __init__(self):
        super().__init__("Gift of Cards", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE)


class GroveTender(MinionCard):
    def __init__(self):
        super().__init__("Grove Tender", 3, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE, choices=[
            Choice(GiftOfMana(), GiveManaCrystal(), PlayerSelector(players=BothPlayer())),
            Choice(GiftOfCards(), Draw(), PlayerSelector(players=BothPlayer()))
        ])

    def create_minion(self, player):
        return Minion(2, 4)


class FlameCat(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Flame", 3, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False, MINION_TYPE.BEAST,
                         ref_name="Druid of the Flame (cat)")

    def create_minion(self, p):
        return Minion(5, 2)


class FlameBird(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Flame", 3, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False, MINION_TYPE.BEAST,
                         ref_name="Druid of the Flame (bird)")

    def create_minion(self, p):
        return Minion(2, 5)


class FlameCatForm(ChoiceCard):
    def __init__(self):
        super().__init__("Flame Cat Form", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class FlameBirdForm(ChoiceCard):
    def __init__(self):
        super().__init__("Flame Bird Form", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class DruidOfTheFlame(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Flame", 3, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, choices=[
            Choice(FlameCatForm(), Transform(FlameCat()), SelfSelector()),
            Choice(FlameBirdForm(), Transform(FlameBird()), SelfSelector())
        ])

    def create_minion(self, player):
        return Minion(2, 2)


class VolcanicLumberer(MinionCard):
    def __init__(self):
        super().__init__("Volcanic Lumberer", 9, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE,
                         buffs=[Buff(ManaChange(Count(DeadMinionSelector(players=BothPlayer())), -1))])

    def create_minion(self, player):
        return Minion(7, 8, taunt=True)
