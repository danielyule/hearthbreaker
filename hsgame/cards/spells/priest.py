import copy
import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card, Minion, MinionCard

__author__ = 'Daniel'


class CircleOfHealing(Card):
    def __init__(self):
        super().__init__("Circle of Healing", 0, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        
        targets = game.other_player.minions.copy()
        targets.extend(player.minions)

        for minion in targets:
            minion.heal(player.effective_heal_power(4), self)

class DivineSpirit(Card):
    def __init__(self):
        super().__init__("Divine Spirit", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        # Increases by health, not max_health - source: http://www.hearthhead.com/card=1361/divine-spirit#comments:id=1908273
        self.target.increase_health(self.target.health)
        
class HolyFire(Card):
    def __init__(self):
        super().__init__("Holy Fire", 6, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE, hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        self.target.damage(player.effective_spell_damage(5), self)
        player.hero.heal(player.effective_heal_power(5), self)
        
class HolyNova(Card): # TODO: Can this card be cast if no minions is in play?
    def __init__(self):
        super().__init__("Holy Nova", 5, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        
        for minion in game.other_player.minions.copy():
            minion.damage(player.effective_spell_damage(2), self)
        
        for minion in player.minions:
            minion.heal(player.effective_heal_power(2), self)

class HolySmite(Card):
    def __init__(self):
        super().__init__("Holy Smite", 1, CHARACTER_CLASS.PRIEST, CARD_RARITY.FREE, hsgame.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        self.target.damage(player.effective_spell_damage(2), self)
        
class InnerFire(Card):
    def __init__(self):
        super().__init__("Inner Fire", 1, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        # This will increase/decrease a minions attack to its current health
        # It will set the attack to its current health, not max health (source: http://www.hearthhead.com/card=376/inner-fire#comments:id=1931155)
        self.target.change_attack(self.target.health - self.target.attack_power)
        
class MassDispel(Card): # TODO: Can this spell be cast if the enemy have no minions?
    def __init__(self):
        super().__init__("Mass Dispel", 4, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        
        for minion in game.other_player.minions.copy():
            minion.silence()
            
        player.draw()
        
class MindBlast(Card):
    def __init__(self):
        super().__init__("Mind Blast", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        
        game.other_player.hero.damage(player.effective_spell_damage(5), self)
        
class MindControl(Card):
    def __init__(self):
        super().__init__("Mind Control", 10, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, hsgame.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        self.target.remove_from_board()
        self.target.add_to_board(self.target.card, self.target.game, player, 0)
        
class MindVision(Card): # TODO: Can this card be played if opponent has no cards in hand?
    def __init__(self):
        super().__init__("Mind Vision", 1, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        
        card = copy.deepcopy(game.other_player.hand[game.random(0, len(game.other_player.hand) - 1)])
        player.hand.append(card)
        
class Mindgames(Card):
    def __init__(self):
        super().__init__("Mindgames", 4, CHARACTER_CLASS.PRIEST, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)
        
        class ShadowOfNothing(MinionCard):
            def __init__(self):
                super().__init__("Shadow of Nothing", 0, CHARACTER_CLASS.PRIEST, CARD_RARITY.SPECIAL)

            def create_minion(self, p):
                minion = Minion(0, 1)
                return minion
        
        minions = []
        
        for index in range(0, 30):
            if not game.other_player.deck.used[index] and not game.other_player.deck.cards[index].is_spell():
                minions.append(game.other_player.deck.cards[index])
                
        if len(minions) == 0:
            minions.append(ShadowOfNothing())

        minion = copy.copy(minions[game.random(0, len(minions) - 1)])
        minion.create_minion(player).add_to_board(minion, game, player, 0)

class PowerWordShield(Card):
    def __init__(self):
        super().__init__("Power Word: Shield", 1, CHARACTER_CLASS.PRIEST, CARD_RARITY.FREE, hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        self.target.increase_health(2)
        player.draw()


class ShadowMadness(Card):
    def __init__(self):
        super().__init__("Shadow Madness", 4, CHARACTER_CLASS.PRIEST, CARD_RARITY.RARE, hsgame.targeting.find_enemy_minion_spell_target, lambda target: target.attack_power <= 3 and target.spell_targetable())

    def use(self, player, game):
        
        def unbind_turn_ended():
            player.unbind("turn_ended", switch_side)
        
        def switch_side(*args):
            minion.unbind("silenced", unbind_turn_ended)
            m = copy.deepcopy(minion)
            
            minion.remove_from_board()
            m.add_to_board(self.target.card, self.target.game, self.target.player, 0)
        
        super().use(player, game)
        
        minion = copy.deepcopy(self.target)
        minion.charge = True
        minion.bind_once("silenced", unbind_turn_ended)
        
        self.target.remove_from_board()
        minion.add_to_board(minion.card, game, player, 0)
        
        player.bind_once("turn_ended", switch_side)
        
        
class ShadowWordDeath(Card):
    def __init__(self):
        super().__init__("Shadow Word: Death", 3, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, hsgame.targeting.find_minion_spell_target, lambda target: target.attack_power >= 5 and target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)
        
class ShadowWordPain(Card):
    def __init__(self):
        super().__init__("Shadow Word: Pain", 2, CHARACTER_CLASS.PRIEST, CARD_RARITY.FREE, hsgame.targeting.find_minion_spell_target, lambda target: target.attack_power <= 3 and target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)
        
class Shadowform(Card):
    def __init__(self):
        super().__init__("Shadowform", 3, CHARACTER_CLASS.PRIEST, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)

        if type(player.hero.power) is not hsgame.powers.MindShatter and type(player.hero.power) is not hsgame.powers.MindSpike:
            player.hero.power = hsgame.powers.MindSpike(player.hero)
        elif type(player.hero.power) is hsgame.powers.MindSpike:
            player.hero.power = hsgame.powers.MindShatter(player.hero)
        
        
class Silence(Card):
    def __init__(self):
        super().__init__("Silence", 0, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON, hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        
        self.target.silence()
        
class Thoughtsteal(Card):
    def __init__(self):
        super().__init__("Thoughtsteal", 3, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
                
        cards = []
        
        for index in range(0, 30):
            if not game.other_player.deck.used[index]:
                cards.append(game.other_player.deck.cards[index])
        
        for i in range(0, 2):
            if not len(cards) == 0 and not len(player.hand) == 10: # TODO: We are assuming nothing will happen if you have 10 cards in hand. Will you even see the card go up in flames?
                rand = game.random(0, len(cards) - 1)
                card = copy.copy(cards.pop(rand)) # TODO: We are assuming you can't copy the same card twice
                player.hand.append(card)
        