import copy
from hearthbreaker.cards.base import SpellCard
from hearthbreaker.tags.action import Damage, Draw, Discard
from hearthbreaker.tags.base import AuraUntil, Buff, Effect, CardQuery, CARD_SOURCE, ActionTag
from hearthbreaker.tags.condition import GreaterThan, IsDamaged
from hearthbreaker.tags.event import TurnEnded, Drawn
from hearthbreaker.tags.selector import MinionSelector, HeroSelector, PlayerSelector, Count
from hearthbreaker.tags.status import Charge as _Charge, MinimumHealth, ManaChange
import hearthbreaker.targeting
import hearthbreaker.tags.action
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY


class BattleRage(SpellCard):
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


class Brawl(SpellCard):
    def __init__(self):
        super().__init__("Brawl", 5, CHARACTER_CLASS.WARRIOR, CARD_RARITY.EPIC)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) + len(player.opponent.minions) >= 2

    def use(self, player, game):
        super().use(player, game)

        minions = copy.copy(player.minions)
        minions.extend(game.other_player.minions)

        if len(minions) > 1:
            survivor = game.random_choice(minions)
            for minion in minions:
                if minion is not survivor:
                    minion.die(self)


class Charge(SpellCard):
    def __init__(self):
        super().__init__("Charge", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.change_attack(2)
        self.target.add_buff(Buff(_Charge()))


class Cleave(SpellCard):
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


class CommandingShout(SpellCard):
    def __init__(self):
        super().__init__("Commanding Shout", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        player.add_aura(AuraUntil(MinimumHealth(1), MinionSelector(), TurnEnded()))

        player.draw()


class Execute(SpellCard):
    def __init__(self):
        super().__init__("Execute", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_enemy_minion_spell_target,
                         filter_func=lambda target: target.health != target.calculate_max_health() and
                         target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)


class HeroicStrike(SpellCard):
    def __init__(self):
        super().__init__("Heroic Strike", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        player.hero.change_temp_attack(4)


class InnerRage(SpellCard):
    def __init__(self):
        super().__init__("Inner Rage", 0, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(1, self)
        self.target.change_attack(2)


class MortalStrike(SpellCard):
    def __init__(self):
        super().__init__("Mortal Strike", 4, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if player.hero.health <= 12:
            self.target.damage(player.effective_spell_damage(6), self)
        else:
            self.target.damage(player.effective_spell_damage(4), self)


class Rampage(SpellCard):
    def __init__(self):
        super().__init__("Rampage", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target,
                         filter_func=lambda target: target.health != target.calculate_max_health() and
                         target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(3)
        self.target.increase_health(3)


class ShieldBlock(SpellCard):
    def __init__(self):
        super().__init__("Shield Block", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        player.hero.increase_armor(5)
        player.draw()


class ShieldSlam(SpellCard):
    def __init__(self):
        super().__init__("Shield Slam", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.EPIC,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(player.hero.armor), self)


class Slam(SpellCard):
    def __init__(self):
        super().__init__("Slam", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if self.target.health > player.effective_spell_damage(2) or self.target.divine_shield:
            self.target.damage(player.effective_spell_damage(2), self)
            player.draw()
        else:
            self.target.damage(player.effective_spell_damage(2), self)


class Upgrade(SpellCard):
    def __init__(self):
        super().__init__("Upgrade!", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        from hearthbreaker.cards.weapons.warrior import HeavyAxe
        if player.hero.weapon:
            player.hero.weapon.durability += 1
            player.hero.weapon.base_attack += 1
        else:
            heavy_axe = HeavyAxe().create_weapon(player)
            heavy_axe.equip(player)


class Whirlwind(SpellCard):
    def __init__(self):
        super().__init__("Whirlwind", 1, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        targets = copy.copy(game.other_player.minions)
        targets.extend(game.current_player.minions)
        for minion in targets:
            minion.damage(player.effective_spell_damage(1), self)


class BouncingBlade(SpellCard):
    def __init__(self):
        super().__init__("Bouncing Blade", 3, CHARACTER_CLASS.WARRIOR, CARD_RARITY.EPIC)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) + len(player.opponent.minions) >= 1

    def use(self, player, game):
        super().use(player, game)
        # According to https://www.youtube.com/watch?v=7ij_6_Dx47g, Bouncing Blade bounces at most 80 times

        # TODO Bouncing blade should only target those minions whose health is above minimum
        # See http://us.battle.net/hearthstone/en/forum/topic/15142084659
        targets = player.minions[:] + player.opponent.minions[:]
        if len(targets):
            for bounces in range(80):
                target = game.random_choice(targets)
                target.damage(player.effective_spell_damage(1), self)
                if target.dead:
                    break


class Crush(SpellCard):
    def __init__(self):
        super().__init__("Crush", 7, CHARACTER_CLASS.WARRIOR, CARD_RARITY.EPIC,
                         target_func=hearthbreaker.targeting.find_minion_spell_target,
                         buffs=[Buff(ManaChange(-4), GreaterThan(Count(MinionSelector(IsDamaged())), value=0))])

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)


class BurrowingMine(SpellCard):
    def __init__(self):
        super().__init__("Burrowing Mine", 0, CHARACTER_CLASS.WARRIOR, CARD_RARITY.COMMON, False,
                         effects=[Effect(Drawn(), ActionTag(Damage(10), HeroSelector())),
                                  Effect(Drawn(), ActionTag(Discard(query=CardQuery(source=CARD_SOURCE.LAST_DRAWN)),
                                         PlayerSelector())),
                                  Effect(Drawn(), ActionTag(Draw(), PlayerSelector()))])

    def use(self, player, game):
        super().use(player, game)


class Revenge(SpellCard):
    def __init__(self):
        super().__init__("Revenge", 2, CHARACTER_CLASS.WARRIOR, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        targets = copy.copy(game.other_player.minions)
        targets.extend(game.current_player.minions)
        if player.hero.health <= 12:
            for minion in targets:
                minion.damage(player.effective_spell_damage(3), self)
        else:
            for minion in targets:
                minion.damage(player.effective_spell_damage(1), self)
