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
    elif character_class == hsgame.constants.CHARACTER_CLASS.SHAMAN:
        return ShamanPower
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
        target.damage(1 * self.hero.player.spell_multiplier, None)


class PriestPower(Power):

    def __init__(self, hero):
        super().__init__(hero)

    def use(self):
        super().use()
        target = self.hero.find_power_target()
        if self.hero.player.heal_does_damage:
            target.damage(2 * self.hero.player.spell_multiplier, None)
        else:
            target.heal(2 * self.hero.player.heal_multiplier, None)
        
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
        recruit_card.create_minion(self.hero.player).add_to_board(recruit_card, self.hero.player.game, self.hero.player, 0)


class ShamanPower(Power):
    
    def __init__(self, hero):
        self.healing_totem = False
        self.searing_totem = False
        self.stoneclaw_totem = False
        self.wrath_of_air_totem = False
        
        super().__init__(hero)
    
    def can_use(self):
        self.healing_totem = False
        self.searing_totem = False
        self.stoneclaw_totem = False
        self.wrath_of_air_totem = False
        
        for minion in self.hero.player.minions:
            if minion.card.name == "Healing Totem":
                self.healing_totem = True
            elif minion.card.name == "Searing Totem":
                self.searing_totem = True
            elif minion.card.name == "Stoneclaw Totem":
                self.stoneclaw_totem = True
            elif minion.card.name == "Wrath of Air Totem":
                self.wrath_of_air_totem = True
        
        if self.healing_totem and self.searing_totem and self.stoneclaw_totem and self.wrath_of_air_totem:
            return False
        
        return super().can_use()
    
    def use(self):
        class HealingTotem(hsgame.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Healing Totem", 1, hsgame.constants.CHARACTER_CLASS.SHAMAN, hsgame.constants.CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                def heal_friendly_minions():
                    for m in player.minions:
                        m.heal(1, self)
        
                def silence():
                    player.unbind("turn_ended", heal_friendly_minions)
                
                minion = hsgame.game_objects.Minion(0, 2)
                player.bind("turn_ended", heal_friendly_minions)
                minion.bind_once("silenced", silence)
                return minion
                        
        class SearingTotem(hsgame.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Searing Totem", 1, hsgame.constants.CHARACTER_CLASS.SHAMAN, hsgame.constants.CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                return hsgame.game_objects.Minion(1, 1)
            
        class StoneclawTotem(hsgame.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Stoneclaw Totem", 1, hsgame.constants.CHARACTER_CLASS.SHAMAN, hsgame.constants.CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                minion = hsgame.game_objects.Minion(0, 2)
                minion.taunt = True
                return minion

        class WrathOfAirTotem(hsgame.game_objects.MinionCard):
            def __init__(self):
                super().__init__("Wrath of Air Totem", 1, hsgame.constants.CHARACTER_CLASS.SHAMAN, hsgame.constants.CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                minion = hsgame.game_objects.Minion(0, 2)
                minion.spell_power = 1
                return minion

        super().use()

        totems = []
        if not self.healing_totem:
            totems.append(HealingTotem())
        if not self.searing_totem:
            totems.append(SearingTotem())
        if not self.stoneclaw_totem:
            totems.append(StoneclawTotem())
        if not self.wrath_of_air_totem:
            totems.append(WrathOfAirTotem())

        random_totem = totems[self.hero.player.game.random(0, len(totems) - 1)]
        random_totem.create_minion(self.hero.player).add_to_board(random_totem, self.hero.player.game, self.hero.player, 0)

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

