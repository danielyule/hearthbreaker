import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import MinionCard, Minion
from hsgame.cards.battlecries import take_control_of_minion, give_three_health

__author__ = 'Daniel'


class AlAkirTheWindlord(MinionCard):
    def __init__(self):
        super().__init__("Al'Akir the Windlord", 8, CHARACTER_CLASS.SHAMAN, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):                    
        minion = Minion(3, 5)
        minion.wind_fury = True
        minion.charge = True
        minion.divine_shield = True
        minion.taunt = True
        return minion