import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import MinionCard, Minion, Card
from hsgame.cards.battlecries import silence, deal_two_damage

__author__ = 'Daniel'


class KeeperOfTheGrove(MinionCard):
    def __init__(self):
        super().__init__("Keeper of the Grove", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE,
                         hsgame.targeting.find_minion_battlecry_target)

    def create_minion(self, player):

        class Moonfire(Card):
            def __init__(self):
                super().__init__("Moonfire", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE)

        class Dispel(Card):
            def __init__(self):
                super().__init__("Dispel", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE)

        moonfire = Moonfire()
        dispell = Dispel()
        option = player.agent.choose_option(moonfire, dispell)
        minion = Minion(2, 4)
        if option == moonfire:
            minion.bind("added_to_board", deal_two_damage)
        else:
            minion.bind("added_to_board", silence)

        return minion


class DruidOfTheClaw(MinionCard):

    def __init__(self):
        super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)

    def create_minion(self, player):

        #These are basically placeholders to give the agent something to choose
        class CatForm(Card):
            def __init__(self):
                super().__init__("Cat Form", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

        class BearForm(Card):
            def __init__(self):
                super().__init__("Bear Form", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

        cat = CatForm()
        bear = BearForm()
        option = player.agent.choose_option(cat, bear)
        if option is cat:
            minion = Minion(4, 4)
            minion.charge = True
        else:
            minion = Minion(4, 6)
            minion.taunt = True

        return minion


class AncientOfLore(MinionCard):

    def __init__(self):
        super().__init__("Ancient of Lore", 7, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC)

    def create_minion(self, player):

        #These are basically placeholders to give the agent something to choose
        class AncientSecrets(Card):
            def __init__(self):
                super().__init__("Ancient Secrets", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def use(self, player, game):
                player.hero.heal(5)

        class AncientTeachings(Card):
            def __init__(self):
                super().__init__("Ancient  Teachings", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def use(self, player, game):
                player.draw()
                player.draw()

        option = player.agent.choose_option(AncientSecrets(), AncientTeachings())
        option.use(player, player.game)

        return Minion(5, 5)


class AncientOfWar(MinionCard):

    def __init__(self):
        super().__init__("Ancient of War", 7, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC)

    def create_minion(self, player):

        #These are basically placeholders to give the agent something to choose
        class Health(Card):
            def __init__(self):
                super().__init__("+5 Health and Taunt", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

        class Attack(Card):
            def __init__(self):
                super().__init__("+5 Attack", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

        health = Health()
        attack = Attack()
        option = player.agent.choose_option(health, attack)
        minion = Minion(5, 5)
        if option is health:
            minion.increase_health(5)
            minion.taunt = True
        else:
            minion.increase_attack(5)

        return minion


class IronbarkProtector (MinionCard):

    def __init__(self):
        super().__init__("Ironbark Protector", 8, CHARACTER_CLASS.DRUID, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(8, 8)
        minion.taunt = True
        return minion


class Cenarius(MinionCard):

    def __init__(self):
        super().__init__("Cenarius", 9, CHARACTER_CLASS.DRUID, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):

        #These are basically placeholders to give the agent something to choose
        class IncreaseStats(Card):
            def __init__(self):
                super().__init__("Give your other minions +2/+2 and taunt", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def use(self, player, game):
                for minion in player.minions:
                    minion.increase_attack(2)
                    minion.increase_health(2)
                    minion.taunt = True

        class SummonTreants(Card):
            def __init__(self):
                super().__init__("Summon two 2/2 Treants with taunt", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def use(self, player, game):
                class Treant(MinionCard):
                    def __init__(self):
                        super().__init__("Treant", 1, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)

                    def create_minion(self, p):
                        minion = Minion(2, 2, MINION_TYPE.NONE)
                        minion.taunt = True
                        return minion
                #TODO Check if Cenarius summons the minions before or after himself
                for i in [0, 1]:
                    treant = Treant()
                    treant.create_minion(player).add_to_board(treant, game, player, 0)

        option = player.agent.choose_option(IncreaseStats(), SummonTreants())
        option.use(player, player.game)

        return Minion(5, 8)