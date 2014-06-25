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