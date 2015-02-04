import random
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.agents.trade_agent import TradeAgent
from hearthbreaker.cards import WarGolem, TheCoin
from hearthbreaker.game_objects import Game, MinionCard, Minion, Player
import re
from tests.testing_utils import generate_game_for


def t(self):
    return self.name
Minion.try_name = t


class TempCard(MinionCard):
    def __init__(self, base_attack=0, health=0, name="", taunt=False):
        self.base_attack = base_attack
        self.health = health
        self.name = name
        self.ref_name = name
        self.taunt = taunt
        self.mana = None
        self.minion_type = 0
        self.rarity = 0

    def create_minion(self, player):
        res = Minion(self.base_attack, self.health, taunt=self.taunt)
        res.name = self.name
        return res

    @staticmethod
    def make(s):
        taunt = False
        a, h = s.split("/")
        g = re.search("(\d+)t$", h)
        if g:
            taunt = True
            h = g.group(1)
        return TempCard(int(a), int(h), taunt=taunt, name=s)


class FakePlayer(Player):
    def __init__(self, name, deck, agent, game):
        super().__init__(name, deck, agent, game)
        self.draws_to_prevent = 1

    def draw(self):
        if self.draws_to_prevent == 0:
            return super().draw()
        else:
            self.draws_to_prevent -= 1


class FakeGame(Game):
    def __init__(self, decks, agents, random_func=random.randint):
        super(Game, self).__init__()
        self.delayed_minions = set()
        self.random_func = random_func
        self.first_player = random_func(0, 1)
        if self.first_player is 0:
            play_order = [0, 1]
        else:
            play_order = [1, 0]
        self.players = [FakePlayer("one", decks[play_order[0]], agents[play_order[0]], self),
                        FakePlayer("two", decks[play_order[1]], agents[play_order[1]], self)]
        self.current_player = self.players[0]
        self.other_player = self.players[1]
        self.current_player.opponent = self.other_player
        self.other_player.opponent = self.current_player
        self.game_ended = False
        self.minion_counter = 0
        self.__pre_game_run = False


class TestHelpers:
    @staticmethod
    def fix_create_minion(classes=None):
        if not classes:
            classes = MinionCard.__subclasses__()
        for cls in classes:
            TestHelpers.fix_create_minion_single(cls)

    @staticmethod
    def fix_create_minion_single(cls):
        if isinstance(cls, TheCoin):
            return

        if not hasattr(cls, "create_minion_old"):
            old = cls.create_minion
            cls.create_minion_old = old

            def create_minion_named_gen(self, player):
                res = old(self, player)
                res.name = self.name
                return res

            cls.create_minion = create_minion_named_gen

    def list_copy(self, list):
        return [c for c in list]

    def make_game(self, before_draw_callback=None):
        return generate_game_for(WarGolem, WarGolem, TradeAgent, RandomAgent)
