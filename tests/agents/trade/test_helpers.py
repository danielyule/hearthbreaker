from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.agents.trade_agent import TradeAgent
from hearthbreaker.cards import WarGolem
from hearthbreaker.cards.base import MinionCard
import re
from hearthbreaker.cards.spells.neutral import TheCoin
from hearthbreaker.game_objects import Minion
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
        self._attached = False
        self.effects = []
        self.buffs = []
        self.auras = []

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
