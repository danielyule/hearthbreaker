import copy
from hearthbreaker.tags.action import AddCard
from hearthbreaker.tags.aura import ManaAura
from hearthbreaker.tags.base import Effect, BuffUntil
from hearthbreaker.tags.event import TurnStarted, TurnEnded
from hearthbreaker.tags.selector import PlayerSelector, SpellSelector, SpecificCardSelector
from hearthbreaker.tags.status import Stealth
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import Card


class Assassinate(Card):
    def __init__(self):
        super().__init__("Assassinate", 5, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)


class Backstab(Card):
    def __init__(self):
        super().__init__("Backstab", 0, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target,
                         lambda target: target.health == target.calculate_max_health() and target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(2), self)


class Betrayal(Card):
    def __init__(self):
        super().__init__("Betrayal", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        left_minion = None
        right_minion = None

        index = self.target.index
        if index > 0:
            left_minion = game.other_player.minions[index - 1]
        if index < min(len(game.other_player.minions) - 1, 6):
            right_minion = game.other_player.minions[index + 1]

        original_immune = self.target.immune
        self.target.immune = True
        if left_minion is not None:
            left_minion.damage(self.target.calculate_attack(), self.target)
        if right_minion is not None:
            right_minion.damage(self.target.calculate_attack(), self.target)
        self.target.immune = original_immune


class BladeFlurry(Card):
    def __init__(self):
        super().__init__("Blade Flurry", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)

        if player.hero.weapon is not None:
            # Yes, this card is affected by spell damage cards.
            # Source: http://www.hearthhead.com/card=1064/blade-flurry#comments:id=1927317
            attack_power = player.effective_spell_damage(player.hero.calculate_attack())
            player.hero.weapon.destroy()

            for minion in copy.copy(game.other_player.minions):
                minion.damage(attack_power, self)

            game.other_player.hero.damage(attack_power, self)


class ColdBlood(Card):
    def __init__(self):
        super().__init__("Cold Blood", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        if player.cards_played > 0:
            self.target.change_attack(4)
        else:
            self.target.change_attack(2)


class Conceal(Card):
    def __init__(self):
        super().__init__("Conceal", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for minion in player.minions:
            if not minion.stealth:
                minion.add_buff(BuffUntil(Stealth(), TurnStarted()))


class DeadlyPoison(Card):
    def __init__(self):
        super().__init__("Deadly Poison", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)

        player.hero.weapon.base_attack += 2
        player.hero.change_temp_attack(2)

    def can_use(self, player, game):
        return super().can_use(player, game) and player.hero.weapon is not None


class Eviscerate(Card):
    def __init__(self):
        super().__init__("Eviscerate", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        if player.cards_played > 0:
            self.target.damage(player.effective_spell_damage(4), self)
        else:
            self.target.damage(player.effective_spell_damage(2), self)


class FanOfKnives(Card):
    def __init__(self):
        super().__init__("Fan of Knives", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(1), self)

        player.draw()


class Headcrack(Card):
    def __init__(self):
        super().__init__("Headcrack", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        game.other_player.hero.damage(player.effective_spell_damage(2), self)
        if player.cards_played > 0:
            player.add_effect(Effect(TurnEnded(), AddCard(self), PlayerSelector()))


class Preparation(Card):
    def __init__(self):
        super().__init__("Preparation", 0, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)
        player.add_aura(ManaAura(100, 0, SpellSelector(), True))


class Sap(Card):
    def __init__(self):
        super().__init__("Sap", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.bounce()


class Shadowstep(Card):
    def __init__(self):
        super().__init__("Shadowstep", 0, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.bounce()
        player.add_aura(ManaAura(3, 0, SpecificCardSelector(self.target.card), True, False))


class Shiv(Card):
    def __init__(self):
        super().__init__("Shiv", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(1), self)
        player.draw()


class SinisterStrike(Card):
    def __init__(self):
        super().__init__("Sinister Strike", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)

        game.other_player.hero.damage(player.effective_spell_damage(3), self)


class Sprint(Card):
    def __init__(self):
        super().__init__("Sprint", 7, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for i in range(0, 4):
            player.draw()


class Vanish(Card):
    def __init__(self):
        super().__init__("Vanish", 6, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        targets = copy.copy(game.other_player.minions)
        targets.extend(player.minions)

        # Minions are returned to a player's hand in the order in which they were played.
        # Source: http://www.hearthhead.com/card=196/vanish#comments:id=1908549
        for minion in sorted(targets, key=lambda m: m.born):
            minion.bounce()
