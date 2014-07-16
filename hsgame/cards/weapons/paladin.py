from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import WeaponCard, Weapon


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
            player.game.unbind("minion_added", buff_minion)

        weapon = Weapon(1, 5)
        player.game.bind("minion_added", buff_minion)
        weapon.bind_once("destroyed", on_destroy)
        return weapon


class TruesilverChampion(WeaponCard):
    def __init__(self):
        super().__init__("Truesilver Champion", 4, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        def heal(attacker):
            player.hero.heal(2, self)

        def on_destroy():
            player.hero.unbind("attack", heal)

        weapon = Weapon(4, 2)
        player.hero.bind("attack", heal)
        weapon.bind_once("destroyed", on_destroy)
        return weapon
