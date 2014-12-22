from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import Card
from hearthbreaker.tags.base import Aura, AuraUntil
from hearthbreaker.tags.event import TurnStarted
from hearthbreaker.tags.selector import SelfSelector
from hearthbreaker.tags.status import Stealth, Taunt
import hearthbreaker.targeting


class ArmorPlating(Card):
    def __init__(self):
        super().__init__("Armor Plating", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.increase_health(1)


class EmergencyCoolant(Card):
    def __init__(self):
        super().__init__("Emergency Coolant", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.freeze()


class FinickyCloakfield(Card):
    def __init__(self):
        super().__init__("Finicky Cloakfield", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                         hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.add_aura(AuraUntil(Stealth(), SelfSelector(), TurnStarted()))


class ReversingSwitch(Card):
    def __init__(self):
        super().__init__("Reversing Switch", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        temp_attack = self.target.calculate_attack()
        temp_health = self.target.health
        if temp_attack == 0:
            self.target.die(None)
        else:
            self.target.set_attack_to(temp_health)
            self.target.set_health_to(temp_attack)


class RustyHorn(Card):
    def __init__(self):
        super().__init__("Rusty Horn", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.add_aura(Aura(Taunt(), SelfSelector()))


class TimeRewinder(Card):
    def __init__(self):
        super().__init__("Time Rewinder", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                         hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.bounce()


class WhirlingBlades(Card):
    def __init__(self):
        super().__init__("Whirling Blades", 1, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(1)
