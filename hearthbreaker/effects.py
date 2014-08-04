from hearthbreaker.game_objects import Effect


class ImmuneThisTurn(Effect):
    def __init__(self, target, game):
        super().__init__("Immune This Turn", target, game)

    def apply(self):
        self.target.immune = True
        self.game.current_player.bind("turn_ended", self.remove_immunity)

    def unapply(self):
        self.game.current_player.unbind("turn_ended", self.remove_immunity)

    def remove_immunity(self):
        self.target.immune = False
