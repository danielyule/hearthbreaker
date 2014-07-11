import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import Card, SecretCard, Minion


class HuntersMark(Card):
    def __init__(self):
        super().__init__("Hunter's Mark", 0, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.COMMON,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.decrease_health(self.target.base_health - 1)


class ArcaneShot(Card):
    def __init__(self):
        super().__init__("Arcane Shot", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.FREE,
                         hsgame.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(2), self)


class BestialWrath(Card):
    def __init__(self):
        super().__init__("Bestial Wrath", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.EPIC,
                         hsgame.targeting.find_minion_spell_target,
                         lambda minion: minion.minion_type is MINION_TYPE.BEAST)

    def use(self, player, game):
        super().use(player, game)

        def remove_immunity():
            self.target.immune = False
            self.target.unbind("silenced", silenced)

        def silenced():
            player.unbind("turn_ended", remove_immunity)

        self.target.immune = True
        self.target.temp_attack += 2
        player.bind_once("turn_ended", remove_immunity)
        self.target.bind_once("silenced", silenced)


class Flare(Card):
    def __init__(self):
        super().__init__("Flare", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        for minion in hsgame.targeting.find_minion_spell_target(game,
                                                                lambda m: m.stealth):
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
        player.hero.bind("attacked", self._reveal)

    def deactivate(self, player):
        player.hero.unbind("attacked", self._reveal)

    def _reveal(self, minion):
        enemies = minion.game.current_player.minions.copy()
        enemies.append(minion.game.current_player.hero)
        for enemy in enemies:
            enemy.damage(2, None)
        for enemy in enemies:
            enemy.activate_delayed()
        super().reveal()


class FreezingTrap(SecretCard):
    def __init__(self):
        super().__init__("Freezing Trap", 2, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON)

    def activate(self, player):
        player.game.current_player.bind_once("attacking", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("attacking", self._reveal)

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
                possibilities = game.current_player.minions.copy()
                possibilities.extend(game.other_player.minions)
                possibilities.append(game.current_player.hero)
                possibilities.append(game.other_player.hero)
                old_target = old_target_func(targets)
                possibilities.remove(old_target)
                game.current_player.agent.choose_target = old_target_func
                return possibilities[game.random(0, len(possibilities))]

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
        minion.activate_delayed()