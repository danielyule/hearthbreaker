import copy
import json
import abc

from hearthbreaker.constants import MINION_TYPE
import hearthbreaker.game_objects


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
            "buff_temp": BuffTemp,
            "kill": Kill,
            "damage": Damage,
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


class TranientEffect(MinionEffect):
    """
    TransientEffects are used only for serialization and de-serialization
    What they do is tracked by the game engine itself, and doesn't need an effect in the list of effects.
    As such, these effects are generated at the time a minion is serialized, and removed when it is deserialized
    """

    def unapply(self):
        pass


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


class EventEffect(MinionEffect, metaclass=abc.ABCMeta):
    def __init__(self, when, minion_filter, target, players, include_self, target_self):
        super().__init__()
        self.when = when
        self.minion_filter = minion_filter
        self.action_target = target
        self.players = players
        self.include_self = include_self
        self.target_self = target_self
        self.other = None

    def apply(self):
        if self.players == "friendly":
            players = [self.target.player]
        elif self.players == "enemy":
            players = [self.target.player.opponent]
        elif self.players == "both":
            players = [self.target.player, self.target.player.opponent]
        else:
            raise RuntimeError("Required players to be 'friendly', 'enemy', or 'both', got '{0}".format(self.players))

        if self.when == "death":
            for player in players:
                player.bind("minion_died", self._check_minion_filter)
        elif self.when == "damaged":
            for player in players:
                player.bind("minion_damaged", self._check_minion_filter)
        elif self.when == "summoned":
            for player in players:
                player.bind("minion_summoned", self._check_minion_filter)
        elif self.when == "played":
            if self.minion_filter == "spell" or self.minion_filter == "secret" or self.minion_filter == "card":
                for player in players:
                    player.bind("card_played", self._check_card_filter)
            else:
                for player in players:
                    player.bind("minion_played", self._check_minion_filter)
        elif self.when == "placed":
            for player in players:
                player.bind("minion_placed", self._check_minion_filter)
        elif self.when == "after_added":
            for player in players:
                player.bind("after_minion_added", self._check_minion_filter)
        elif self.when == "attack":
            self.target.bind("attack", self._check_minion_filter)
        elif self.when == "attacked":
            self.target.bind("attacked", self._check_minion_filter)
        elif self.when == "did_damage":
            self.target.bind("did_damage", self._check_minion_filter)
        elif self.when == "enraged":
            if self.action_target == "self":
                self.target.bind("enraged", self._do_enraged_action)
                self.target.bind("unenraged", self._undo_enraged_action)
        elif self.when == "overloaded":
            for player in players:
                player.bind("overloaded", self._check_turn_end_filter)
        elif self.when == "turn_ended":
            for player in players:
                player.bind("turn_ended", self._check_turn_end_filter)
        elif self.when == "turn_started":
            for player in players:
                player.bind("turn_started", self._check_turn_end_filter)

    def unapply(self):
        if self.players == "friendly":
            players = [self.target.player]
        elif self.players == "enemy":
            players = [self.target.player.opponent]
        elif self.players == "both":
            players = [self.target.player, self.target.player.opponent]
        else:
            raise RuntimeError("Required players to be 'friendly', 'enemy', or 'both', got '{0}".format(self.players))

        if self.when == "death":
            for player in players:
                player.unbind("minion_died", self._check_minion_filter)
        elif self.when == "damaged":
            for player in players:
                player.unbind("minion_damaged", self._check_minion_filter)
        elif self.when == "summoned":
            for player in players:
                player.unbind("minion_summoned", self._check_minion_filter)
        elif self.when == "played":
            if self.minion_filter == "spell" or self.minion_filter == "secret" or self.minion_filter == "card":
                for player in players:
                    player.unbind("card_played", self._check_card_filter)
            else:
                for player in players:
                    player.unbind("minion_played", self._check_minion_filter)
        elif self.when == "placed":
            for player in players:
                player.unbind("minion_placed", self._check_minion_filter)
        elif self.when == "after_added":
            for player in players:
                player.unbind("after_minion_added", self._check_minion_filter)
        elif self.when == "attack":
            self.target.unbind("attack", self._check_minion_filter)
        elif self.when == "attacked":
            self.target.unbind("attacked", self._check_minion_filter)
        elif self.when == "did_damage":
            self.target.unbind("did_damage", self._check_minion_filter)
        elif self.when == "overloaded":
            for player in players:
                player.unbind("overloaded", self._check_turn_end_filter)
        elif self.when == "turn_ended":
            for player in players:
                player.unbind("turn_ended", self._check_turn_end_filter)
        elif self.when == "turn_started":
            for player in players:
                player.unbind("turn_started", self._check_turn_end_filter)

    def _check_minion_filter(self, minion, *args):
        self.other = minion
        if self.minion_filter == "self":
            if minion == self.target:
                self._select_target()
        elif self.include_self or minion is not self.target:
            if self.minion_filter == "minion":
                self._select_target()
            elif self.minion_filter == "deathrattle" and minion.deathrattle is not None:
                self._select_target()
            elif self.minion_filter == "attack_less_than_or_equal_to_3" and minion.calculate_attack() <= 3:
                self._select_target()
            elif self.target is not minion:
                try:
                    type_id = MINION_TYPE.from_str(self.minion_filter)
                    if minion.card.minion_type == type_id:
                        self._select_target()
                except KeyError:
                    pass

    def _check_card_filter(self, card, index):
        if self.minion_filter == "spell" and card.is_spell():
            self._select_target()
        elif self.minion_filter == "secret" and isinstance(card, hearthbreaker.game_objects.SecretCard):
            self._select_target()
        elif self.minion_filter == "card":
            self._select_target()

    def _check_turn_end_filter(self):
        if self.minion_filter != "secret" or len(self.target.player.secrets) > 0:
            self._select_target()

    def _select_target(self):
        if self.action_target == "self":
            self._do_action(self.target)
        elif self.action_target == "other":
            self._do_action(self.other)
        elif self.action_target == "all":
            targets = copy.copy(self.target.player.minions)
            targets.append(self.target.player.hero)
            if not self.target_self:
                targets.remove(self.target)
            targets.extend(self.target.player.opponent.minions)
            targets.append(self.target.player.opponent.hero)
            for target in targets:
                self._do_action(target)
        elif self.action_target == "minion":
            targets = copy.copy(self.target.player.minions)
            if not self.target_self:
                targets.remove(self.target)
            targets.extend(self.target.player.opponent.minions)
            for target in targets:
                self._do_action(target)
        else:
            if self.action_target == "random_minion":
                targets = copy.copy(self.target.player.minions)
                targets.extend(self.target.player.opponent.minions)
                if not self.target_self:
                    targets.remove(self.target)
            elif self.action_target == "random_friendly_minion":
                targets = copy.copy(self.target.player.minions)
                if not self.target_self:
                    targets.remove(self.target)
            elif self.action_target == "random_friendly":
                targets = copy.copy(self.target.player.minions)
                targets.append(self.target.player.hero)
                if not self.target_self:
                    targets.remove(self.target)
            elif self.action_target == "random_enemy_minion":
                targets = copy.copy(self.target.player.opponent.minions)
            elif self.action_target == "random_enemy":
                targets = copy.copy(self.target.player.opponent.minions)
                targets.append(self.target.player.opponent.hero)
            else:
                raise RuntimeError("Expected 'target' to be one of 'self', 'other', 'random', " +
                                   "'random_friendly' or 'random_enemy'.  Got '{0}'".format(self.action_target))
            if len(targets) > 0:
                target = self.target.game.random_choice(targets)
                self._do_action(target)

    @abc.abstractmethod
    def _do_action(self, target):
        pass

    def __str__(self):
        return json.dumps(self.__to_json__())

    def __to_json__(self):
        return {
            "when": self.when,
            "minion_filter": self.minion_filter,
            "target": self.action_target,
            "players": self.players,
            "include_self": self.include_self,
            "target_self": self.target_self,
        }


class ReversibleEffect(EventEffect, metaclass=abc.ABCMeta):
    def apply(self):
        if self.when == "enraged":
            if self.action_target == "self":
                self.target.bind("enraged", self._do_enraged_action)
                self.target.bind("unenraged", self._undo_enraged_action)
        else:
            super().apply()

    def unapply(self):
        if self.when == "enraged":
            if self.action_target == "self":
                self.target.unbind("enraged", self._do_enraged_action)
                self.target.unbind("unenraged", self._undo_enraged_action)
        else:
            super().unapply()

    def _do_enraged_action(self):
        self._do_action(self.target)

    def _undo_enraged_action(self):
        self._undo_action(self.target)

    @abc.abstractmethod
    def _undo_action(self, target):
        pass


class BuffTemp(EventEffect):
    def __init__(self, when, minion_filter="self", target="self", attack=0, players="friendly",
                 include_self=False, target_self=False):
        super().__init__(when, minion_filter, target, players, include_self, target_self)
        self.attack = attack

    def _do_action(self, target):
        if self.attack != 0:
            target.temp_attack += self.attack

    def __to_json__(self):
        s_json = super().__to_json__()
        s_json.update({
            "action": "buff_temp",
            "attack": self.attack,
        })
        return s_json


class Kill(EventEffect):
    def __init__(self, when, minion_filter="self", target="self", players="friendly", include_self=False,
                 target_self=False):
        super().__init__(when, minion_filter, target, players, include_self, target_self)

    def _do_action(self, target):
        if isinstance(target, hearthbreaker.game_objects.Minion):
            target.die(None)

    def __to_json__(self):
        s_json = super().__to_json__()
        s_json.update({
            "action": "kill",
        })
        return s_json


class Damage(EventEffect):
    def __init__(self, when, amount, minion_filter="self", target="self", players="friendly", include_self=False,
                 target_self=False):
        super().__init__(when, minion_filter, target, players, include_self, target_self)
        self.amount = amount

    def _do_action(self, target):
        if isinstance(target, hearthbreaker.game_objects.Character):
            target.damage(self.amount, self.target)

    def __to_json__(self):
        s_json = super().__to_json__()
        s_json.update({
            "action": "damage",
            "amount": self.amount
        })
        return s_json


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
