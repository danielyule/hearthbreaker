import copy
from hearthbreaker.effects import Immune
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Card, SecretCard, Minion, MinionCard


class HuntersMark(Card):
    def __init__(self):
        super().__init__("Hunter's Mark", 0, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.decrease_health(self.target.base_health - 1)


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

        self.target.add_effect(Immune())
        self.target.change_temp_attack(2)


class Flare(Card):
    def __init__(self):
        super().__init__("Flare", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

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
                cards.append(player.deck.draw(game.random))
        if len(cards) > 0:
            chosen_card = player.agent.choose_option(*cards)
            player.hand.append(chosen_card)
            player.trigger("card_drawn", chosen_card)


class ExplosiveTrap(SecretCard):
    def __init__(self):
        super().__init__("Explosive Trap", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def activate(self, player):
        player.hero.bind_once("attacked", self._reveal)

    def deactivate(self, player):
        player.hero.unbind("attacked", self._reveal)

    def _reveal(self, minion):
        enemies = copy.copy(minion.game.current_player.minions)
        enemies.append(minion.game.current_player.hero)
        for enemy in enemies:
            enemy.damage(2, None)
        minion.game.check_delayed()
        super().reveal()


class FreezingTrap(SecretCard):
    def __init__(self):
        super().__init__("Freezing Trap", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def activate(self, player):
        player.game.current_player.bind_once("pre_attack", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("pre_attack", self._reveal)

    def _reveal(self, attacker):
        if isinstance(attacker, Minion) and not attacker.removed:
            class Filter:
                def __init__(self):
                    self.amount = -2
                    self.filter = lambda c: c is card
                    self.min = 0
            card = attacker.card
            attacker.bounce()
            attacker.player.mana_filters.append(Filter())


class Misdirection(SecretCard):
    def __init__(self):
        super().__init__("Misdirection", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

    def activate(self, player):
        player.hero.bind_once("attacked", self._reveal)

    def deactivate(self, player):
        player.hero.unbind("attacked", self._reveal)

    def _reveal(self, character):
        game = character.player.game
        if not character.removed:

            def choose_random(targets):
                possibilities = copy.copy(game.current_player.minions)
                possibilities.extend(game.other_player.minions)
                possibilities.append(game.current_player.hero)
                possibilities.append(game.other_player.hero)
                old_target = old_target_func(targets)
                possibilities.remove(old_target)
                game.current_player.agent.choose_target = old_target_func
                return possibilities[game.random(0, len(possibilities) - 1)]

            old_target_func = game.current_player.agent.choose_target
            game.current_player.agent.choose_target = choose_random
            super().reveal()
        else:
            self.activate(game.other_player)


class Snipe(SecretCard):
    def __init__(self):
        super().__init__("Snipe", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def activate(self, player):
        player.game.current_player.bind_once("minion_played", self._reveal)

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
        target = targets[player.game.random(0, len(targets) - 1)]
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
            target = targets.pop(game.random(0, len(targets) - 1))
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

        class Hound(MinionCard):
            def __init__(self):
                super().__init__("Hound", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                minion = Minion(1, 1, MINION_TYPE.BEAST)
                minion.charge = True
                return minion
        hound = Hound()
        for target in hearthbreaker.targeting.find_enemy_minion_battlecry_target(player.game, lambda x: True):
            hound.summon(player, game, len(player.minions))


class AnimalCompanion(Card):
    def __init__(self):
        super().__init__("Animal Companion", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        class Huffer(MinionCard):
            def __init__(self):
                super().__init__("Huffer", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                minion = Minion(4, 2, MINION_TYPE.BEAST)
                minion.charge = True
                return minion

        class Misha(MinionCard):
            def __init__(self):
                super().__init__("Misha", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                minion = Minion(4, 4, MINION_TYPE.BEAST)
                minion.taunt = True
                return minion

        class Leokk(MinionCard):
            def __init__(self):
                super().__init__("Leokk", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                def add_effect(m, index):
                    m.add_aura(1, 0, [player], lambda mini: mini is not minion)

                minion = Minion(2, 4, MINION_TYPE.BEAST)
                minion.bind("added_to_board", add_effect)
                return minion

        beast_list = [Huffer(), Misha(), Leokk()]
        card = beast_list[player.game.random(0, 2)]
        card.summon(player, player.game, len(player.minions))


class SnakeTrap(SecretCard):
    def __init__(self):
        super().__init__("Snake Trap", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.EPIC)

    def activate(self, player):
        player.game.current_player.bind_once("attack", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("attack", self._reveal)

    def _reveal(self, attacker, target):
        if isinstance(target, Minion):
            class Snake(MinionCard):
                def __init__(self):
                    super().__init__("Snake", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

                def create_minion(self, player):
                    return Minion(1, 1)
            snake = Snake()
            player = target.player.game.other_player
            for i in range(0, 3):
                snake.summon(player, player.game, len(player.minions))
            super().reveal()
        else:
            self.activate(target.player.game.current_player)
