from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.tags.action import Draw, Summon, AddCard, Give
from hearthbreaker.tags.base import Effect, Aura, Deathrattle, CardQuery, Battlecry
from hearthbreaker.tags.condition import IsType
from hearthbreaker.tags.event import MinionPlaced, MinionDied
from hearthbreaker.tags.selector import MinionSelector, SelfSelector, PlayerSelector, UserPicker
from hearthbreaker.game_objects import MinionCard, Minion
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth, Charge, Taunt


class TimberWolf(MinionCard):
    def __init__(self):
        super().__init__("Timber Wolf", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1, auras=[Aura(ChangeAttack(1), MinionSelector(IsType(MINION_TYPE.BEAST)))])


class Hyena(MinionCard):
    def __init__(self):
        super().__init__("Hyena", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 2)


class SavannahHighmane(MinionCard):
    def __init__(self):
        super().__init__("Savannah Highmane", 6, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(6, 5, deathrattle=Deathrattle(Summon(Hyena(), 2), PlayerSelector()))


class Houndmaster(MinionCard):
    def __init__(self):
        super().__init__("Houndmaster", 4, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE, MINION_TYPE.NONE,
                         battlecry=Battlecry(Give([Aura(ChangeHealth(2), SelfSelector()),
                                                   Aura(ChangeAttack(2), SelfSelector()),
                                                   Aura(Taunt(), SelfSelector())]),
                                             MinionSelector(IsType(MINION_TYPE.BEAST), picker=UserPicker())))

    def create_minion(self, player):
        return Minion(4, 3)


class KingKrush(MinionCard):
    def __init__(self):
        super().__init__("King Krush", 9, CHARACTER_CLASS.HUNTER, CARD_RARITY.LEGENDARY, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(8, 8, charge=True)


class StarvingBuzzard(MinionCard):
    def __init__(self):
        super().__init__("Starving Buzzard", 5, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(3, 2,
                      effects=[Effect(MinionPlaced(IsType(MINION_TYPE.BEAST)), Draw(), PlayerSelector())])


class TundraRhino(MinionCard):
    def __init__(self):
        super().__init__("Tundra Rhino", 5, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 5, charge=True,
                      auras=[Aura(Charge(), MinionSelector(IsType(MINION_TYPE.BEAST)))])


class ScavengingHyena(MinionCard):
    def __init__(self):
        super().__init__("Scavenging Hyena", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 2,
                      effects=[Effect(MinionDied(IsType(MINION_TYPE.BEAST)), ChangeAttack(2), SelfSelector()),
                               Effect(MinionDied(IsType(MINION_TYPE.BEAST)), ChangeHealth(1), SelfSelector())])


class Webspinner(MinionCard):
    def __init__(self):
        super().__init__("Webspinner", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1, deathrattle=Deathrattle(AddCard(CardQuery(conditions=[IsType(MINION_TYPE.BEAST)])),
                                                    PlayerSelector()))


class Hound(MinionCard):
    def __init__(self):
        super().__init__("Hound", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1, charge=True)


class Huffer(MinionCard):
    def __init__(self):
        super().__init__("Huffer", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(4, 2, charge=True)


class Misha(MinionCard):
    def __init__(self):
        super().__init__("Misha", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(4, 4, taunt=True)


class Leokk(MinionCard):
    def __init__(self):
        super().__init__("Leokk", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 4, auras=[Aura(ChangeAttack(1), MinionSelector())])


class Snake(MinionCard):
    def __init__(self):
        super().__init__("Snake", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1)
