import json
import abc


class MinionEffect(metaclass=abc.ABCMeta):
    def __init__(self):
        self.target = None

    def set_target(self, target):
        self.target = target

    @abc.abstractmethod
    def apply(self):
        pass

    @abc.abstractmethod
    def unapply(self):
        pass

    def __str__(self):
        return json.dumps(self.__to_json__())

    @abc.abstractmethod
    def __to_json__(self):
        pass

    @staticmethod
    def from_json(game, action, *args, **kwargs):
        __class_mappings = {
            "immune": Immune,
            "double_deathrattle": DoubleDeathrattle,
            "heal_as_damage": HealAsDamage,
            "resurrect_friendly": ResurrectFriendlyMinionsAtEndOfTurn,
            "original_deathrattle": OriginalDeathrattle,
        }
        if action in __class_mappings:
            clazz = __class_mappings[action]
            obj = clazz(*args, **kwargs)
            return obj
        else:
            return None


class Immune(MinionEffect):
    """
    Gives a character immunity.  This immunity will last until the end of the player' turn
    """

    def apply(self):
        self.target.immune = True
        self.target.game.current_player.bind("turn_ended", self.remove_immunity)

    def unapply(self):
        self.remove_immunity()
        self.target.game.current_player.unbind("turn_ended", self.remove_immunity)

    def remove_immunity(self):
        self.target.immune = False

    def __to_json__(self):
        return {
            "action": "immune",
        }


class DoubleDeathrattle(MinionEffect):
    def apply(self):
        if self.target.player.effect_count[DoubleDeathrattle] == 1:
            self.target.player.bind("minion_died", self.trigger_deathrattle)

    def unapply(self):
        if self.target.player.effect_count[DoubleDeathrattle] == 0:
            self.target.player.unbind("minion_died", self.trigger_deathrattle)

    def trigger_deathrattle(self, minion, killed_by):
        if minion.deathrattle is not None:
            minion.deathrattle(minion)

    def __to_json__(self):
        return {
            "action": "double_deathrattle",
        }


class HealAsDamage(MinionEffect):
    def apply(self):
        if self.target.player.effect_count[HealAsDamage] == 1:
            self.target.player.heal_does_damage = True

    def unapply(self):
        if self.target.player.effect_count[HealAsDamage] == 0:
            self.target.player.heal_does_damage = False

    def __to_json__(self):
        return {
            "action": "heal_as_damage",
        }


class ResurrectFriendlyMinionsAtEndOfTurn(MinionEffect):
    def __init__(self):
        super().__init__()

    def apply(self):
        self.target.player.bind("turn_ended", self._turn_ended)
        self.target.player.opponent.bind("turn_ended", self._turn_ended)

    def unapply(self):
        self.target.player.unbind("turn_ended", self._turn_ended)
        self.target.player.opponent.unbind("turn_ended", self._turn_ended)

    def _turn_ended(self):
        # Will be called once per Kel'Thuzad on the board
        # http://www.hearthhead.com/card=1794/kelthuzad#comments
        for minion in sorted(self.target.player.dead_this_turn, key=lambda m: m.born):
            minion.card.summon(self.target.player, self.target.game, len(self.target.player.minions))

    def __to_json__(self):
        return {
            "action": "resurrect_friendly"
        }

    def __str__(self):
        return ""


class OriginalDeathrattle(MinionEffect):
    def __init__(self):
        super().__init__()

    def apply(self):
        self.target.deathrattle = self.target.card.create_minion(self.target.player).deathrattle

    def unapply(self):
        self.target.deathrattle = None

    def __to_json__(self):
        return {
            "action": "original_deathrattle"
        }
