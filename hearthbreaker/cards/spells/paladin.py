import copy
from hearthbreaker.cards.base import SpellCard, SecretCard
from hearthbreaker.tags.action import Draw
from hearthbreaker.tags.base import Effect, Buff, ActionTag
from hearthbreaker.tags.event import Attack
from hearthbreaker.tags.selector import PlayerSelector, PlayerOne, PlayerTwo, BothPlayer, Count, DeadMinionSelector
from hearthbreaker.tags.status import DoubleAttack, ManaChange
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.cards.minions.paladin import SilverHandRecruit
from hearthbreaker.cards.weapons.paladin import LightsJustice


class AvengingWrath(SpellCard):
    def __init__(self):
        super().__init__("Avenging Wrath", 6, CHARACTER_CLASS.PALADIN, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, player.effective_spell_damage(8)):
            targets = copy.copy(game.other_player.minions)
            targets.append(game.other_player.hero)
            target = game.random_choice(targets)
            target.damage(1, self)


class BlessedChampion(SpellCard):
    def __init__(self):
        super().__init__("Blessed Champion", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.add_buff(Buff(DoubleAttack()))


class BlessingOfKings(SpellCard):
    def __init__(self):
        super().__init__("Blessing of Kings", 4, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(4)
        self.target.increase_health(4)


class BlessingOfMight(SpellCard):
    def __init__(self):
        super().__init__("Blessing of Might", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(3)


class BlessingOfWisdom(SpellCard):
    def __init__(self):
        super().__init__("Blessing of Wisdom", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if player is game.players[0]:
            draw_player = PlayerOne()
        else:
            draw_player = PlayerTwo()
        self.target.add_effect(Effect(Attack(), ActionTag(Draw(), PlayerSelector(draw_player))))


class Consecration(SpellCard):
    def __init__(self):
        super().__init__("Consecration", 4, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(2), self)
        game.other_player.hero.damage(player.effective_spell_damage(2), self)


class DivineFavor(SpellCard):
    def __init__(self):
        super().__init__("Divine Favor", 3, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        difference = len(game.other_player.hand) - len(player.hand)
        for i in range(0, difference):
            player.draw()


class Equality(SpellCard):
    def __init__(self):
        super().__init__("Equality", 2, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)

        targets = copy.copy(game.other_player.minions)
        targets.extend(player.minions)

        for minion in targets:
            minion.set_health_to(1)

    def can_use(self, player, game):
        return super().can_use(player, game) and (len(player.minions) > 0 or len(game.other_player.minions) > 0)


class HammerOfWrath(SpellCard):
    def __init__(self):
        super().__init__("Hammer of Wrath", 4, CHARACTER_CLASS.PALADIN, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(3), self)
        player.draw()


class HandOfProtection(SpellCard):
    def __init__(self):
        super().__init__("Hand of Protection", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.divine_shield = True


class HolyLight(SpellCard):
    def __init__(self):
        super().__init__("Holy Light", 2, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.FREE, target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.heal(player.effective_heal_power(6), self)


class HolyWrath(SpellCard):
    def __init__(self):
        super().__init__("Holy Wrath", 5, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.RARE, target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        fatigue = False
        if player.deck.left == 0:
            fatigue = True

        player.draw()
        if not fatigue:
            cost = player.hand[-1].mana
            self.target.damage(player.effective_spell_damage(cost), self)


class Humility(SpellCard):
    def __init__(self):
        super().__init__("Humility", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        # This will increase/decrease a minions attack to 1
        self.target.change_attack(1 - self.target.calculate_attack())


class LayOnHands(SpellCard):
    def __init__(self):
        super().__init__("Lay on Hands", 8, CHARACTER_CLASS.PALADIN, CARD_RARITY.EPIC,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.heal(player.effective_heal_power(8), self)
        player.draw()
        player.draw()
        player.draw()


class Avenge(SecretCard):
    def __init__(self):
        super().__init__("Avenge", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def _reveal(self, dead_minion, attacker):
        if len([minion for minion in self.player.minions if not minion.dead]) > 0:
            target = self.player.game.random_choice(self.player.minions)
            target.change_attack(3)
            target.increase_health(2)
            super().reveal()

    def activate(self, player):
        player.bind("minion_died", self._reveal)

    def deactivate(self, player):
        player.unbind("minion_died", self._reveal)


class EyeForAnEye(SecretCard):
    def __init__(self):
        super().__init__("Eye for an Eye", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def _reveal(self, character, attacker, amount):
        if character.is_hero():
            character.player.opponent.hero.damage(amount, self)
        super().reveal()

    def activate(self, player):
        player.bind("character_damaged", self._reveal)

    def deactivate(self, player):
        player.unbind("character_damaged", self._reveal)


class NobleSacrifice(SecretCard):
    def __init__(self):
        super().__init__("Noble Sacrifice", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def _reveal(self, attacker, target):
        player = attacker.player.game.other_player
        if len(player.minions) < 7 and not attacker.removed:
            from hearthbreaker.cards.minions.paladin import DefenderMinion
            defender = DefenderMinion()
            defender.summon(player, player.game, len(player.minions))
            attacker.current_target = player.minions[-1]
            super().reveal()

    def activate(self, player):
        player.opponent.bind("character_attack", self._reveal)

    def deactivate(self, player):
        player.opponent.unbind("character_attack", self._reveal)


class Redemption(SecretCard):
    def __init__(self):
        super().__init__("Redemption", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def _reveal(self, minion, by):
        resurrection = minion.card.summon(minion.player, minion.game, min(minion.index, len(minion.player.minions)))
        if resurrection:
            resurrection.health = 1
            super().reveal()

    def activate(self, player):
        player.bind("minion_died", self._reveal)

    def deactivate(self, player):
        player.unbind("minion_died", self._reveal)


class Repentance(SecretCard):
    def __init__(self):
        super().__init__("Repentance", 1, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def _reveal(self, minion):

        minion.set_health_to(1)
        super().reveal()

    def activate(self, player):
        player.game.current_player.bind("minion_played", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("minion_played", self._reveal)


class SealOfLight(SpellCard):
    def __init__(self):
        super().__init__("Seal of Light", 2, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        player.hero.heal(player.effective_heal_power(4), self)
        player.hero.change_temp_attack(2)


class MusterForBattle(SpellCard):
    def __init__(self):
        super().__init__("Muster for Battle", 3, CHARACTER_CLASS.PALADIN, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)

        for i in range(0, 3):
            dude = SilverHandRecruit()
            dude.summon(player, player.game, len(player.minions))
        justice = LightsJustice()
        hammer = justice.create_weapon(player)
        hammer.card = justice
        hammer.equip(player)


class SolemnVigil(SpellCard):
    def __init__(self):
        super().__init__("Solemn Vigil", 5, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON,
                         buffs=[Buff(ManaChange(Count(DeadMinionSelector(players=BothPlayer())), -1))])

    def use(self, player, game):
        super().use(player, game)
        for n in range(0, 2):
            player.draw()
