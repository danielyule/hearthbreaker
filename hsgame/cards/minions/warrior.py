from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import MinionCard, Minion, WeaponCard, Weapon


class ArathiWeaponsmith(MinionCard):
    def __init__(self):
        super().__init__("Arathi Weaponsmith", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_minion(self, player):
        class BattleAxe(WeaponCard):
            def __init__(self):
                super().__init__("Battle Axe", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.SPECIAL)

            def create_weapon(self, player):
                return Weapon(2, 2)

        def equip_battle_axe(minion):
            battle_axe = BattleAxe().create_weapon(player)
            battle_axe.equip(player)

        return Minion(3, 3, battlecry=equip_battle_axe)


class Armorsmith(MinionCard):
    def __init__(self):
        super().__init__("Armorsmith", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def create_minion(self, player):
        def gain_one_armor(minion):
            if minion.player is player:
                player.hero.increase_armor(1)

        minion = Minion(1, 4)
        player.game.bind("minion_damaged", gain_one_armor)
        minion.bind_once("silenced", lambda: player.game.unbind("minion_damaged", gain_one_armor))
        return minion
