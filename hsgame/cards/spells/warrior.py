import copy
import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card


class BattleRage(Card):
    def __init__(self):
        super().__init__("Battle Rage", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def use(self, player, game):
        def damaged_character(character):
            return character.health < character.calculate_max_health()

        super().use(player, game)

        characters = copy.copy(player.minions)
        characters.append(player.hero)

        characters = [character for character in characters if damaged_character(character)]

        for i in range(0, len(characters)):
            player.draw()


class Brawl(Card):
    def __init__(self):
        super().__init__("Brawl", 5, CHARACTER_CLASS.WARRIOR, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)

        minions = copy.copy(player.minions)
        minions.extend(game.other_player.minions)

        while len(minions) != 1:
            minion = minions.pop(game.random(0, len(minions) - 1))
            minion.die(self)


class Charge(Card):
    def __init__(self):
        super().__init__("Charge", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE,
                         hsgame.targeting.find_friendly_minion_battlecry_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.change_attack(2)
        self.target.charge = True
        self.target.exhausted = False


class Cleave(Card):
    def __init__(self):
        super().__init__("Cleave", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        minions = copy.copy(game.other_player.minions)

        for i in range(0, 2):
            minion = minions.pop(game.random(0, len(minions) - 1))
            minion.damage(player.effective_spell_damage(2), self)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 2
