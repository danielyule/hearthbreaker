import hearthbreaker.cards
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.effects.minion import ManaFilter, AddCard, Buff, Freeze
from hearthbreaker.effects.player import PlayerManaFilter
from hearthbreaker.game_objects import MinionCard, Minion


class ManaWyrm(MinionCard):
    def __init__(self):
        super().__init__("Mana Wyrm", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 3, effects=[Buff("played", "spell", "self", 1, 0, "friendly")])


class SorcerersApprentice(MinionCard):
    def __init__(self):
        super().__init__("Sorcerer's Apprentice", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 2, effects=[ManaFilter(1, "spell")])


class KirinTorMage(MinionCard):
    def __init__(self):
        super().__init__("Kirin Tor Mage", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        def first_secret_cost_zero(m):
            m.player.add_effect(PlayerManaFilter(100, "secret", "turn_ended", True))

        return Minion(4, 3, battlecry=first_secret_cost_zero)


class EtherealArcanist(MinionCard):
    def __init__(self):
        super().__init__("Ethereal Arcanist", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 3, effects=[Buff("turn_ended", "secret", attack=2, health=2)])


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 6, effects=[Freeze("did_damage", "minion", "other")])


class ArchmageAntonidas(MinionCard):
    def __init__(self):
        super().__init__("Archmage Antonidas", 7, CHARACTER_CLASS.MAGE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(5, 7, effects=[AddCard("played", hearthbreaker.cards.Fireball, "spell", "owner")])
