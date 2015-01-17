import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import WeaponCard, Weapon
from hearthbreaker.tags.base import Buff
from hearthbreaker.tags.status import ChangeAttack


class EaglehornBow(WeaponCard):
    def __init__(self):
        super().__init__("Eaglehorn Bow", 3, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.RARE)

    def create_weapon(self, player):
        def apply_effect(w, p):
            def increase_durability(s):
                w.durability += 1

            p.bind("secret_revealed", increase_durability)
            w.bind_once("destroyed", lambda: p.unbind("secret_revealed", increase_durability))
            w.bind("copied", apply_effect)
        weapon = Weapon(3, 2)
        apply_effect(weapon, player)
        return weapon


class GladiatorsLongbow(WeaponCard):
    def __init__(self):
        super().__init__("Gladiator's Longbow", 7, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.EPIC)

    def create_weapon(self, player):
        def add_effect(w, p):
            def make_immune(ignored_target):
                p.hero.immune = True

            def end_immune():
                p.hero.immune = False

            def on_destroy():
                p.hero.unbind("attack", make_immune)
                p.hero.unbind("attack_completed", end_immune)
            p.hero.bind("attack", make_immune)
            p.hero.bind("attack_completed", end_immune)
            w.bind_once("destroyed", on_destroy)
            w.bind("copied", add_effect)

        weapon = Weapon(5, 2)
        add_effect(weapon, player)
        return weapon


class Glaivezooka(WeaponCard):
    def __init__(self):
        super().__init__("Glaivezooka", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        def random_buff(w):
            targets = hearthbreaker.targeting.find_friendly_minion_battlecry_target(player.game, lambda x: x)
            if targets is not None:
                target = player.game.random_choice(targets)
                target.add_buff(Buff(ChangeAttack(1)))

        weapon = Weapon(2, 2, battlecry=random_buff)
        return weapon
