from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.tags.action import Draw, ChangeAttack, ChangeHealth, Charge, Summon, AddCard
from hearthbreaker.tags.base import Effect, Aura, Deathrattle, CardQuery
from hearthbreaker.tags.condition import MinionIsType
from hearthbreaker.tags.event import MinionPlaced, MinionDied
from hearthbreaker.tags.selector import MinionSelector, SelfSelector, PlayerSelector
from hearthbreaker.game_objects import MinionCard, Minion
import hearthbreaker.targeting


class TimberWolf(MinionCard):
    def __init__(self):
        super().__init__("Timber Wolf", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1, auras=[Aura(ChangeAttack(1), MinionSelector(MinionIsType(MINION_TYPE.BEAST)))])


class Hyena(MinionCard):
    def __init__(self):
        super().__init__("Hyena", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL, minion_type=MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 2, MINION_TYPE.BEAST)


class SavannahHighmane(MinionCard):
    def __init__(self):
        super().__init__("Savannah Highmane", 6, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(6, 5, deathrattle=Deathrattle(Summon(Hyena(), 2), PlayerSelector()))


class Houndmaster(MinionCard):
    def __init__(self):
        super().__init__("Houndmaster", 4, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE, MINION_TYPE.NONE,
                         hearthbreaker.targeting.find_friendly_minion_battlecry_target,
                         lambda m: m.card.minion_type is MINION_TYPE.BEAST)

    def create_minion(self, player):
        def buff_beast(m):
            if self.target is not None:
                self.target.increase_health(2)
                self.target.change_attack(2)
                self.target.taunt = True

        return Minion(4, 3, battlecry=buff_beast)


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
                      effects=[Effect(MinionPlaced(MinionIsType(MINION_TYPE.BEAST)), Draw(), PlayerSelector())])


class TundraRhino(MinionCard):
    def __init__(self):
        super().__init__("Tundra Rhino", 5, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 5, charge=True,
                      auras=[Aura(Charge(), MinionSelector(MinionIsType(MINION_TYPE.BEAST)))])


class ScavengingHyena(MinionCard):
    def __init__(self):
        super().__init__("Scavenging Hyena", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(2, 2,
                      effects=[Effect(MinionDied(MinionIsType(MINION_TYPE.BEAST)), ChangeAttack(2), SelfSelector()),
                               Effect(MinionDied(MinionIsType(MINION_TYPE.BEAST)), ChangeHealth(1), SelfSelector())])


class Webspinner(MinionCard):
    def __init__(self):
        super().__init__("Webspinner", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON, MINION_TYPE.BEAST)

    def create_minion(self, player):
        return Minion(1, 1, deathrattle=Deathrattle(AddCard(CardQuery(conditions=[MinionIsType(MINION_TYPE.BEAST)])),
                                                    PlayerSelector()))
