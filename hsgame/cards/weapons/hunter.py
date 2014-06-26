from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import WeaponCard, Weapon

__author__ = 'Daniel'


class EaglehornBow(WeaponCard):
    def __init__(self):
        super().__init__("Eaglehorn Bow", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

    def create_weapon(self, player):
        def increase_durability(s):
            weapon.durability += 1
        weapon = Weapon(3, 2)
        player.game.players[0].bind("secret_revealed", increase_durability)
        player.game.players[1].bind("secret_revealed", increase_durability)
        weapon.bind_once("destroyed", lambda: player.game.players[0].unbind("secret_revealed", increase_durability))
        weapon.bind_once("destroyed", lambda: player.game.players[1].unbind("secret_revealed", increase_durability))
        return weapon


class GladiatorsLongbow(WeaponCard):
    def __init__(self):
        super().__init__("Gladiator's Longbow", 7, CHARACTER_CLASS.HUNTER, CARD_RARITY.EPIC)

    def create_weapon(self, player):
        def make_immune(ignored_target):
            player.hero.immune = True

        def end_immune():
            player.hero.immune = False

        def on_destroy():
            player.hero.unbind("attack", make_immune)
            player.hero.unbind("attack_complete", end_immune)

        weapon = Weapon(5, 2)
        player.hero.bind("attack", make_immune)
        player.hero.bind("attack_complete", end_immune)
        weapon.bind_once("destroyed", on_destroy)
        return weapon
