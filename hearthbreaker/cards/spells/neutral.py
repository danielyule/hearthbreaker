from hearthbreaker.cards.base import SpellCard
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.tags.base import BuffUntil, Buff
from hearthbreaker.tags.event import TurnStarted
from hearthbreaker.tags.status import Stealth, Taunt, Frozen
import hearthbreaker.targeting


class TheCoin(SpellCard):
    def __init__(self):
        super().__init__("The Coin", 0, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)
        if player.mana < 10:
            player.mana += 1


class ArmorPlating(SpellCard):
    def __init__(self):
        super().__init__("Armor Plating", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.increase_health(1)


class EmergencyCoolant(SpellCard):
    def __init__(self):
        super().__init__("Emergency Coolant", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.add_buff(Buff(Frozen()))


class FinickyCloakfield(SpellCard):
    def __init__(self):
        super().__init__("Finicky Cloakfield", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         target_func=hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.add_buff(BuffUntil(Stealth(), TurnStarted()))


class ReversingSwitch(SpellCard):
    def __init__(self):
        super().__init__("Reversing Switch", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        temp_attack = self.target.calculate_attack()
        temp_health = self.target.health
        if temp_attack == 0:
            self.target.die(None)
        else:
            self.target.set_attack_to(temp_health)
            self.target.set_health_to(temp_attack)


class RustyHorn(SpellCard):
    def __init__(self):
        super().__init__("Rusty Horn", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.add_buff(Buff(Taunt()))


class TimeRewinder(SpellCard):
    def __init__(self):
        super().__init__("Time Rewinder", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         target_func=hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.bounce()


class WhirlingBlades(SpellCard):
    def __init__(self):
        super().__init__("Whirling Blades", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(1)


spare_part_list = [ArmorPlating(), EmergencyCoolant(), FinickyCloakfield(), TimeRewinder(), ReversingSwitch(),
                   RustyHorn(), WhirlingBlades()]


class GallywixsCoin(SpellCard):
    def __init__(self):
        super().__init__("Gallywix's Coin", 0, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)
        if player.mana < 10:
            player.mana += 1
