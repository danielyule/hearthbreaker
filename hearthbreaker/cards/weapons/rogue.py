import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import WeaponCard, Weapon


class AssassinsBlade(WeaponCard):
    def __init__(self):
        super().__init__("Assassin's Blade", 5, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def create_weapon(self, player):
        weapon = Weapon(3, 4)
        return weapon


class PerditionsBlade(WeaponCard):
    def __init__(self):
        super().__init__("Perdition's Blade", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE,
                         hearthbreaker.targeting.find_battlecry_target)

    def create_weapon(self, player):
        def deal_damage(w):
            if w.card.target is not None:
                if player.cards_played > 0:
                    w.card.target.damage(2, self)
                else:
                    w.card.target.damage(1, self)

        weapon = Weapon(2, 2, battlecry=deal_damage)
        return weapon
