from hearthbreaker.effects.minion import Buff, Charge
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import MinionCard, Minion, WeaponCard, Weapon


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
        def gain_one_armor(minion, attacker):
            if minion.player is player:
                player.hero.increase_armor(1)

        minion = Minion(1, 4)
        player.bind("minion_damaged", gain_one_armor)
        player.opponent.bind("minion_damaged", gain_one_armor)
        minion.bind_once("silenced", lambda: player.unbind("minion_damaged", gain_one_armor))
        minion.bind_once("silenced", lambda: player.opponent.unbind("minion_damaged", gain_one_armor))
        return minion


class CruelTaskmaster(MinionCard):
    def __init__(self):
        super().__init__("Cruel Taskmaster", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         targeting_func=hearthbreaker.targeting.find_minion_battlecry_target)

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
        minion = Minion(2, 4, effects=[Buff("damaged", "minion", "self", 1, 0, "both", True)])
        return minion


class GrommashHellscream(MinionCard):
    def __init__(self):
        super().__init__("Grommash Hellscream", 8, CHARACTER_CLASS.WARRIOR, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        def increase_attack():
            minion.change_attack(6)

        def decrease_attack():
            minion.change_attack(-6)

        def silenced():
            minion.unbind("enraged", increase_attack)
            minion.unbind("unenraged", decrease_attack)

        minion = Minion(4, 9, charge=True)
        minion.bind("enraged", increase_attack)
        minion.bind("unenraged", decrease_attack)
        minion.bind("silenced", silenced)
        return minion


class KorkronElite(MinionCard):
    def __init__(self):
        super().__init__("Kor'kron Elite", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(4, 3, charge=True)


class WarsongCommander(MinionCard):
    def __init__(self):
        super().__init__("Warsong Commander", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE)

    def create_minion(self, player):
        def give_charge(m):
            if m is not minion and m.calculate_attack() <= 3:
                m.add_effect(Charge())
                m.exhausted = False

        def silence():
            player.unbind("minion_placed", give_charge)

        minion = Minion(2, 3)
        player.bind("minion_placed", give_charge)
        minion.bind_once("silenced", silence)
        return minion
