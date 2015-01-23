import copy
from hearthbreaker.tags.aura import ManaAura
from hearthbreaker.tags.base import BuffUntil
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import CurrentPlayer, SpecificCardSelector
from hearthbreaker.tags.status import Immune
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Card, SecretCard, Minion, Hero


class HuntersMark(Card):
    def __init__(self):
        super().__init__("Hunter's Mark", 0, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.set_health_to(1)


class ArcaneShot(Card):
    def __init__(self):
        super().__init__("Arcane Shot", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(2), self)


class BestialWrath(Card):
    def __init__(self):
        super().__init__("Bestial Wrath", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.EPIC,
                         hearthbreaker.targeting.find_minion_spell_target,
                         lambda minion: minion.card.minion_type is MINION_TYPE.BEAST and minion.spell_targetable())

    def use(self, player, game):
        super().use(player, game)
        self.target.add_buff(BuffUntil(Immune(), TurnEnded(player=CurrentPlayer())))
        self.target.change_temp_attack(2)


class Flare(Card):
    def __init__(self):
        super().__init__("Flare", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        for minion in hearthbreaker.targeting.find_minion_spell_target(game, lambda m: m.stealth):
            minion.stealth = False

        for secret in game.other_player.secrets:
            secret.deactivate(game.other_player)

        game.other_player.secrets = []
        player.draw()


class Tracking(Card):
    def __init__(self):
        super().__init__("Tracking", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        cards = []
        for card_index in range(0, 3):
            if player.can_draw():
                cards.append(player.deck.draw(game))
        if len(cards) > 0:
            chosen_card = player.agent.choose_option(*cards)
            player.hand.append(chosen_card)
            player.trigger("card_drawn", chosen_card)


class ExplosiveTrap(SecretCard):
    def __init__(self):
        super().__init__("Explosive Trap", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def activate(self, player):
        player.opponent.bind("character_attack", self._reveal)

    def deactivate(self, player):
        player.opponent.unbind("character_attack", self._reveal)

    def _reveal(self, attacker, target):
        if isinstance(target, Hero):
            game = attacker.player.game
            enemies = copy.copy(game.current_player.minions)
            enemies.append(game.current_player.hero)
            for enemy in enemies:
                enemy.damage(2, None)
            game.check_delayed()
            super().reveal()


class FreezingTrap(SecretCard):
    def __init__(self):
        super().__init__("Freezing Trap", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def activate(self, player):
        player.game.current_player.bind("character_attack", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("character_attack", self._reveal)

    def _reveal(self, attacker, target):
        if isinstance(attacker, Minion) and not attacker.removed:
            attacker.bounce()
            attacker.player.add_aura(ManaAura(-2, 0, SpecificCardSelector(attacker.card), True, False))
            super().reveal()


class Misdirection(SecretCard):
    def __init__(self):
        super().__init__("Misdirection", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

    def activate(self, player):
        player.opponent.bind("character_attack", self._reveal)

    def deactivate(self, player):
        player.opponent.unbind("character_attack", self._reveal)

    def _reveal(self, character, target):
        if isinstance(target, Hero) and not character.removed:
            game = character.player.game

            def choose_random(targets):
                possibilities = copy.copy(game.current_player.minions)
                possibilities.extend(game.other_player.minions)
                possibilities.append(game.current_player.hero)
                possibilities.append(game.other_player.hero)
                old_target = old_target_func(targets)
                possibilities.remove(old_target)
                game.current_player.agent.choose_target = old_target_func
                return game.random_choice(possibilities)

            old_target_func = game.current_player.agent.choose_target
            game.current_player.agent.choose_target = choose_random
            super().reveal()


class Snipe(SecretCard):
    def __init__(self):
        super().__init__("Snipe", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def activate(self, player):
        player.game.current_player.bind("minion_played", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("minion_played", self._reveal)

    def _reveal(self, minion):
        minion.damage(4, None)
        super().reveal()


class DeadlyShot(Card):
    def __init__(self):
        super().__init__("Deadly Shot", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        targets = hearthbreaker.targeting.find_enemy_minion_battlecry_target(player.game, lambda x: True)
        target = game.random_choice(targets)
        target.die(None)
        game.check_delayed()

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 1


class MultiShot(Card):
    def __init__(self):
        super().__init__("Multi-Shot", 4, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)

        targets = copy.copy(game.other_player.minions)
        for i in range(0, 2):
            target = game.random_choice(targets)
            targets.remove(target)
            target.damage(player.effective_spell_damage(3), self)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 2


class ExplosiveShot(Card):
    def __init__(self):
        super().__init__("Explosive Shot", 5, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        index = self.target.index
        if self.target.index < len(self.target.player.minions) - 1:
            minion = self.target.player.minions[index + 1]
            minion.damage(player.effective_spell_damage(2), self)

        self.target.damage(player.effective_spell_damage(5), self)

        if self.target.index > 0:
            minion = self.target.player.minions[index - 1]
            minion.damage(player.effective_spell_damage(2), self)


class KillCommand(Card):
    def __init__(self):
        super().__init__("Kill Command", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        beasts = hearthbreaker.targeting.find_friendly_minion_battlecry_target(
            player.game, lambda x: x.card.minion_type is MINION_TYPE.BEAST)
        if beasts is None:
            self.target.damage(player.effective_spell_damage(3), self)
        else:
            self.target.damage(player.effective_spell_damage(5), self)


class UnleashTheHounds(Card):
    def __init__(self):
        super().__init__("Unleash the Hounds", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for target in hearthbreaker.targeting.find_enemy_minion_spell_target(player.game, lambda x: True):
            hound = hearthbreaker.cards.minions.hunter.Hound()
            hound.summon(player, game, len(player.minions))


class AnimalCompanion(Card):
    def __init__(self):
        super().__init__("Animal Companion", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        beast_list = [hearthbreaker.cards.minions.hunter.Huffer(), hearthbreaker.cards.minions.hunter.Misha(),
                      hearthbreaker.cards.minions.hunter.Leokk()]
        card = game.random_choice(beast_list)
        card.summon(player, player.game, len(player.minions))


class SnakeTrap(SecretCard):
    def __init__(self):
        super().__init__("Snake Trap", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.EPIC)

    def activate(self, player):
        player.game.current_player.bind("character_attack", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("character_attack", self._reveal)

    def _reveal(self, attacker, target):
        if isinstance(target, Minion):
            snake = hearthbreaker.cards.minions.hunter.Snake()
            player = target.player.game.other_player
            for i in range(0, 3):
                snake.summon(player, player.game, len(player.minions))
            super().reveal()


class CallPet(Card):
    def __init__(self):
        super().__init__("Call Pet", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

    def use(self, player, game):
        def reduce_cost(card):
            if card.is_minion() and card.minion_type == MINION_TYPE.BEAST:
                nonlocal aura
                aura = ManaAura(4, 0, SpecificCardSelector(card), True, False)

        super().use(player, game)
        aura = None
        player.bind_once("card_drawn", reduce_cost)
        player.draw()
        if aura is not None:
            player.add_aura(aura)


class CobraShot(Card):
    def __init__(self):
        super().__init__("Cobra Shot", 5, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(3), self)
        game.other_player.hero.damage(player.effective_spell_damage(3), self)
