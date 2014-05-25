import hsgame.targetting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion, Card
from hsgame.cards.battlecries import change_attack_to_one, give_divine_shield

__author__ = 'Daniel'


class AldorPeacekeeper(MinionCard):
    def __init__(self):
        super().__init__("Aldor Peacekeeper", 3, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE, hsgame.targetting.find_enemy_minion_battlecry_target)

    def create_minion(self, player):
        minion = Minion(3, 3)
        minion.bind("added_to_board", change_attack_to_one)
        return minion
    
class ArgentProtector(MinionCard):
    def __init__(self):
        super().__init__("Argent Protector", 2, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON, hsgame.targetting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        minion = Minion(2, 2)
        minion.bind("added_to_board", give_divine_shield)
        return minion
    
class GuardianOfKings(MinionCard):
    def __init__(self):
        super().__init__("Guardian of Kings", 7, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(5, 6)
        player.hero.heal(6)
        return minion