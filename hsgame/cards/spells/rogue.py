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

            for minion in game.other_player.minions.copy():
                minion.damage(attack_power, self)

            game.other_player.hero.damage(attack_power, self)


class ColdBlood(Card):
    def __init__(self):
        super().__init__("Cold Blood", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON,
                         hsgame.targeting.find_minion_spell_target)

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
        def remove_stealth():
            for minion in affected_minions:
                minion.stealth = False

        super().use(player, game)

        affected_minions = []

        for minion in player.minions:
            if not minion.stealth:
                minion.stealth = True
                affected_minions.append(minion)

        player.bind_once("turn_started", remove_stealth)


class DeadlyPoison(Card):
    def __init__(self):
        super().__init__("Deadly Poison", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)

        player.hero.weapon.base_attack += 2
        player.hero.change_temp_attack(2)

    def can_use(self, player, game):
        return super().can_use(player, game) and player.hero.weapon is not None
