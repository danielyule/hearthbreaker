import hearthbreaker.cards
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.effects import GrowOnSpell, ManaFilter, GrowIfSecret, AddCardOnSpell, FreezeOnDamage
from hearthbreaker.game_objects import MinionCard, Minion


class ManaWyrm(MinionCard):
    def __init__(self):
        super().__init__("Mana Wyrm", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(1, 3, effects=[GrowOnSpell(1, 0)])


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
            m.player.add_card_filter(100, "secret", "turn_ended", True)

        return Minion(4, 3, battlecry=first_secret_cost_zero)


class EtherealArcanist(MinionCard):
    def __init__(self):
        super().__init__("Ethereal Arcanist", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def create_minion(self, player):
        return Minion(3, 3, effects=[GrowIfSecret(2, 2)])


class WaterElemental(MinionCard):
    def __init__(self):
        super().__init__("Water Elemental", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(3, 6, effects=[FreezeOnDamage()])


class ArchmageAntonidas(MinionCard):
    def __init__(self):
        super().__init__("Archmage Antonidas", 7, CHARACTER_CLASS.MAGE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        return Minion(5, 7, effects=[AddCardOnSpell(hearthbreaker.cards.Fireball)])
