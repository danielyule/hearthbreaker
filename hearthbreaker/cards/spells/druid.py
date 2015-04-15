import copy
from hearthbreaker.cards.base import ChoiceCard, SpellCard
from hearthbreaker.tags.action import Summon, GiveMana, Damage, Give, IncreaseArmor, Kill, Draw, Heal,\
    GiveDeathrattle, GiveManaCrystal
from hearthbreaker.tags.base import Deathrattle, ActionTag, BuffUntil, Buff, Choice
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import PlayerSelector, CharacterSelector, BothPlayer, UserPicker, HeroSelector, \
    MinionSelector, EnemyPlayer, Attribute, CurrentPlayer
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth, Taunt
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY


class Innervate(SpellCard):
    def __init__(self):
        super().__init__("Innervate", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.FREE,
                         action_tags=[ActionTag(GiveMana(2), PlayerSelector())])


class Moonfire(SpellCard):
    def __init__(self):
        super().__init__("Moonfire", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         action_tags=[ActionTag(Damage(1), CharacterSelector(None, BothPlayer(), UserPicker()))])


class Claw(SpellCard):
    def __init__(self):
        super().__init__("Claw", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.FREE,
                         action_tags=[ActionTag([Give(BuffUntil(ChangeAttack(2), TurnEnded())), IncreaseArmor(2)],
                                                HeroSelector())])


class Naturalize(SpellCard):
    def __init__(self):
        super().__init__("Naturalize", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         action_tags=[ActionTag(Kill(), MinionSelector(None, BothPlayer(), UserPicker())),
                                      ActionTag(Draw(2), PlayerSelector(EnemyPlayer()))])


class Savagery(SpellCard):
    def __init__(self):
        super().__init__("Savagery", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE,
                         action_tags=[ActionTag(Damage(Attribute('attack', HeroSelector())),
                                                MinionSelector(None, BothPlayer()))])


class MarkOfTheWild(SpellCard):
    def __init__(self):
        super().__init__("Mark of the Wild", 2, CHARACTER_CLASS.DRUID, CARD_RARITY.FREE,
                         action_tags=[ActionTag(Give([Buff(ChangeAttack(2)), Buff(ChangeHealth(2)), Buff(Taunt())]),
                                                MinionSelector(None, BothPlayer(), UserPicker()))])


class LeaderOfThePack(ChoiceCard):
    def __init__(self):
        super().__init__("Leader of the Pack", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class SummonPanther(ChoiceCard):
    def __init__(self):
        super().__init__("Summon a Panther", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


class PowerOfTheWild(SpellCard):
    def __init__(self):
        from hearthbreaker.cards.minions.druid import Panther
        super().__init__("Power of the Wild", 2, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         choices=[Choice(LeaderOfThePack(), [ActionTag(Give([Buff(ChangeAttack(1)),
                                                                            Buff(ChangeHealth(1))]),
                                         MinionSelector(None))]),
                                  Choice(SummonPanther(), [ActionTag(Summon(Panther()), PlayerSelector())])])


class WildGrowth(SpellCard):
    def __init__(self):
        super().__init__("Wild Growth", 2, CHARACTER_CLASS.DRUID, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        if player.max_mana < 10:
            player.max_mana += 1
        else:
            player.hand.append(ExcessMana())
            player.hand[-1].player = player


# Special card that only appears in tandem with Wild Growth
class ExcessMana(SpellCard):
    def __init__(self):
        super().__init__("Excess Mana", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)
        player.draw()


class WrathOne(ChoiceCard):
    def __init__(self):
        super().__init__("Wrath 1 Damage", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False)


class WrathThree(ChoiceCard):
    def __init__(self):
        super().__init__("Wrath 3 Damage", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False)


class Wrath(SpellCard):
    def __init__(self):
        super().__init__("Wrath", 2, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         choices=[Choice(WrathOne(), [ActionTag(Damage(1), MinionSelector(None, BothPlayer())),
                                                      ActionTag(Draw(1), PlayerSelector())]),
                                  Choice(WrathThree(), [ActionTag(Damage(3), MinionSelector(None, BothPlayer()))])])


class HealingTouch(SpellCard):
    def __init__(self):
        super().__init__("Healing Touch", 3, CHARACTER_CLASS.DRUID, CARD_RARITY.FREE,
                         action_tags=[ActionTag(Heal(8), CharacterSelector(None, BothPlayer()))])


class MarkOfNatureAttack(ChoiceCard):
    def __init__(self):
        super().__init__("Mark of Nature +4 Attack", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class MarkOfNatureHealth(ChoiceCard):
    def __init__(self):
        super().__init__("Mark of Nature +4 Health", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)


class MarkOfNature(SpellCard):
    def __init__(self):
        super().__init__("Mark of Nature", 3, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         choices=[Choice(MarkOfNatureAttack(), [ActionTag(Give(Buff(ChangeAttack(4))),
                                                                          MinionSelector(None, BothPlayer()))]),
                                  Choice(MarkOfNatureHealth(), [ActionTag(Give([Buff(ChangeHealth(4)), Buff(Taunt())]),
                                                                          MinionSelector(None, BothPlayer()))])])


class SavageRoar(SpellCard):
    def __init__(self):
        super().__init__("Savage Roar", 3, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         action_tags=[ActionTag(Give(BuffUntil(ChangeAttack(2), TurnEnded(player=CurrentPlayer()))),
                                                MinionSelector(None))])


class Bite(SpellCard):
    def __init__(self):
        super().__init__("Bite", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE,
                         action_tags=[ActionTag([Give(BuffUntil(ChangeAttack(4), TurnEnded())), IncreaseArmor(4)],
                                                HeroSelector())])


class SoulOfTheForest(SpellCard):
    def __init__(self):
        from hearthbreaker.cards.minions.druid import Treant
        super().__init__("Soul of the Forest", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         action_tags=[ActionTag(GiveDeathrattle(Deathrattle(Summon(Treant()), PlayerSelector())),
                                                MinionSelector(None))])


class Swipe(SpellCard):
    def __init__(self):
        super().__init__("Swipe", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_enemy_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(4, self)

        for minion in copy.copy(game.other_player.minions):
            if minion is not self.target:
                minion.damage(player.effective_spell_damage(1), self)

        if self.target is not game.other_player.hero:
            game.other_player.hero.damage(player.effective_spell_damage(1), self)


class Gain2(ChoiceCard):

    def __init__(self):
        super().__init__("Gain 2 mana crystals", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False)


class Draw3(ChoiceCard):

    def __init__(self):
        super().__init__("Draw three cards", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False)


class Nourish(SpellCard):
    def __init__(self):
        super().__init__("Nourish", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE,
                         choices=[Choice(Gain2(), [ActionTag(GiveManaCrystal(2), PlayerSelector())]),
                                  Choice(Draw3(), [ActionTag(Draw(3), PlayerSelector())])])


class DamageAll(ChoiceCard):
    def __init__(self):
        super().__init__("Do two damage to all enemy minions", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False)


class DamageOne(ChoiceCard):
            def __init__(self):
                super().__init__("Do five damage to an enemy minion", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                                 False)

            def can_use(self, player, game):
                return super().can_use(player, game) and len(hearthbreaker.targeting.find_minion_spell_target(
                    game, lambda t: t.spell_targetable())) > 0


class Starfall(SpellCard):
    def __init__(self):
        super().__init__("Starfall", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE,
                         choices=[Choice(DamageAll(), [ActionTag(Damage(2), MinionSelector(None, EnemyPlayer()))]),
                                  Choice(DamageOne(), [ActionTag(Damage(5), MinionSelector(None, EnemyPlayer(),
                                                                                           UserPicker()))])])

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) > 0


class ForceOfNature(SpellCard):
    def __init__(self):
        from hearthbreaker.cards.minions.druid import ChargeTreant
        super().__init__("Force of Nature", 6, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC,
                         action_tags=[ActionTag(Summon(ChargeTreant(), 3), PlayerSelector())])

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


class Starfire(SpellCard):
    def __init__(self):
        super().__init__("Starfire", 6, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON,
                         action_tags=[ActionTag(Damage(5), CharacterSelector(None, EnemyPlayer(), UserPicker())),
                                      ActionTag(Draw(), PlayerSelector())])


class PoisonSeeds(SpellCard):
    def __init__(self):
        super().__init__("Poison Seeds", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        from hearthbreaker.cards.minions.druid import PoisonSeedsTreant
        targets = hearthbreaker.targeting.find_minion_spell_target(game, lambda m: True)
        for target in targets:
            target.die(None)

        game.check_delayed()

        for target in targets:
            PoisonSeedsTreant().summon(target.player, target.game, len(target.player.minions))


class DarkWispers(SpellCard):
    def __init__(self):
        super().__init__("Dark Wispers", 6, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC)

    def can_use(self, player, game):
        return (super().can_use(player, game) and
                (len(player.minions) < 7 or
                 hearthbreaker.targeting.find_minion_spell_target(game, lambda t: t.spell_targetable()) is not None))

    def use(self, player, game):
        super().use(player, game)

        class Buff5(ChoiceCard):
            def __init__(self):
                super().__init__("Give a minion +5/+5 and Taunt", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False)

            def can_use(self, player, game):
                return hearthbreaker.targeting.find_minion_spell_target(game,
                                                                        lambda t: t.spell_targetable()) is not None

            def use(self, player, game):
                targets = hearthbreaker.targeting.find_minion_spell_target(game, lambda t: t.spell_targetable())
                target = player.agent.choose_target(targets)
                target.change_attack(5)
                target.increase_health(5)
                target.taunt = True

        class Wisps5(ChoiceCard):
            def __init__(self):
                super().__init__("Summon 5 Wisps", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON, False)

            def can_use(self, player, game):
                return len(player.minions) < 7

            def use(self, player, game):
                from hearthbreaker.cards.minions.neutral import Wisp
                for i in range(0, 5):
                    wisp = Wisp()
                    wisp.summon(player, game, len(player.minions))

        # In the official interface, both options are shown, but only one is highlighted.
        if len(hearthbreaker.targeting.find_minion_spell_target(game, lambda t: t.spell_targetable())) == 0:
            option = Wisps5()
        else:
            option = player.agent.choose_option([Wisps5(), Buff5()], player)
        option.use(player, game)


class Recycle(SpellCard):
    def __init__(self):
        super().__init__("Recycle", 6, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        player.opponent.deck.put_back(self.target)
        self.target.remove_from_board()


class TreeOfLife(SpellCard):
    def __init__(self):
        super().__init__("Tree of Life", 9, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)

        targets = copy.copy(game.other_player.minions)
        targets.extend(game.current_player.minions)
        targets.append(game.other_player.hero)
        targets.append(game.current_player.hero)
        for target in targets:
            target.heal(player.effective_heal_power(target.calculate_max_health()), self)
