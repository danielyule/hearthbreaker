import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import MinionCard, Minion, WeaponCard, Weapon
from hearthbreaker.cards.battlecries import change_attack_to_one, give_divine_shield, guardian_of_kings


class AldorPeacekeeper(MinionCard):
    def __init__(self):
        super().__init__("Aldor Peacekeeper", 3, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE,
                         targeting_func=hearthbreaker.targeting.find_enemy_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(3, 3, battlecry=change_attack_to_one)


class ArgentProtector(MinionCard):
    def __init__(self):
        super().__init__("Argent Protector", 2, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(2, 2, battlecry=give_divine_shield)


class GuardianOfKings(MinionCard):
    def __init__(self):
        super().__init__("Guardian of Kings", 7, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(5, 6, battlecry=guardian_of_kings)
        return minion


class TirionFordring(MinionCard):
    def __init__(self):
        super().__init__("Tirion Fordring", 8, CHARACTER_CLASS.PALADIN, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        class Ashbringer(WeaponCard):
            def __init__(self):
                super().__init__("Ashbringer", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.LEGENDARY)

            def create_weapon(self, player):
                weapon = Weapon(5, 3)
                return weapon

        def equip_ashbringer(minion):
            ashbringer = Ashbringer().create_weapon(minion.player)
            ashbringer.equip(minion.player)

        return Minion(6, 6, divine_shield=True, taunt=True, deathrattle=equip_ashbringer)
