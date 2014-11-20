import copy
from hearthbreaker.tags.action import Summon, Kill
from hearthbreaker.tags.base import Effect, Deathrattle
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import SelfSelector, PlayerSelector
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Card, MinionCard, Minion


class Innervate(Card):
    def __init__(self):
        super().__init__("Innervate", 0, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        if player.mana < 8:
            player.mana += 2
        else:
            player.mana = 10


class Moonfire(Card):
    def __init__(self):
        super().__init__("Moonfire", 0, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(1), self)


class Claw(Card):
    def __init__(self):
        super().__init__("Claw", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        player.hero.change_temp_attack(2)
        player.hero.increase_armor(2)


class Naturalize(Card):
    def __init__(self):
        super().__init__("Naturalize", 1, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.die(self)
        game.other_player.draw()
        game.other_player.draw()


class Savagery(Card):
    def __init__(self):
        super().__init__("Savagery", 1, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.RARE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(player.hero.calculate_attack()), self)


class MarkOfTheWild(Card):
    def __init__(self):
        super().__init__("Mark of the Wild", 2, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_attack(2)
        self.target.increase_health(2)
        self.target.taunt = True


class PowerOfTheWild(Card):
    def __init__(self):
        super().__init__("Power of the Wild", 2, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        class LeaderOfThePack(Card):
            def __init__(self):
                super().__init__("Leader of the Pack", 0,
                                 CHARACTER_CLASS.DRUID,
                                 CARD_RARITY.COMMON)

            def use(self, player, game):
                for minion in player.minions:
                    minion.change_attack(1)
                    minion.increase_health(1)

        class SummonPanther(Card):
            def __init__(self):
                super().__init__("Summon a Panther", 0, CHARACTER_CLASS.DRUID,
                                 CARD_RARITY.SPECIAL)

            def use(self, player, game):
                class Panther(MinionCard):
                    def __init__(self):
                        super().__init__("Panther", 2, CHARACTER_CLASS.DRUID,
                                         CARD_RARITY.SPECIAL)

                    def create_minion(self, _):
                        return Minion(3, 2, MINION_TYPE.BEAST)

                panther = Panther()
                panther.summon(player, game, len(player.minions))

        option = player.agent.choose_option(LeaderOfThePack(), SummonPanther())
        option.use(player, game)


class WildGrowth(Card):
    def __init__(self):
        super().__init__("Wild Growth", 2, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        if player.max_mana < 10:
            player.max_mana += 1
        else:
            player.hand.append(ExcessMana())


# Special card that only appears in tandem with Wild Growth
class ExcessMana(Card):
    def __init__(self):
        super().__init__("Excess Mana", 0, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.SPECIAL)

    def use(self, player, game):
        super().use(player, game)
        player.draw()


class Wrath(Card):
    def __init__(self):
        super().__init__("Wrath", 2, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        class WrathOne(Card):
            def __init__(self):
                super().__init__("Wrath 1 Damage", 2, CHARACTER_CLASS.DRUID,
                                 CARD_RARITY.SPECIAL,
                                 hearthbreaker.targeting.find_minion_spell_target)

            def use(self, player, game):
                target.damage(player.effective_spell_damage(1), wrath)
                player.draw()

        class WrathThree(Card):
            def __init__(self):
                super().__init__("Wrath 3 Damage", 2, CHARACTER_CLASS.DRUID,
                                 CARD_RARITY.SPECIAL,
                                 hearthbreaker.targeting.find_minion_spell_target)

            def use(self, player, game):
                target.damage(player.effective_spell_damage(3), wrath)

        super().use(player, game)
        option = game.current_player.agent.choose_option(WrathOne(),
                                                         WrathThree())
        target = self.target
        wrath = self
        option.use(player, game)


class HealingTouch(Card):
    def __init__(self):
        super().__init__("Healing Touch", 3, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.heal(player.effective_heal_power(8), self)


class MarkOfNature(Card):
    def __init__(self):
        super().__init__("Mark of Nature", 3, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        class MarkOfNatureAttack(Card):
            def __init__(self):
                super().__init__("Mark of Nature +4 Attack", 0,
                                 CHARACTER_CLASS.DRUID,
                                 CARD_RARITY.SPECIAL,
                                 hearthbreaker.targeting.find_minion_spell_target)

            def use(self, player, game):
                target.change_attack(4)

        class MarkOfNatureHealth(Card):
            def __init__(self):
                super().__init__("Mark of Nature +4 Health", 0,
                                 CHARACTER_CLASS.DRUID,
                                 CARD_RARITY.SPECIAL,
                                 hearthbreaker.targeting.find_minion_spell_target)

            def use(self, player, game):
                target.increase_health(4)
                target.taunt = True

        super().use(player, game)
        target = self.target
        option = game.current_player.agent.choose_option(MarkOfNatureAttack(),
                                                         MarkOfNatureHealth())
        option.use(player, game)


class SavageRoar(Card):
    def __init__(self):
        super().__init__("Savage Roar", 3, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for minion in player.minions:
            minion.change_temp_attack(2)
        player.hero.change_temp_attack(2)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) > 0


class Bite(Card):
    def __init__(self):
        super().__init__("Bite", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        player.hero.change_temp_attack(4)
        player.hero.increase_armor(4)


class SoulOfTheForest(Card):
    def __init__(self):
        super().__init__("Soul of the Forest", 4, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        class Treant(MinionCard):
            def __init__(self):
                super().__init__("Treant", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)

            def create_minion(self, _):
                return Minion(2, 2)
        # Can stack as many deathrattles as we want, so no need to check if this has already been given
        # See http://hearthstone.gamepedia.com/Soul_of_the_Forest
        for minion in player.minions:
            minion.deathrattle.append(Deathrattle(Summon(Treant()), PlayerSelector()))


class Swipe(Card):
    def __init__(self):
        super().__init__("Swipe", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_enemy_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(4, self)

        for minion in copy.copy(game.other_player.minions):
            if minion is not self.target:
                minion.damage(player.effective_spell_damage(1), self)

        if self.target is not game.other_player.hero:
            game.other_player.hero.damage(player.effective_spell_damage(1),
                                          self)


class Nourish(Card):
    def __init__(self):
        super().__init__("Nourish", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)

        class Gain2(Card):

            def __init__(self):
                super().__init__("Gain 2 mana crystals", 0,
                                 CHARACTER_CLASS.DRUID,
                                 CARD_RARITY.SPECIAL)

            def use(self, player, game):
                if player.max_mana < 8:
                    player.max_mana += 2
                    player.mana += 2
                else:
                    player.max_mana = 10
                    player.mana += 2

        class Draw3(Card):

            def __init__(self):
                super().__init__("Draw three cards", 0, CHARACTER_CLASS.DRUID,
                                 CARD_RARITY.SPECIAL)

            def use(self, player, game):
                player.draw()
                player.draw()
                player.draw()

        option = player.agent.choose_option(Gain2(), Draw3())
        option.use(player, game)


class Starfall(Card):
    def __init__(self):
        super().__init__("Starfall", 5, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.RARE)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) > 0

    def use(self, player, game):
        super().use(player, game)

        class DamageAll(Card):
            def __init__(self):
                super().__init__("Do two damage to all enemy minions", 0,
                                 CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def use(self, player, game):
                for minion in copy.copy(game.other_player.minions):
                    minion.damage(player.effective_spell_damage(2), self)

        class DamageOne(Card):
            def __init__(self):
                super().__init__("Do five damage to an enemy minion", 0,
                                 CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def use(self, player, game):
                targets = hearthbreaker.targeting.find_minion_spell_target(game, lambda t: t.spell_targetable())
                target = player.agent.choose_target(targets)
                target.damage(player.effective_spell_damage(5), self)

        option = player.agent.choose_option(DamageAll(), DamageOne())
        option.use(player, game)


class ForceOfNature(Card):
    def __init__(self):
        super().__init__("Force of Nature", 6, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)

        class Treant(MinionCard):
            def __init__(self):
                super().__init__("Treant", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)

            def create_minion(self, player):
                return Minion(2, 2, charge=True, effects=[Effect(TurnEnded(), Kill(), SelfSelector())])

        for i in [0, 1, 2]:
            treant_card = Treant()
            treant_card.summon(player, game, len(player.minions))


class Starfire(Card):
    def __init__(self):
        super().__init__("Starfire", 6, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(5), self)
        player.draw()


class PoisionSeeds(Card):
    def __init__(self):
        super().__init__("Poison Seeds", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        class Treant(MinionCard):
            def __init__(self):
                super().__init__("Treant", 2, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def create_minion(self, player):
                return Minion(2, 2)

        targets = hearthbreaker.targeting.find_minion_spell_target(game, lambda m: True)
        for target in targets:
            target.die(None)

        game.check_delayed()

        for target in targets:
            Treant().summon(target.player, target.game, len(target.player.minions))
