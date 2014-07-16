from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion
import hsgame.targeting


class TimberWolf(MinionCard):
    def __init__(self):
        super().__init__("Timber Wolf", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.FREE)

    def create_minion(self, player):

        def add_effect(m, index):
            m.add_aura(1, 0, [player], lambda mini: mini is not minion and mini.minion_type is MINION_TYPE.BEAST)

        minion = Minion(1, 1, MINION_TYPE.BEAST)
        minion.bind("added_to_board", add_effect)
        return minion


class SavannahHighmane(MinionCard):
    def __init__(self):
        super().__init__("Savannah Highmane", 6, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

    def create_minion(self, player):
        def summon_hyenas(m):
            class Hyena(MinionCard):
                def __init__(self):
                    super().__init__("Hyena", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(2, 2, MINION_TYPE.BEAST)

            Hyena().summon(player, player.game, m.index)
            Hyena().summon(player, player.game, m.index)

        return Minion(6, 5, MINION_TYPE.BEAST, deathrattle=summon_hyenas)


class Houndmaster(MinionCard):
    def __init__(self):
        super().__init__("Houndmaster", 4, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE,
                         hsgame.targeting.find_friendly_minion_battlecry_target,
                         lambda m: m.minion_type is MINION_TYPE.BEAST)

    def create_minion(self, player):
        def buff_beast(m):
            if self.target is not None:
                self.target.increase_health(2)
                self.target.change_attack(2)
                self.target.taunt = True

        return Minion(4, 3, battlecry=buff_beast)


class KingKrush(MinionCard):
    def __init__(self):
        super().__init__("King Krush", 9, CHARACTER_CLASS.HUNTER, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        minion = Minion(8, 8, MINION_TYPE.BEAST)
        minion.charge = True
        return minion