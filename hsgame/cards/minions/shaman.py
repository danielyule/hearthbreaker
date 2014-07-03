import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion
from hsgame.cards.battlecries import deal_three_damage, give_windfury


class AlAkirTheWindlord(MinionCard):
    def __init__(self):
        super().__init__("Al'Akir the Windlord", 8, CHARACTER_CLASS.SHAMAN, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        minion = Minion(3, 5)
        minion.windfury = True
        minion.charge = True
        minion.divine_shield = True
        minion.taunt = True
        return minion


class DustDevil(MinionCard):
    def __init__(self):
        super().__init__("Dust Devil", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON, overload=2)

    def create_minion(self, player):
        minion = Minion(3, 1)
        minion.windfury = True
        return minion


class EarthElemental(MinionCard):
    def __init__(self):
        super().__init__("Earth Elemental", 5, CHARACTER_CLASS.SHAMAN, CARD_RARITY.EPIC, overload=3)

    def create_minion(self, player):
        minion = Minion(7, 8)
        minion.taunt = True
        return minion


class FireElemental(MinionCard):
    def __init__(self):
        super().__init__("Fire Elemental", 6, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         hsgame.targeting.find_battlecry_target)

    def create_minion(self, player):
        minion = Minion(6, 5, battlecry=deal_three_damage)
        return minion


class FlametongueTotem(MinionCard):
    def __init__(self):
        super().__init__("Flametongue Totem", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def increase_attack(m):
            m.attack_power += 2
            m.trigger("attack_changed", 2)

        def decrease_attack(m):
            m.attack_power -= 2
            m.trigger("attack_changed", -2)

        def add_effect(m, index):
            m.add_board_effect(increase_attack, decrease_attack,
                               lambda mini: mini.index is m.index - 1 or mini.index is m.index + 1)

        minion = Minion(0, 3, MINION_TYPE.TOTEM)
        minion.bind("added_to_board", add_effect)
        return minion


class ManaTideTotem(MinionCard):
    def __init__(self):
        super().__init__("Mana Tide Totem", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE)

    def create_minion(self, player):
        def draw_card():
            player.draw()

        minion = Minion(0, 3, MINION_TYPE.TOTEM)
        player.bind("turn_ended", draw_card)
        minion.bind_once("silenced", lambda: player.unbind("turn_ended", draw_card))
        return minion


class UnboundElemental(MinionCard):
    def __init__(self):
        super().__init__("Unbound Elemental", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def buff_minion():
            minion.increase_health(1)
            minion.change_attack(1)

        minion = Minion(2, 4)
        player.bind("overloaded", buff_minion)
        minion.bind_once("silenced", lambda: player.unbind("overloaded", buff_minion))
        return minion


class Windspeaker(MinionCard):
    def __init__(self):
        super().__init__("Windspeaker", 4, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         hsgame.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        minion = Minion(3, 3, battlecry=give_windfury)
        return minion
