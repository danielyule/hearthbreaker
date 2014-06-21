import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion, Card, 
from hsgame.cards.battlecries import deal_three_damage, deal_five_damage, deal_one_damage_all_characters, destroy_own_crystal, discard_one, discard_two

__author__ = 'randomflyingtaco'
#let the train wreck begin

class FlameImp(MinionCard):
    def __init__(self):
        super().__init__("Flame Imp", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON)

    def create_minion(self, player):
        player.hero.damage(3, None)
        return Minion(3, 2, MINION_TYPE.DEMON)

class PitLord(MinionCard):
    def __init__(self):
        super().__init__("Pit Lord", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.EPIC)

    def create_minion(self, player):
        player.hero.damage(5, None)
        return Minion(5, 6, MINION_TYPE.DEMON)

class VoidWalker(MinionCard):
    def __init__(self):
        super().__init__("Void Walker", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(1, 3, MINION_TYPE.DEMON)
        minion.taunt = True
        return minion
        
class DreadInfernal(MinionCard):
    def __init__(self):
        super().__init__("Dread Infernal", 6, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE)

    def create_minion(self, player):
        targets = game.other_player.minions.copy()
        targets.extend(game.current_player.minions)
        targets.append(game.other_player.hero)
        targets.append(game.current_player.hero)
        for minion in targets:
            minion.damage(1, None)
        return Minion(6, 6, MINION_TYPE.DEMON)

class Felguard(MinionCard):
    def __init__(self):
        super().__init__("Felguard", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE)

    def create_minion(self, player):
        player.max_mana -= 1
        minion = Minion(3, 5, MINION_TYPE.DEMON)
        minion.taunt = True
        return minion

class Doomguard(MinionCard):
    def __init__(self):
        super().__init__("Doomguard", 5, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE)

    def create_minion(self, player):
        player.discard()
        player.discard()
        minion = Minion(5, 7, MINION_TYPE.DEMON)
        minion.charge = True
        return minion
        
class Succubus(MinionCard):
    def __init__(self):
        super().__init__("Succubus", 2, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE)

    def create_minion(self, player):
        player.discard()
        minion = Minion(4, 3, MINION_TYPE.DEMON)
        return minion

class SummoningPortal(MinionCard):
    def __init__(self):
        super().__init__("Summoning Portal", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        class Filter:
            def __init__(self):
                self.amount = 2
                self.filter = lambda c: not c.is_spell()
                self.min = 1

        filter = Filter()
        minion = Minion(0, 4)
        minion.bind_once("silenced", lambda: player.mana_filters.remove(filter))
        player.mana_filters.append(filter)
        return minion
