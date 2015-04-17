import copy
from hearthbreaker.cards.base import SpellCard
from hearthbreaker.tags.action import AddCard
from hearthbreaker.tags.base import Effect, BuffUntil, Buff, AuraUntil, ActionTag
from hearthbreaker.tags.condition import IsSpell
from hearthbreaker.tags.event import TurnStarted, TurnEnded, SpellCast
from hearthbreaker.tags.selector import PlayerSelector, CardSelector
from hearthbreaker.tags.status import Stealth, ChangeAttack, ManaChange
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY


class Assassinate(SpellCard):
    def __init__(self):
        super().__init__("Assassinate", 5, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)


class Backstab(SpellCard):
    def __init__(self):
        super().__init__("Backstab", 0, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target,
                         filter_func=lambda target: target.health == target.calculate_max_health() and
                         target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(2), self)


class Betrayal(SpellCard):
    def __init__(self):
        super().__init__("Betrayal", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_enemy_minion_spell_target)

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


class BladeFlurry(SpellCard):
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


class ColdBlood(SpellCard):
    def __init__(self):
        super().__init__("Cold Blood", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        if player.cards_played > 0:
            self.target.change_attack(4)
        else:
            self.target.change_attack(2)


class Conceal(SpellCard):
    def __init__(self):
        super().__init__("Conceal", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for minion in player.minions:
            if not minion.stealth:
                minion.add_buff(BuffUntil(Stealth(), TurnStarted()))


class DeadlyPoison(SpellCard):
    def __init__(self):
        super().__init__("Deadly Poison", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)

        player.hero.weapon.base_attack += 2
        player.hero.change_temp_attack(2)

    def can_use(self, player, game):
        return super().can_use(player, game) and player.hero.weapon is not None


class Eviscerate(SpellCard):
    def __init__(self):
        super().__init__("Eviscerate", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        if player.cards_played > 0:
            self.target.damage(player.effective_spell_damage(4), self)
        else:
            self.target.damage(player.effective_spell_damage(2), self)


class FanOfKnives(SpellCard):
    def __init__(self):
        super().__init__("Fan of Knives", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(1), self)

        player.draw()


class Headcrack(SpellCard):
    def __init__(self):
        super().__init__("Headcrack", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        game.other_player.hero.damage(player.effective_spell_damage(2), self)
        if player.cards_played > 0:
            player.add_effect(Effect(TurnEnded(), ActionTag(AddCard(self), PlayerSelector())))


class Preparation(SpellCard):
    def __init__(self):
        super().__init__("Preparation", 0, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)
        player.add_aura(AuraUntil(ManaChange(-3), CardSelector(condition=IsSpell()), SpellCast()))


class Sap(SpellCard):
    def __init__(self):
        super().__init__("Sap", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.bounce()


class Shadowstep(SpellCard):
    def __init__(self):
        super().__init__("Shadowstep", 0, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.bounce()
        self.target.card.add_buff(Buff(ManaChange(-3)))


class Shiv(SpellCard):
    def __init__(self):
        super().__init__("Shiv", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(1), self)
        player.draw()


class SinisterStrike(SpellCard):
    def __init__(self):
        super().__init__("Sinister Strike", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)

        game.other_player.hero.damage(player.effective_spell_damage(3), self)


class Sprint(SpellCard):
    def __init__(self):
        super().__init__("Sprint", 7, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for i in range(0, 4):
            player.draw()


class Vanish(SpellCard):
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


class TinkersSharpswordOil(SpellCard):
    def __init__(self):
        super().__init__("Tinker's Sharpsword Oil", 4, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        player.hero.weapon.base_attack += 3
        player.hero.change_temp_attack(3)
        if player.cards_played > 0:
            targets = hearthbreaker.targeting.find_friendly_minion_battlecry_target(player.game, lambda x: x)
            if targets is not None:
                target = player.game.random_choice(targets)
                target.add_buff(Buff(ChangeAttack(3)))

    def can_use(self, player, game):
        return super().can_use(player, game) and player.hero.weapon is not None


class Sabotage(SpellCard):
    def __init__(self):
        super().__init__("Sabotage", 4, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)
        targets = hearthbreaker.targeting.find_enemy_minion_battlecry_target(player.game, lambda x: True)
        target = game.random_choice(targets)
        target.die(None)
        game.check_delayed()
        if player.cards_played > 0 and game.other_player.hero.weapon is not None:
            game.other_player.hero.weapon.destroy()

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 1


class GangUp(SpellCard):
    def __init__(self):
        super().__init__("Gang Up", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        for i in range(3):
            player.put_back(type(self.target.card)())
