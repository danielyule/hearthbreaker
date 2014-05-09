import hsgame.targetting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card

__author__ = 'Daniel'


class CircleOfHealing(Card):
    def __init__(self):
        super().__init__("Circle of Healing", 0, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)
        
        targets = game.other_player.minions.copy()
        targets.extend(player.minions)

        for minion in targets:
            minion.heal(4 + player.spell_power)

class DivineSpirit(Card):
    def __init__(self):
        super().__init__("Divine Spirit", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        # Increases by defense, not max_defense - source: http://www.hearthhead.com/card=1361/divine-spirit#comments:id=1908273
        self.target.increase_health(self.target.defense)
        
class HolyFire(Card):
    def __init__(self):
        super().__init__("Holy Fire", 6, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        self.target.spell_damage(5 + player.spell_power, self)
        player.heal(5) # The heal aspect of the card is not affected by +spell damage cards
        
class HolyNova(Card): # TODO: Can this card be cast if no minions is in play?
    def __init__(self):
        super().__init__("Holy Nova", 5, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)
        
        for minion in game.other_player.minions.copy():
            minion.spell_damage(2 + player.spell_power, self)  
        
        for minion in player.minions:
            minion.heal(2)

class HolySmite(Card):
    def __init__(self):
        super().__init__("Holy Smite", 1, CHARACTER_CLASS.PRIEST, CARD_RARITY.FREE, True, hsgame.targetting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        self.target.spell_damage(2 + player.spell_power, self)
        
class InnerFire(Card):
    def __init__(self):
        super().__init__("Inner Fire", 1, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        # This will increase/decrease a minions attack to its current health
        # It will set the attack to its current health, not max health (source: http://www.hearthhead.com/card=376/inner-fire#comments:id=1931155)
        self.target.increase_attack(self.target.defense - self.target.attack_power)
        
class MassDispel(Card): # TODO: Can this spell be cast if the enemy have no minions?
    def __init__(self):
        super().__init__("Mass Dispel", 4, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE, False)

    def use(self, player, game):
        super().use(player, game)
        
        for minion in game.other_player.minions.copy():
            minion.silence()
            
        player.draw()
        
class MindBlast(Card):
    def __init__(self):
        super().__init__("Mind Blast", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.FREE, False)

    def use(self, player, game):
        super().use(player, game)
        
        game.other_player.spell_damage(5 + player.spell_power, self)
        