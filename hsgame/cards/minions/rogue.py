import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import MinionCard, Minion
from hsgame.cards.battlecries import give_stealth


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

            if m is minion and m.player.cards_played > 0 and len(m.player.minions) < 7:
                bandit_card = DefiasBandit()
                bandit_card.summon(m.player, m.game, m.index + 1)

        minion = Minion(2, 2)
        player.bind_once("minion_played", combo)
        return minion


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
        super().__init__("Kidnapper", 6, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC,
                         hsgame.targeting.find_minion_battlecry_target)

    def create_minion(self, player):
        def combo(m):
            if m.card.target is not None and player.cards_played > 0:
                m.card.target.remove_from_board()
                if len(m.card.target.player.hand) < 10:
                    m.card.target.player.hand.append(m.card)

        minion = Minion(5, 3, battlecry=combo)
        return minion


class MasterOfDisguise(MinionCard):
    def __init__(self):
        super().__init__("Master of Disguise", 4, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE,
                         hsgame.targeting.find_friendly_minion_battlecry_target)

    def create_minion(self, player):
        minion = Minion(4, 4, battlecry=give_stealth)
        return minion


class PatientAssassin(MinionCard):
    def __init__(self):
        super().__init__("Patient Assassin", 2, CHARACTER_CLASS.ROGUE, CARD_RARITY.EPIC)

    def create_minion(self, player):
        def poisonous(amount, target):
            if type(target) is Minion:
                target.die(self)

        minion = Minion(1, 1)
        minion.stealth = True
        minion.bind("did_damage", poisonous)
        minion.bind_once("silenced", lambda: minion.unbind("did_damage", poisonous))
        return minion


class SI7Agent(MinionCard):
    def __init__(self):
        super().__init__("SI:7 Agent", 3, CHARACTER_CLASS.ROGUE, CARD_RARITY.RARE,
                         hsgame.targeting.find_battlecry_target)

    def create_minion(self, player):
        def combo(m):
            if m.card.target is not None and player.cards_played > 0:
                m.card.target.damage(2, self)

        minion = Minion(3, 3, battlecry=combo)
        return minion
