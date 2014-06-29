import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import MinionCard, Minion
from hsgame.cards.battlecries import change_attack_to_one, \
    give_divine_shield, guardian_of_kings

__author__ = 'Daniel'


class AldorPeacekeeper(MinionCard):
    def __init__(self):
        super().__init__("Aldor Peacekeeper", 3, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.RARE,
                         hsgame.targeting.find_enemy_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(3, 3, battlecry=change_attack_to_one)


class ArgentProtector(MinionCard):
    def __init__(self):
        super().__init__("Argent Protector", 2, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.COMMON,
                         hsgame.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(2, 2, battlecry=give_divine_shield)


class GuardianOfKings(MinionCard):
    def __init__(self):
        super().__init__("Guardian of Kings", 7, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(5, 6, battlecry=guardian_of_kings)
        return minion
