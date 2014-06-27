import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import Card

__author__ = 'Daniel'


class HuntersMark(Card):
    def __init__(self):
        super().__init__("Hunter's Mark", 0, CHARACTER_CLASS.HUNTER, CARD_RARITY.COMMON,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.decrease_health(self.target.max_health - 1)


class ArcaneShot(Card):
    def __init__(self):
        super().__init__("Arcane Shot", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.FREE,
                         hsgame.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(2), self)


class BestialWrath(Card):
    def __init__(self):
        super().__init__("Bestial Wrath", 1, CHARACTER_CLASS.HUNTER, CARD_RARITY.EPIC,
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
        for minion in hsgame.targeting.find_minion_spell_target(game, lambda m: m.stealth):
            minion.stealth = False

        for secret in game.other_player.secrets:
            secret.deactivate(game.other_player)

        game.other_player.secrets = []
        player.draw()

