import hsgame.targetting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card

__author__ = 'Daniel'


class AvengingWrath(Card):
    def __init__(self):
        super().__init__("Avenging Wrath", 6, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, 8 + player.spell_power):
            targets = game.other_player.minions.copy()
            targets.append(game.other_player)
            target = targets[game.random(0, len(targets) - 1)]
            target.spell_damage(1, self)

class BlessedChampion(Card):
    def __init__(self):
        super().__init__("Blessed Champion", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE, True, hsgame.targetting.find_minion_spell_target)
        
    def use(self, player, game):
        super().use(player, game)
        self.target.increase_attack(self.target.attack_power)
        
class BlessingOfKings(Card):
    def __init__(self):
        super().__init__("Blessing of Kings", 4, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.increase_attack(4)
        self.target.increase_health(4)

class BlessingOfMight(Card):
    def __init__(self):
        super().__init__("Blessing of Might", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.FREE, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.increase_attack(3)

class BlessingOfWisdom(Card):
    def __init__(self):
        super().__init__("Blessing of Wisdom", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):

        def draw(*args):
            player.draw()

        super().use(player, game)
        self.target.bind("attack_minion", draw, self.target)
        self.target.bind("attack_player", draw, self.target)
        self.target.bind_once("silenced", lambda minion: minion.unbind("attack_minion", draw), self.target)
        self.target.bind_once("silenced", lambda minion: minion.unbind("attack_player", draw), self.target)

class Consecration(Card):
    def __init__(self):
        super().__init__("Consecration", 4, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON, False)
        
    def use(self, player, game):
        super().use(player, game)
        for minion in game.other_player.minions.copy():
            minion.spell_damage(2 + player.spell_power, self)
        game.other_player.spell_damage(2 + player.spell_power, self)
