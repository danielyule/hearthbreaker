from hearthbreaker.agents.basic_agents import DoNothingAgent
from hearthbreaker.agents.trade.possible_play import PlayMixin
from hearthbreaker.agents.trade.trade import TradeMixin, AttackMixin
from hearthbreaker.agents.trade.util import Util
from hearthbreaker.tags.action import Damage
from hearthbreaker.tags.status import ChangeAttack, ChangeHealth


class BattlecryType:

    @staticmethod
    def target_type_for_card(card):
        res = None

        if hasattr(card, 'battlecry') and card.battlecry:
            for battlecry in card.battlecry:
                for action in battlecry.actions:
                    # TODO add more battlecries here
                    if isinstance(action, ChangeAttack) or isinstance(action, ChangeHealth):
                        res = "Friendly"
                    elif isinstance(action, Damage):
                        res = "Enemy"
        return res


class ChooseTargetMixin:
    def choose_target_enemy(self, all_targets):
        if len(all_targets) == 0:
            raise Exception("No targets")

        targets = self.prune_targets(all_targets, False)
        if len(targets) == 0:
            return Util.rand_el(all_targets)

        if not self.current_trade:
            return Util.rand_prefer_minion(targets)
            # raise Exception("No current trade")

        for target in targets:
            if self.current_trade.opp_minion == target:
                return target

        # raise Exception("Could not find target {}".format(target))
        return Util.rand_prefer_minion(targets)

    def choose_target_friendly(self, targets):
        pruned = self.prune_targets(targets, True)
        if len(pruned) == 0:
            return Util.rand_el(targets)

        return Util.rand_el(pruned)

    def prune_targets(self, targets, get_friendly):
        res = []
        for target in targets:
            is_friendly_minion = any(map(lambda c: c == target, self.player.minions))
            is_friendly_hero = target == self.player.hero
            is_friendly = is_friendly_minion or is_friendly_hero

            if is_friendly == get_friendly:
                res.append(target)

        return res

    def has_friendly_targets(self, targets):
        return len(self.prune_targets(targets, True)) > 0

    def should_target_self(self, targets):
        cry_type = BattlecryType.target_type_for_card(self.last_card_played)

        if cry_type == "Friendly":
            return True
        elif cry_type == "Enemy":
            return False
        elif self.last_card_played.name == "Elven Archerzzz":
            return False
        elif self.has_friendly_targets(targets):
            return True
        else:
            return False

    def choose_target_inner(self, targets):
        if len(targets) == 0:
            return None

        if self.should_target_self(targets):
            return self.choose_target_friendly(targets)
        else:
            return self.choose_target_enemy(targets)

    def choose_target(self, targets):
        res = self.choose_target_inner(targets)
        # print("Target {}".format(res))
        return res


class NullCard:
    def __init__(self):
        self.name = "Null Card"

    def create_minion(self, player):
        return None


class TradeAgent(TradeMixin, AttackMixin, PlayMixin, ChooseTargetMixin, DoNothingAgent):
    def __init__(self):
        super().__init__()
        self.current_trade = None
        self.last_card_played = NullCard()

    def do_turn(self, player):
        self.player = player
        self.play_cards(player)
        self.attack(player)

        if not player.game.game_ended:
            self.play_cards(player)

    def do_card_check(self, cards):
        return [True, True, True, True]

    def choose_index(self, card, player):
        return 0
