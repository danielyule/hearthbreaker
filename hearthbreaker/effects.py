from hearthbreaker.constants import MINION_TYPE
from hearthbreaker.game_objects import Effect


class ImmuneThisTurn(Effect):
    name = "Immune This Turn"

    def apply(self):
        self.target.immune = True
        self.target.game.current_player.bind("turn_ended", self.remove_immunity)

    def unapply(self):
        self.remove_immunity()
        self.target.game.current_player.unbind("turn_ended", self.remove_immunity)

    def remove_immunity(self):
        self.target.immune = False


class DrawOnBeast(Effect):
    name = "Draw On Beast"

    def apply(self):
        self.target.player.bind("minion_placed", self.check_beast_draw)

    def check_beast_draw(self, new_minion):
        if new_minion.minion_type is MINION_TYPE.BEAST and new_minion is not self.target:
            self.target.player.draw()

    def unapply(self):
        self.target.player.unbind("minion_placed", self.check_beast_draw)


class GrowOnBeastDeath(Effect):
    name = "Grow On Beast Death"

    def apply(self):
        self.target.player.bind("minion_died", self.hyena_grow)

    def unapply(self):
        self.target.player.unbind("minion_died", self.hyena_grow)

    def hyena_grow(self, dead_minion, by):
        if dead_minion is not self.target and dead_minion.minion_type is MINION_TYPE.BEAST:
            self.target.change_attack(2)
            self.target.increase_health(1)


class GiveChargeToBeasts(Effect):
    name = "Give Charge to Beasts"

    def __init__(self, target):
        super().__init__(target)
        self.affected_minions = []
        self.charged_minions = []

    def apply(self):

        for charge_minion in self.target.player.minions:
            self.give_charge_if_beast(charge_minion)

        self.target.bind("minion_played", self.give_charge_if_beast)

    def unapply(self):
        self.target.unbind("minion_played", self.give_charge_if_beast)

    def give_charge_if_beast(self, played_minion):
        def give_permacharge_effect(beast):
            def silenced():
                beast.charge = True

            def target_silenced():
                beast.unbind("silenced", silenced)
                beast.unbind("copied", copied)
                beast.charge = False

            def copied(new_minion, new_owner):
                new_minion.charge = False

            beast.charge = True
            self.affected_minions.append(beast)
            beast.bind("silenced", silenced)
            beast.bind("copied", copied)
            self.target.bind_once("silenced", target_silenced)

        def watch_for_silence(beast):
            def silenced():
                self.charged_minions.remove(beast)
                give_permacharge_effect(beast)
            beast.bind_once("silenced", silenced)
            self.target.bind_once("silenced", lambda: beast.unbind("silenced", silenced))
            self.charged_minions.append(beast)

        if played_minion.minion_type is MINION_TYPE.BEAST and not played_minion.charge:
            give_permacharge_effect(played_minion)
        elif played_minion.minion_type is MINION_TYPE.BEAST:
            watch_for_silence(played_minion)
