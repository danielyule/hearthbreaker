import copy


class DoNothingBot:
    def __init__(self):
        self.game = None

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        pass

    def set_game(self, game):
        self.game = game

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card):
        return 0

    def choose_option(self, *options):
        return options[0]


class PredictableBot:
    def __init__(self):
        self.game = None

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        done_something = True

        if player.hero.power.can_use():
            player.hero.power.use()

        if player.hero.can_attack():
            player.hero.attack()

        while done_something:
            done_something = False
            for card in copy.copy(player.hand):
                if card.can_use(player, self.game):
                    self.game.play_card(card)
                    done_something = True

        for minion in copy.copy(player.minions):
            if minion.can_attack():
                minion.attack()

    def set_game(self, game):
        self.game = game

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card):
        return 0

    def choose_option(self, *options):
        return options[0]
