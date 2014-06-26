from hsgame.agents.basic_agents import DoNothingBot

__author__ = 'Daniel'


class SpellTestingAgent(DoNothingBot):
    def __init__(self, play_on=1):
        super().__init__()
        self.play_on = play_on
        self.turn = 0

    def do_turn(self, player):
        self.turn += 1
        while self.turn >= self.play_on and len(player.hand) > 0 and player.hand[0].can_use(player, self.game):
            self.game.play_card(player.hand[0])


class OneSpellTestingAgent(DoNothingBot):
    def do_turn(self, player):
        if len(player.hand) > 0 and player.hand[0].can_use(player, self.game):
            self.game.play_card(player.hand[0])


class SelfSpellTestingAgent(SpellTestingAgent):
    def __init__(self):
        super().__init__()

    def choose_target(self, targets):
        return self.game.current_player.hero


class EnemySpellTestingAgent(SpellTestingAgent):
    def __init__(self):
        super().__init__()

    def choose_target(self, targets):
        return self.game.other_player.hero


class EnemyMinionSpellTestingAgent(SpellTestingAgent):
    def __init__(self):
        super().__init__()

    def choose_target(self, targets):
        return self.game.other_player.minions[0]


class MinionPlayingAgent(DoNothingBot):
    def __init__(self):
        super().__init__()

    def do_turn(self, player):
        if len(player.hand) > 0 and player.hand[0].can_use(player, player.game):
            self.game.play_card(player.hand[0])


class MinionAttackingAgent(MinionPlayingAgent):
    def do_turn(self, player):
        super().do_turn(player)
        for minion in player.minions.copy():
            if minion.can_attack():
                minion.attack()

                
class PredictableAgentWithoutHeroPower(DoNothingBot):
    def do_turn(self, player):
        done_something = True

        while done_something:
            done_something = False
            for card in player.hand:
                if card.can_use(player, self.game):
                    self.game.play_card(card)
                    done_something = True

        if player.hero.can_attack():
            player.hero.attack()

        for minion in player.minions:
            if minion.can_attack():
                minion.attack()