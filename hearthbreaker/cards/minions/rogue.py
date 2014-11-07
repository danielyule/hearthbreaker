import copy
from hearthbreaker.tags.action import Kill, Bounce
from hearthbreaker.tags.base import Effect, Deathrattle
from hearthbreaker.tags.condition import IsMinion
from hearthbreaker.tags.event import DidDamage
from hearthbreaker.tags.selector import TargetSelector, RandomSelector, MinionSelector
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.game_objects import MinionCard, Minion
from hearthbreaker.cards.battlecries import give_stealth


class DefiasRingleader(MinionCard):
    def __init__(self):
        super().__init__("Defias Ringleader", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def combo(m):
            class DefiasBandit(MinionCard):
                def __init__(self):
                    super().__init__("Defias Bandit", 1, CHARACTER_CLASS.ROGUE, CARD_RARITY.SPECIAL)

                def create_minion(self, player):
                    return Minion(2, 1)

            if m.player.cards_played > 0:
                bandit_card = DefiasBandit()
                bandit_card.summon(m.player, m.game, m.index + 1)

        player.bind_once("minion_placed", combo)
        return Minion(2, 2)


class EdwinVanCleef(MinionCard):
    def __init__(self):
        super().__init__("Edwin VanCleef", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.LEGENDARY)

    def create_minion(self, player):
        minion = Minion(2, 2)
        for combo in range(0, player.cards_played):
            minion.increase_health(2)
            minion.change_attack(2)

        return minion


class Kidnapper(MinionCard):
    def __init__(self):
        super().__init__("Kidnapper", 6, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC)

    def create_minion(self, player):
        def combo(minion):
            if player.cards_played > 0:
                if targets is not None:
                    target = player.agent.choose_target(targets)
                    if target is not None:
                        target.bounce()

        targets = hearthbreaker.targeting.find_minion_battlecry_target(player.game, lambda m: m.player is player
                                                                       or not m.stealth)
        player.bind_once("minion_placed", combo)
        return Minion(5, 3)


class MasterOfDisguise(MinionCard):
    def __init__(self):
        super().__init__("Master of Disguise", 4, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE,
                         targeting_func=hearthbreaker.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        return Minion(4, 4, battlecry=give_stealth)


class PatientAssassin(MinionCard):
    def __init__(self):
        super().__init__("Patient Assassin", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC)

    def create_minion(self, player):
        return Minion(1, 1, stealth=True, effects=[Effect(DidDamage(), Kill(), TargetSelector(IsMinion()))])


class SI7Agent(MinionCard):
    def __init__(self):
        super().__init__("SI:7 Agent", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE)

    def create_minion(self, player):
        def combo(minion):
            if player.cards_played > 0:
                if targets is not None:
                    target = player.agent.choose_target(targets)
                    if target is not None:
                        target.damage(2, self)

        targets = hearthbreaker.targeting.find_battlecry_target(player.game, lambda c: c.player is player
                                                                or not c.stealth)
        player.bind_once("minion_placed", combo)
        return Minion(3, 3)


class AnubarAmbusher(MinionCard):
    def __init__(self):
        super().__init__("Anub'ar Ambusher", 4, CHARACTER_CLASS.ROGUE, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def return_random_friendly_minion(minion):
            targets = copy.copy(minion.player.minions)

            if len(targets) > 0:
                minion.game.random_choice(targets).bounce()

        return Minion(5, 5, deathrattle=Deathrattle(Bounce(), RandomSelector(MinionSelector())))
