import hearthbreaker.targeting
from hearthbreaker.tags.base import Buff
from hearthbreaker.tags.status import DivineShield, Taunt
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import WeaponCard, Weapon


class LightsJustice(WeaponCard):
    def __init__(self):
        super().__init__("Light's Justice", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.FREE)

    def create_weapon(self, player):
        weapon = Weapon(1, 4)
        return weapon


class SwordOfJustice(WeaponCard):
    def __init__(self):
        super().__init__("Sword of Justice", 3, CHARACTER_CLASS.PALADIN, CARD_RARITY.EPIC)

    def create_weapon(self, player):
        def buff_minion(minion):
            if minion.player is player:
                minion.increase_health(1)
                minion.change_attack(1)
                weapon.durability -= 1
                if weapon.durability == 0:
                    weapon.destroy()

        def on_destroy():
            player.unbind("minion_summoned", buff_minion)

        weapon = Weapon(1, 5)
        player.bind("minion_summoned", buff_minion)
        weapon.bind_once("destroyed", on_destroy)
        return weapon


class TruesilverChampion(WeaponCard):
    def __init__(self):
        super().__init__("Truesilver Champion", 4, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        def heal(attacker):
            player.hero.heal(player.effective_heal_power(2), self)

        def on_destroy():
            player.hero.unbind("attack", heal)

        weapon = Weapon(4, 2)
        player.hero.bind("attack", heal)
        weapon.bind_once("destroyed", on_destroy)
        return weapon


class Coghammer(WeaponCard):
    def __init__(self):
        super().__init__("Coghammer", 3, CHARACTER_CLASS.PALADIN, CARD_RARITY.EPIC)

    def create_weapon(self, player):
        def random_buff(w):
            targets = hearthbreaker.targeting.find_friendly_minion_battlecry_target(player.game, lambda x: x)
            if targets is not None:
                target = player.game.random_choice(targets)
                target.add_buff(Buff(DivineShield()))
                target.add_buff(Buff(Taunt()))

        weapon = Weapon(2, 3, battlecry=random_buff)
        return weapon
