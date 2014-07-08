import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card


class Assassinate(Card):
    def __init__(self):
        super().__init__("Assassinate", 5, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE,
                         hsgame.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)


class Backstab(Card):
    def __init__(self):
        super().__init__("Backstab", 0, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE,
                         hsgame.targeting.find_minion_spell_target,
                         lambda target: target.health == target.calculate_max_health())

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(2), self)


class Betrayal(Card):
    def __init__(self):
        super().__init__("Betrayal", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         hsgame.targeting.find_enemy_minion_spell_target)

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
