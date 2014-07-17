import hsgame.targeting
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


class CruelTaskmaster(MinionCard):
    def __init__(self):
        super().__init__("Cruel Taskmaster", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         hsgame.targeting.find_minion_battlecry_target)

    def create_minion(self, player):
        def deal_one_damage_and_give_two_attack(minion):
            if minion.card.target is not None:
                minion.card.target.damage(1, self)
                minion.card.target.change_attack(2)

        return Minion(2, 2, battlecry=deal_one_damage_and_give_two_attack)


class FrothingBerserker(MinionCard):
    def __init__(self):
        super().__init__("Frothing Berserker", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def create_minion(self, player):
        def gain_one_attack(m):
            minion.change_attack(1)

        minion = Minion(2, 4)
        player.game.bind("minion_damaged", gain_one_attack)
        minion.bind_once("silenced", lambda: player.game.unbind("minion_damaged", gain_one_attack))
        return minion
