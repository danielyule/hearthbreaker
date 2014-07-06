from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import MinionCard, Minion


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
