from hearthbreaker.effects.minion import Taunt
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import MinionCard, Minion, Card
from hearthbreaker.cards.battlecries import silence, deal_two_damage


class KeeperOfTheGrove(MinionCard):
    def __init__(self):
        super().__init__("Keeper of the Grove", 4, CHARACTER_CLASS.DRUID, CARD_RARITY.RARE)

    def create_minion(self, player):

        class Moonfire(Card):
            def __init__(self):
                super().__init__("Moonfire", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

        class Dispel(Card):
            def __init__(self):
                super().__init__("Dispel", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

        moonfire = Moonfire()
        dispell = Dispel()
        option = player.agent.choose_option(moonfire, dispell)
        minion = Minion(2, 4)
        if option == moonfire:
            action = deal_two_damage
            targets = hearthbreaker.targeting.find_battlecry_target(player.game, lambda m: not m.stealth)
        else:
            action = silence
            targets = hearthbreaker.targeting.find_minion_battlecry_target(player.game, lambda m: not m.stealth)

        if targets is not None:
            self.target = player.agent.choose_target(targets)

        # here we have to set these things up to mimic a battlecry, although it is not a battlecry
        minion.card = self
        action(minion)

        return minion


class DruidOfTheClaw(MinionCard):
    def __init__(self):
        super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.COMMON)

    def create_minion(self, player):

        # These are basically placeholders to give the agent something to
        # choose
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
            class CatDruid(MinionCard):
                def __init__(self):
                    super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

                def create_minion(self, p):
                    return Minion(4, 4, charge=True)

            druid = CatDruid()
        else:
            class BearDruid(MinionCard):
                def __init__(self):
                    super().__init__("Druid of the Claw", 5, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

                def create_minion(self, p):
                    return Minion(4, 6, taunt=True)
            druid = BearDruid()

        def set_card(m):
            m.card = druid
        minion = druid.create_minion(player)
        player.bind_once("minion_played", set_card)
        return minion


class AncientOfLore(MinionCard):
    def __init__(self):
        super().__init__("Ancient of Lore", 7, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC)

    def create_minion(self, player):
        # These are basically placeholders to give the agent something to
        # choose.  Note the lack of call to super().use()
        class AncientSecrets(Card):
            def __init__(self):
                super().__init__("Ancient Secrets", 0, CHARACTER_CLASS.DRUID,
                                 CARD_RARITY.SPECIAL)

            def use(self, player, game):
                player.hero.heal(player.effective_heal_power(5), self)

        class AncientTeachings(Card):
            def __init__(self):
                super().__init__("Ancient  Teachings", 0, CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def use(self, player, game):
                player.draw()
                player.draw()

        option = player.agent.choose_option(AncientSecrets(),
                                            AncientTeachings())
        option.use(player, player.game)

        return Minion(5, 5)


class AncientOfWar(MinionCard):
    def __init__(self):
        super().__init__("Ancient of War", 7, CHARACTER_CLASS.DRUID, CARD_RARITY.EPIC)

    def create_minion(self, player):

        # These are basically placeholders to give the agent something to
        # choose
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
            minion._effects_to_add.append(Taunt())
        else:
            minion.change_attack(5)

        return minion


class IronbarkProtector(MinionCard):
    def __init__(self):
        super().__init__("Ironbark Protector", 8, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.COMMON)

    def create_minion(self, player):
        return Minion(8, 8, taunt=True)


class Cenarius(MinionCard):
    def __init__(self):
        super().__init__("Cenarius", 9, CHARACTER_CLASS.DRUID,
                         CARD_RARITY.LEGENDARY)

    def create_minion(self, player):

        # These are basically placeholders to give the agent something to
        # choose
        class IncreaseStats(Card):
            def __init__(self):
                super().__init__("Give your other minions +2/+2 and taunt", 0,
                                 CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def use(self, player, game):
                for minion in player.minions:
                    if minion is not cenarius:
                        minion.change_attack(2)
                        minion.increase_health(2)
                        minion.taunt = True

            def invoke(self, minion, index):
                self.use(minion.player, minion.game)

        class SummonTreants(Card):
            def __init__(self):
                super().__init__("Summon two 2/2 Treants with taunt", 0,
                                 CHARACTER_CLASS.DRUID, CARD_RARITY.SPECIAL)

            def use(self, player, game):
                class Treant(MinionCard):
                    def __init__(self):
                        super().__init__("Treant", 1, CHARACTER_CLASS.DRUID,
                                         CARD_RARITY.COMMON)

                    def create_minion(self, p):
                        minion = Minion(2, 2, MINION_TYPE.NONE)
                        minion.taunt = True
                        return minion
                ltreant = Treant()
                ltreant.summon(player, game, cenarius.index)
                rtreant = Treant()
                rtreant.summon(player, game, cenarius.index + 1)

            def invoke(self, minion, index):
                self.use(minion.player, minion.game)

        option = player.agent.choose_option(IncreaseStats(), SummonTreants())
        cenarius = Minion(5, 8)
        cenarius.bind_once("added_to_board", option.invoke)
        return cenarius
