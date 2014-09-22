from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.agents.trade.possible_play import PlayMixin
from hearthbreaker.agents.trade.trade import TradeMixin, AttackMixin
from hearthbreaker.agents.trade.util import Util


class ChooseTargetMixin:
    def choose_target_enemy(self, targets):
        if len(targets) == 0:
            raise Exception("No targets")

        if not self.current_trade:
            return Util.rand_el(targets)
            # raise Exception("No current trade")

        for target in targets:
            if self.current_trade.opp_minion == target:
                return target

        # raise Exception("Could not find target {}".format(target))
        return Util.rand_el(targets)

    def choose_target_friendly(self, targets):
        return targets[0]

    def choose_target(self, targets):
        if len(targets) == 0:
            return None
        return self.choose_target_enemy(targets)


class TradeAgent(TradeMixin, AttackMixin, PlayMixin, ChooseTargetMixin, RandomAgent):
    def __init__(self):
        super().__init__()
        self.current_trade = None

    def do_turn(self, player):
        self.player = player
        self.play_cards(player)
        self.attack(player)

        if not player.game.game_ended:
            self.play_cards(player)
