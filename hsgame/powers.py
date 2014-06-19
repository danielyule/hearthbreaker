import hsgame.constants
import hsgame.game_objects

__author__ = 'Daniel'

def powers(character_class):
    if character_class == hsgame.constants.CHARACTER_CLASS.DRUID:
        return DruidPower
    elif character_class == hsgame.constants.CHARACTER_CLASS.HUNTER:
        return HunterPower
    elif character_class == hsgame.constants.CHARACTER_CLASS.MAGE:
        return MagePower
    elif character_class == hsgame.constants.CHARACTER_CLASS.PRIEST:
        return PriestPower
    elif character_class == hsgame.constants.CHARACTER_CLASS.PALADIN:
        return PaladinPower
    elif character_class == hsgame.constants.CHARACTER_CLASS.WARLOCK:
        return WarlockPower

class Power:

    def __init__(self, hero):
        self.hero = hero

    def can_use(self):
        return self.hero.player.mana >= 2

    def use(self):
        if self.can_use():
            self.hero.player.trigger("used_power")
            self.hero.player.mana -= 2


class DruidPower(Power):

    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        self.hero.increase_temp_attack(1)
        self.hero.increase_armour(1)


class HunterPower(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        self.hero.player.game.other_player.hero.damage(2, None)


class MagePower(Power):

    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        target = self.hero.find_power_target()
        target.damage(1, None)


class PriestPower(Power):

    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        target = self.hero.find_power_target()
        target.heal(2)
        
    def __str__(self):
        return "Lesser Heal"
        

# Special power the priest can obtain via the card Shadowform
class MindSpike(Power):
    
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        target = self.hero.find_power_target()
        target.damage(2, None)
        
    def __str__(self):
        return "Mind Spike"
        

# Special power the priest can obtain via the card Shadowform
class MindShatter(Power):
    
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        target = self.hero.find_power_target()
        target.damage(3, None)
        
    def __str__(self):
        return "Mind Shatter"


class PaladinPower(Power):
    
    def __init__(self, hero):
        super().__init__(hero)
        
    def use(self):
        class SilverHandRecruit(hsgame.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Silver Hand Recruit", 1, hsgame.constants.CHARACTER_CLASS.PALADIN, hsgame.constants.CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                return hsgame.game_objects.Minion(1, 1)

        super().use()

        recruit_card = SilverHandRecruit()
        recruit_card.create_minion(None).add_to_board(recruit_card, self.hero.player.game, self.hero.player, 0)


class WarlockPower(Power):
    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        self.hero.player.game.current_player.hero.damage(2, None)
        self.hero.player.game.current_player.draw()  #idk path for this


class JaraxxusPower(Power):
    
    def __init__(self, hero):
        super().__init__(hero)
        
    def use(self):
        class Infernal(hsgame.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Infernal", 6, hsgame.constants.CHARACTER_CLASS.WARLOCK, hsgame.constants.CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                return hsgame.game_objects.Minion(6, 6)

        super().use()

        infernal_card = Infernal()
        infernal_card.create_minion(None).add_to_board(infernal_card, self.hero.player.game, self.hero.player, 0)
