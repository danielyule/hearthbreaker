from hearthbreaker.game_objects import Effect


class ImmuneThisTurn(Effect):
    name = "Immune This Turn"

    def apply(self):
        self.target.immune = True
        self.game.current_player.bind("turn_ended", self.remove_immunity)

    def unapply(self):
        self.remove_immunity()
        self.game.current_player.unbind("turn_ended", self.remove_immunity)

    def remove_immunity(self):
        self.target.immune = False
