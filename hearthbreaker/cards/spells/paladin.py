import copy
from hearthbreaker.effects import DrawOnAttack
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import Card, Minion, MinionCard, SecretCard


class AvengingWrath(Card):
    def __init__(self):
        super().__init__("Avenging Wrath", 6, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, player.effective_spell_damage(8)):
            targets = copy.copy(game.other_player.minions)
            targets.append(game.other_player.hero)
            target = targets[game.random(0, len(targets) - 1)]
            target.damage(1, self)


class BlessedChampion(Card):
    def __init__(self):
        super().__init__("Blessed Champion", 5, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.RARE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(self.target.calculate_attack())


class BlessingOfKings(Card):
    def __init__(self):
        super().__init__("Blessing of Kings", 4, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(4)
        self.target.increase_health(4)


class BlessingOfMight(Card):
    def __init__(self):
        super().__init__("Blessing of Might", 1, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(3)


class BlessingOfWisdom(Card):
    def __init__(self):
        super().__init__("Blessing of Wisdom", 1, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.add_effect(DrawOnAttack(amount=1, first_player=player is game.players[0]))


class Consecration(Card):
    def __init__(self):
        super().__init__("Consecration", 4, CHARACTER_CLASS.PALADIN, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(2), self)
        game.other_player.hero.damage(player.effective_spell_damage(2), self)


class DivineFavor(Card):
    def __init__(self):
        super().__init__("Divine Favor", 3, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        difference = len(game.other_player.hand) - len(player.hand)
        for i in range(0, difference):
            player.draw()


class Equality(Card):
    def __init__(self):
        super().__init__("Equality", 2, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)

        targets = copy.copy(game.other_player.minions)
        targets.extend(player.minions)

        for minion in targets:
            minion.decrease_health(minion.base_health - 1)

    def can_use(self, player, game):
        return super().can_use(player, game) and (len(player.minions) > 0 or len(game.other_player.minions) > 0)


class HammerOfWrath(Card):
    def __init__(self):
        super().__init__("Hammer of Wrath", 4, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(3), self)
        player.draw()


class HandOfProtection(Card):
    def __init__(self):
        super().__init__("Hand of Protection", 1, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.divine_shield = True


class HolyLight(Card):
    def __init__(self):
        super().__init__("Holy Light", 2, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.FREE, hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.heal(player.effective_heal_power(6), self)


class HolyWrath(Card):
    def __init__(self):
        super().__init__("Holy Wrath", 5, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.RARE, hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        player.draw()
        cost = player.hand[-1].mana
        self.target.damage(player.effective_spell_damage(cost), self)


class Humility(Card):
    def __init__(self):
        super().__init__("Humility", 1, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        # This will increase/decrease a minions attack to 1
        self.target.change_attack(1 - self.target.calculate_attack())


class LayOnHands(Card):
    def __init__(self):
        super().__init__("Lay on Hands", 8, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.EPIC,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.heal(player.effective_heal_power(8), self)
        player.draw()
        player.draw()
        player.draw()


class EyeForAnEye(SecretCard):
    def __init__(self):
        super().__init__("Eye for an Eye", 1, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.COMMON)

    def _reveal(self, amount, what):
        self.player.game.current_player.hero.damage(amount, self)
        super().reveal()

    def activate(self, player):
        player.hero.bind_once("hero_damaged", self._reveal)

    def deactivate(self, player):
        player.hero.unbind("hero_damaged", self._reveal)


class NobleSacrifice(SecretCard):
    def __init__(self):
        super().__init__("Noble Sacrifice", 1, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.COMMON)

    def _reveal(self, attacker):
        player = attacker.game.other_player
        if len(player.minions) < 7 and not attacker.removed:
            class DefenderMinion(MinionCard):
                def __init__(self):
                    super().__init__("Defender", 1, CHARACTER_CLASS.PALADIN,
                                     CARD_RARITY.SPECIAL)

                def create_minion(self, p):
                    return Minion(2, 1)

            def choose_defender(targets):
                defender = DefenderMinion()
                defender.summon(player, player.game, len(player.minions))
                old_target(targets)  # Called to allow the player to choose a target, although it will be ignored
                player.game.current_player.agent.choose_target = old_target
                return player.minions[-1]

            old_target = player.game.current_player.agent.choose_target
            player.game.current_player.agent.choose_target = choose_defender
            super().reveal()
        else:
            self.activate(player)

    def activate(self, player):
        player.game.current_player.bind_once("pre_attack", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("pre_attack", self._reveal)


class Redemption(SecretCard):
    def __init__(self):
        super().__init__("Redemption", 1, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.COMMON)

    def _reveal(self, minion, by):
        player = minion.player
        resurrection = minion.card.create_minion(player)
        resurrection.index = len(player.minions)
        resurrection.health = 1
        resurrection.player = player
        resurrection.game = player.game
        player.minions.append(resurrection)
        player.game.trigger("minion_added", resurrection)
        super().reveal()

    def activate(self, player):
        player.bind_once("minion_died", self._reveal)

    def deactivate(self, player):
        player.unbind("minion_died", self._reveal)


class Repentance(SecretCard):
    def __init__(self):
        super().__init__("Repentance", 1, CHARACTER_CLASS.PALADIN,
                         CARD_RARITY.COMMON)

    def _reveal(self, minion):

        minion.decrease_health(minion.calculate_max_health() - 1)
        super().reveal()

    def activate(self, player):
        player.game.current_player.bind_once("minion_played", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("minion_played", self._reveal)
