from hsgame.agents.basic_agents import DoNothingBot

__author__ = 'Daniel'


class SpellTestingAgent(DoNothingBot):
    def __init__(self, play_on=1):
        super().__init__()
        self.play_on = play_on
        self.turn = 0

    def do_turn(self, player):
        self.turn += 1
        while self.turn >= self.play_on and len(player.hand) > 0 and self.game.current_player.mana >= player.hand[0].mana:
            self.game.play_card(player.hand[0])


class SelfSpellTestingAgent(SpellTestingAgent):
    def __init__(self):
        super().__init__()

    def choose_target(self, targets):
        return self.game.current_player


class EnemySpellTestingAgent(SpellTestingAgent):
    def __init__(self):
        super().__init__()

    def choose_target(self, targets):
        return self.game.other_player


class MyMinionSpellTestingAgent(SpellTestingAgent):
    def __init__(self):
        super().__init__()

    def choose_target(self, targets):
        return self.game.current_player.minions[0]


class EnemyMinionSpellTestingAgent(SpellTestingAgent):
    def __init__(self):
        super().__init__()

    def choose_target(self, targets):
        return self.game.other_player.minions[0]


class MinionPlayingAgent(DoNothingBot):
    def __init__(self):
        super().__init__()

    def do_turn(self, player):
        if len(player.hand) > 0 and player.mana >= player.hand[0].mana:
            self.game.play_card(player.hand[0])
