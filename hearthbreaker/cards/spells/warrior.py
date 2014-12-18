import copy
from hearthbreaker.tags.base import Aura, AuraUntil
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import SelfSelector, MinionSelector
from hearthbreaker.tags.status import Charge as _Charge, MinimumHealth
import hearthbreaker.targeting
import hearthbreaker.tags.action
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import Card, WeaponCard, Weapon


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

        if len(minions) > 1:
            survivor = game.random_choice(minions)
            for minion in minions:
                if minion is not survivor:
                    minion.die(self)


class Charge(Card):
    def __init__(self):
        super().__init__("Charge", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.change_attack(2)
        self.target.add_aura(Aura(_Charge(), SelfSelector()))


class Cleave(Card):
    def __init__(self):
        super().__init__("Cleave", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        minions = copy.copy(game.other_player.minions)

        for i in range(0, 2):
            minion = game.random_choice(minions)
            minions.remove(minion)
            minion.damage(player.effective_spell_damage(2), self)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 2


class CommandingShout(Card):
    def __init__(self):
        super().__init__("Commanding Shout", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        player.add_aura(AuraUntil(MinimumHealth(1), MinionSelector(), TurnEnded()))

        player.draw()


class Execute(Card):
    def __init__(self):
        super().__init__("Execute", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_enemy_minion_spell_target,
                         lambda target: target.health != target.calculate_max_health() and target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)


class HeroicStrike(Card):
    def __init__(self):
        super().__init__("Heroic Strike", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        player.hero.change_temp_attack(4)


class InnerRage(Card):
    def __init__(self):
        super().__init__("Inner Rage", 0, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(1, self)
        self.target.change_attack(2)


class MortalStrike(Card):
    def __init__(self):
        super().__init__("Mortal Strike", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if player.hero.health <= 12:
            self.target.damage(player.effective_spell_damage(6), self)
        else:
            self.target.damage(player.effective_spell_damage(4), self)


class Rampage(Card):
    def __init__(self):
        super().__init__("Rampage", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target,
                         lambda target: target.health != target.calculate_max_health() and target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(3)
        self.target.increase_health(3)


class ShieldBlock(Card):
    def __init__(self):
        super().__init__("Shield Block", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        player.hero.increase_armor(5)
        player.draw()


class ShieldSlam(Card):
    def __init__(self):
        super().__init__("Shield Slam", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.EPIC,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(player.hero.armor), self)


class Slam(Card):
    def __init__(self):
        super().__init__("Slam", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if self.target.health > player.effective_spell_damage(2) or self.target.divine_shield:
            self.target.damage(player.effective_spell_damage(2), self)
            player.draw()
        else:
            self.target.damage(player.effective_spell_damage(2), self)


class Upgrade(Card):
    def __init__(self):
        super().__init__("Upgrade!", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        if player.hero.weapon:
            player.hero.weapon.durability += 1
            player.hero.weapon.base_attack += 1
        else:
            class HeavyAxe(WeaponCard):
                def __init__(self):
                    super().__init__("Heavy Axe", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.SPECIAL)

                def create_weapon(self, player):
                    return Weapon(1, 3)
            heavy_axe = HeavyAxe().create_weapon(player)
            heavy_axe.equip(player)


class Whirlwind(Card):
    def __init__(self):
        super().__init__("Whirlwind", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        targets = copy.copy(game.other_player.minions)
        targets.extend(game.current_player.minions)
        for minion in targets:
            minion.damage(player.effective_spell_damage(1), self)
