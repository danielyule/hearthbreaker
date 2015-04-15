import copy
from hearthbreaker.cards.base import SecretCard, SpellCard
from hearthbreaker.game_objects import Minion, Hero
from hearthbreaker.tags.base import BuffUntil, Buff
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import CurrentPlayer
from hearthbreaker.tags.status import Immune, ManaChange
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE


class HuntersMark(SpellCard):
    def __init__(self):
        super().__init__("Hunter's Mark", 0, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.set_health_to(1)


class ArcaneShot(SpellCard):
    def __init__(self):
        super().__init__("Arcane Shot", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(2), self)


class BestialWrath(SpellCard):
    def __init__(self):
        super().__init__("Bestial Wrath", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.EPIC,
                         target_func=hearthbreaker.targeting.find_friendly_minion_spell_target,
                         filter_func=lambda minion: minion.card.minion_type is MINION_TYPE.BEAST and
                         minion.spell_targetable())

    def use(self, player, game):
        super().use(player, game)
        self.target.add_buff(BuffUntil(Immune(), TurnEnded(player=CurrentPlayer())))
        self.target.change_temp_attack(2)


class Flare(SpellCard):
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


class Tracking(SpellCard):
    def __init__(self):
        super().__init__("Tracking", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        cards = []
        for card_index in range(0, 3):
            if player.can_draw():
                cards.append(player.deck.draw(game))
        if len(cards) > 0:
            chosen_card = player.agent.choose_option(cards, player)
            player.hand.append(chosen_card)
            player.hand[-1].player = player
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
            attacker.card.add_buff(Buff(ManaChange(2)))
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
            possibilities = copy.copy(game.current_player.minions)
            possibilities.extend(game.other_player.minions)
            possibilities.append(game.current_player.hero)
            possibilities.append(game.other_player.hero)
            possibilities.remove(character.current_target)
            character.current_target = game.random_choice(possibilities)

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


class DeadlyShot(SpellCard):
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


class MultiShot(SpellCard):
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


class ExplosiveShot(SpellCard):
    def __init__(self):
        super().__init__("Explosive Shot", 5, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

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


class KillCommand(SpellCard):
    def __init__(self):
        super().__init__("Kill Command", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        beasts = hearthbreaker.targeting.find_friendly_minion_battlecry_target(
            player.game, lambda x: x.card.minion_type is MINION_TYPE.BEAST)
        if beasts is None:
            self.target.damage(player.effective_spell_damage(3), self)
        else:
            self.target.damage(player.effective_spell_damage(5), self)


class UnleashTheHounds(SpellCard):
    def __init__(self):
        super().__init__("Unleash the Hounds", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for target in hearthbreaker.targeting.find_enemy_minion_spell_target(player.game, lambda x: True):
            hound = hearthbreaker.cards.minions.hunter.Hound()
            hound.summon(player, game, len(player.minions))

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 1 and len(player.minions) < 7


class AnimalCompanion(SpellCard):
    def __init__(self):
        super().__init__("Animal Companion", 3, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        beast_list = [hearthbreaker.cards.minions.hunter.Huffer(), hearthbreaker.cards.minions.hunter.Misha(),
                      hearthbreaker.cards.minions.hunter.Leokk()]
        card = game.random_choice(beast_list)
        card.summon(player, player.game, len(player.minions))

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


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


class CallPet(SpellCard):
    def __init__(self):
        super().__init__("Call Pet", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

    def use(self, player, game):
        def reduce_cost(card):
            if card.is_minion() and card.minion_type == MINION_TYPE.BEAST:
                card.add_buff(Buff(ManaChange(-4)))

        super().use(player, game)
        player.bind_once("card_drawn", reduce_cost)
        player.draw()


class CobraShot(SpellCard):
    def __init__(self):
        super().__init__("Cobra Shot", 5, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(3), self)
        game.other_player.hero.damage(player.effective_spell_damage(3), self)


class FeignDeath(SpellCard):
    def __init__(self):
        super().__init__("Feign Death", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)

        # Feign death operates in the same order as standard deathrattles
        # See http://www.hearthhead.com/card=1991/feign-death#comments:id=2057895
        for minion in sorted(player.minions, key=lambda m: m.born):
            for deathrattle in minion.deathrattle:
                deathrattle.do(minion)
            if player.double_deathrattle:
                for deathrattle in minion.deathrattle:
                    deathrattle.do(minion)


class QuickShot(SpellCard):
    def __init__(self):
        super().__init__("Quick Shot", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(3, self)
        if len(player.hand) == 0:
            player.draw()
