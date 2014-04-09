import hsgame.targetting
from hsgame.constants import CHARACTER_CLASS, CARD_STATUS, MINION_TYPES

__author__ = 'Daniel'
from hsgame.game_objects import Card, MinionCard, Minion


#Druid Spells
class Innervate(Card):
    def __init__(self):
        super().__init__("Innervate", 0, CHARACTER_CLASS.DRUID, CARD_STATUS.BASIC, False)

    def use(self, player, game):
        super().use(player, game)
        player.mana += 2


class Moonfire(Card):
    def __init__(self):
        super().__init__("Moonfire", 0, CHARACTER_CLASS.DRUID, CARD_STATUS.BASIC, True, hsgame.targetting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.spell_damage(1, self)


class Claw(Card):
    def __init__(self):
        super().__init__("Claw", 1, CHARACTER_CLASS.DRUID, CARD_STATUS.BASIC, False)

    def use(self, player, game):
        super().use(player, game)
        player.increase_attack(2)
        player.increase_armour(2)


class Naturalize(Card):
    def __init__(self):
        super().__init__("Naturalize", 1, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.die(self)
        game.other_player.draw()
        game.other_player.draw()


class Savagery(Card):
    def __init__(self):
        super().__init__("Savagery", 1, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.spell_damage(player.attack_power, self)


class MarkOfTheWild(Card):
    def __init__(self):
        super().__init__("Mark of the Wild", 2, CHARACTER_CLASS.DRUID, CARD_STATUS.BASIC, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.increase_attack(2)
        self.target.increase_health(2)
        self.target.taunt = True


class PowerOfTheWild(Card):
    def __init__(self):
        super().__init__("Power of the Wild", 2, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, False)

    def use(self, player, game):
        super().use(player, game)

        class LeaderOfThePack(Card):
            def __init__(self):
                super().__init__("Leader of the Pack", 0, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, False)

            def use(self, player, game):
                for minion in player.minions:
                    minion.increase_attack(1)
                    minion.increase_health(1)

        class SummonPanther(Card):
            def __init__(self):
                super().__init__("Summon a Panther", 0, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, False)

            def use(self, player, game):
                class Panther(MinionCard):
                    def __init__(self):
                        super().__init__("Panther", 2, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT)

                    def create_minion(self):
                        return Minion(3, 2, MINION_TYPES.BEAST)

                panther = Minion(3, 2, MINION_TYPES.BEAST)
                panther.add_to_board(Panther(), game, player, len(player.minions))



        option = player.agent.choose_option(LeaderOfThePack(), SummonPanther())
        option.use(player, game)


class WildGrowth(Card):
    def __init__(self):
        super().__init__("Wild Growth", 2, CHARACTER_CLASS.DRUID, CARD_STATUS.BASIC, False)

    def use(self, player, game):
        super().use(player, game)
        player.max_mana += 1

class Wrath(Card):
    def __init__(self):
        super().__init__("Wrath", 2, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):

        class WrathOne(Card):
            def __init__(self):
                super().__init__("Wrath 1 Damage", 2, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, True, hsgame.targetting.find_minion_spell_target)

            def use(self, player, game):
                target.spell_damage(1, wrath)
                player.draw()

        class WrathThree(Card):
            def __init__(self):
                super().__init__("Wrath 3 Damage", 2, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, True, hsgame.targetting.find_minion_spell_target)

            def use(self, player, game):
                target.spell_damage(3, wrath)

        super().use(player, game)
        option = game.current_player.agent.choose_option(WrathOne(), WrathThree())
        target = self.target
        wrath = self
        option.use(player, game)




class HealingTouch(Card):
    def __init__(self):
        super().__init__("Healing Touch", 3, CHARACTER_CLASS.DRUID, CARD_STATUS.BASIC, False)

    def use(self, player, game):
        super().use(player, game)
        player.heal(8)


class MarkOfNature(Card):
    def __init__(self):
        super().__init__("Mark of Nature", 3, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, True, hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        class MarkOfNatureAttack(Card):
            def __init__(self):
                super().__init__("Mark of Nature +4 Attack", 0, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, True, hsgame.targetting.find_minion_spell_target)

            def use(self, player, game):
                target.increase_attack(4)

        class MarkOfNatureHealth(Card):
            def __init__(self):
                super().__init__("Mark of Nature +4 Health", 0, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, True, hsgame.targetting.find_minion_spell_target)

            def use(self, player, game):
                target.increase_health(4)
                target.taunt = True

        super().use(player, game)
        target = self.target
        option = game.current_player.agent.choose_option(MarkOfNatureAttack(), MarkOfNatureHealth())
        option.use(player, game)


class SavageRoar(Card):
    def __init__(self):
        super().__init__("Savage Roar", 3, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, False)

    def use(self, player, game):
        super().use(player, game)
        for minion in player.minions:
            minion.increase_temp_attack(2)
        player.increase_attack(2)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) > 0


class Bite(Card):
    def __init__(self):
        super().__init__("Bite", 4, CHARACTER_CLASS.DRUID, CARD_STATUS.RARE, False)

    def use(self, player, game):
        super().use(player, game)
        player.increase_attack(4)
        player.increase_armour(4)

class SoulOfTheForest(Card):
    def __init__(self):
        super().__init__("Soul of the Forest", 4, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT, False)

    def use(self, player, game):

        def summon_treant(*args):
            class Treant(MinionCard):
                def __init__(self):
                    super().__init__("Treant", 1, CHARACTER_CLASS.DRUID, CARD_STATUS.EXPERT)

                def create_minion(self):
                    return Minion(2, 2, MINION_TYPES.NONE)

            treant = Minion(2, 2, MINION_TYPES.NONE)
            treant.add_to_board(Treant(), game, player, len(player.minions))

        super().use(player, game)
        for minion in player.minions:
            minion.bind("died", summon_treant, minion)
            minion.bind_once("silenced", lambda minion: minion.unbind("died", summon_treant), minion)



#Keeper of the Grove: Moonfire or Dispel

    #Power of the Wild: leader of the pack or summon a panther

    #mark of Nature: has no names