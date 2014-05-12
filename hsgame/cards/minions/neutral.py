from hsgame.cards.battlecries import draw_card, silence, deal_one_damage
from hsgame.game_objects import Minion, MinionCard
from hsgame.constants import CARD_RARITY, CHARACTER_CLASS, MINION_TYPE
import hsgame.targetting
__author__ = 'Daniel'


class BloodfenRaptor(MinionCard):
    def __init__(self):
        super().__init__("Bloodfen Raptor", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(3, 2, MINION_TYPE.BEAST)


class ElvenArcher(MinionCard):
    def __init__(self):
        super().__init__("Elven Archer", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, True, hsgame.targetting.find_battlecry_target)

    def create_minion(self, player):
        minion = Minion(1, 1)
        minion.bind("added_to_board", deal_one_damage)
        return minion

class NoviceEngineer(MinionCard):
    def __init__(self):
        super().__init__("Novice Engineer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(1, 1)
        minion.bind('added_to_board', draw_card)
        return minion

class StonetuskBoar(MinionCard):
    def __init__(self):
        super().__init__("Stonetusk Boar", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(1, 1, MINION_TYPE.BEAST)
        minion.charge = True
        return minion

class IronbeakOwl(MinionCard):
    def __init__(self):
        super().__init__("Ironbeak Owl", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, True, hsgame.targetting.find_minion_battlecry_target)

    def create_minion(self, player):
        minion = Minion(2, 1, MINION_TYPE.BEAST)
        minion.bind('added_to_board', silence)
        return minion


class WarGolem(MinionCard):
    def __init__(self):
        super().__init__("War Golem", 7, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(7, 7)


class MogushanWarden(MinionCard):
    def __init__(self):
        super().__init__("Mogu'shan Warden", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(1, 7)
        minion.taunt = True
        return minion


class OasisSnapjaw(MinionCard):
    def __init__(self):
        super().__init__("Oasis Snapjaw", 4, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(2, 7, MINION_TYPE.BEAST)


class FaerieDragon(MinionCard):
    def __init__(self):
        super().__init__("Faerie Dragon", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def silence():
            minion.spell_targettable = lambda : True
        minion = Minion(3, 2, MINION_TYPE.DRAGON)
        minion.spell_targettable = lambda: False
        minion.bind("silenced", silence())
        return minion


class KoboldGeomancer(MinionCard):

    def __init__(self):
        super().__init__("Kobold Geomancer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(2, 2)
        minion.spell_power = 1
        return minion


class IronfurGrizzly(MinionCard):

    def __init__(self):
        super().__init__("Ironfur Grizzly", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(3, 3)
        minion.taunt = True
        return minion