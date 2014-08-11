from hearthbreaker.constants import MINION_TYPE
from hearthbreaker.game_objects import Effect, MinionCard, SecretCard, Minion


class KillMinion(Effect):
    """
    Kills a minion.  The minion can be killed at the end of the turn, or at the start of the
    casting player's next turn.
    """

    def __init__(self, when):
        """
        Creates a new KillMinion effect.

        :param string when: The event when this minion should die.  Possible values
                            are "turn_ended" and "turn_started".  These events refer to the casting player's turn
        """
        super().__init__()
        self.when = when

    def apply(self):
        self.target.game.current_player.bind(self.when, self.die)

    def unapply(self):
        self.target.game.current_player.unbind(self.when, self.die)

    def die(self):
        self.target.die(None)

    def __str__(self):
        return "KillMinion({0})".format(self.when)


class SummonOnDeath(Effect):
    """
    Causes a minion to summon another minion when it dies
    """
    def __init__(self, replacement, count=1):
        """
        Creates a new SummonOnDeath effect.

        :param class replacement: A MinionCard subclass that corresponds to the minion to summon.
                                  Should be a class, not an object.
        """
        super().__init__()
        self.replacement = replacement
        self.count = count
        self.old_death_rattle = None

    def apply(self):
        self.old_death_rattle = self.target.deathrattle
        self.target.deathrattle = self.summon_replacement

    def unapply(self):
        pass

    def summon_replacement(self, m):
        if self.old_death_rattle is not None:
            self.old_death_rattle(m)
        for i in range(0, self.count):
            replacement_card = self.replacement()
            replacement_card.summon(self.target.player, self.target.game, len(self.target.player.minions))

    def __str__(self):
        return "SummonOnDeath({0})".format(self.replacement().name)


class Immune(Effect):
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

    def __str__(self):
        return "Immune"


class DrawOnMinion(Effect):
    """
    Causes a card to be drawn every time a minion is played.  Can be given a specific type
    of minion to draw for.
    """

    def __init__(self, minion_type=MINION_TYPE.ALL):
        """
        Creates a new DrawOnMinion effect

        :param int minion_type: A member of :class:`MINION_TYPE` specifying the type of
                                minion to draw for, or `MINION_TYPE.ALL` for any minion
        """
        super().__init__()
        self.minion_type = minion_type

    def apply(self):
        self.target.player.bind("minion_placed", self.check_minion_draw)

    def check_minion_draw(self, new_minion):
        if (self.minion_type != MINION_TYPE.ALL and new_minion.card.minion_type is self.minion_type) \
                and new_minion is not self.target:
            self.target.player.draw()

    def unapply(self):
        self.target.player.unbind("minion_placed", self.check_minion_draw)

    def __str__(self):
        if self.minion_type == MINION_TYPE.ALL:
            return "DrawOnMinion(All)"
        return "DrawOnMinion({0})".format(MINION_TYPE.to_str(self.minion_type))


class GrowOnDeath(Effect):
    """
    Minions with this effect will grow every time another minion dies.

    The amount increased, as well as which players own the minions and what type o
    minions to monitor can all be customized
    """

    def __init__(self, attack, health, players="friendly", minion_type=MINION_TYPE.ALL):
        """
        :param int attack: The amount to increase this minion's attack by
        :param int health: The amount to increase this minion's health by
        :param string players: Whose minions should be watched.  Possible values are "friendly", "enemy" and "both"
        :param int minion_type: A member of :class:`MINION_TYPE` specifying the type of
                                minion whose death will cause an increase, or `MINION_TYPE.ALL` for any minion
        """
        super().__init__()
        self.attack = attack
        self.health = health
        self.players = players
        self.minion_type = minion_type

    def apply(self):
        if self.players == "friendly" or self.players == "both":
            self.target.player.bind("minion_died", self.minion_grow)
        if self.players == "enemy" or self.players == "both":
            self.target.player.opponent.bind("minion_died", self.minion_grow)

    def unapply(self):
        if self.players == "friendly" or self.players == "both":
            self.target.player.unbind("minion_died", self.minion_grow)
        if self.players == "enemy" or self.players == "both":
            self.target.player.opponent.unbind("minion_died", self.minion_grow)

    def minion_grow(self, dead_minion, by):
        if dead_minion is not self.target and \
                (self.minion_type == MINION_TYPE.ALL or dead_minion.card.minion_type is self.minion_type):
            self.target.change_attack(self.attack)
            self.target.increase_health(self.health)

    def __str__(self):
        if self.minion_type == MINION_TYPE.ALL:
            return "GrowOnDeath({0}, {1}, {2}, ALL)".format(self.attack, self.health, self.players)
        return "GrowOnDeath({0}, {1}, {2}, {3})".format(self.attack, self.health, self.players, self.minion_type)


class ChargeAura(Effect):
    """
    A Charge Aura gives affected minions charge.  Unlike other Auras, a ChargeAura can affect the minion giving the
    effect.  Whether the minions are friendly or not as well as what
    type of minions are affected can be customized
    """

    def __init__(self, players="friendly", minion_type=MINION_TYPE.ALL):
        """
        Create a new ChargeAura

        :param string players: Whose minions should be given charge.  Possible values are "friendly", "enemy" and "both"
        :param int minion_type: A member of :class:`MINION_TYPE` specifying the type of
                                minion who will be given charge or `MINION_TYPE.ALL` for any minion
        """
        super().__init__()
        self.affected_minions = []
        self.charged_minions = []
        self.players = players
        self.minion_type = minion_type

    def apply(self):
        if self.players == "friendly" or self.players == "both":
            for charge_minion in self.target.player.minions:
                self.give_charge_if_beast(charge_minion)

            self.target.player.bind("minion_played", self.give_charge_if_beast)

        if self.players == "enemy" or self.players == "both":
            for charge_minion in self.target.player.opponent.minions:
                self.give_charge_if_beast(charge_minion)

            self.target.player.opponent.bind("minion_played", self.give_charge_if_beast)

    def unapply(self):
        if self.players == "friendly" or self.players == "both":
            self.target.player.unbind("minion_played", self.give_charge_if_beast)

        if self.players == "enemy" or self.players == "both":
            self.target.player.opponent.unbind("minion_played", self.give_charge_if_beast)

    def give_charge_if_beast(self, played_minion):
        if played_minion is self.target and \
                (self.minion_type == MINION_TYPE.ALL or played_minion.card.minion_type == self.minion_type):
            self.target.charge = True
        else:
            def give_permacharge_effect(minion):
                def silenced():
                    minion.charge = True

                def target_silenced():
                    minion.unbind("silenced", silenced)
                    minion.unbind("copied", copied)
                    minion.charge = False

                def copied(new_minion, new_owner):
                    new_minion.charge = False

                minion.charge = True
                self.affected_minions.append(minion)
                minion.bind("silenced", silenced)
                minion.bind("copied", copied)
                self.target.bind_once("silenced", target_silenced)

            def watch_for_silence(minion):
                def silenced():
                    self.charged_minions.remove(minion)
                    give_permacharge_effect(minion)
                minion.bind_once("silenced", silenced)
                self.target.bind_once("silenced", lambda: minion.unbind("silenced", silenced))
                self.charged_minions.append(minion)

            if self.minion_type == MINION_TYPE.ALL or played_minion.card.minion_type is self.minion_type:
                if not played_minion.charge:
                    give_permacharge_effect(played_minion)
                else:
                    watch_for_silence(played_minion)

    def __str__(self):
        return "ChargeAura({0}, {1})".format(self.players, MINION_TYPE.to_str(self.minion_type))


class StatsAura(Effect):
    """
    A StatsAura increases the health and/or attack of affected minions.  Whether the minions are friendly or not as well
    as what type of minions are affected can be customized.
    """

    def __init__(self, attack=0, health=0, players="friendly", minion_type=MINION_TYPE.ALL):
        """
        Create a new StatsAura

        :param int attack: The amount to increase this minion's attack by
        :param int health: The amount to increase this minion's health by
        :param string players: Whose minions should be given charge.  Possible values are "friendly", "enemy" and "both"
        :param int minion_type: A member of :class:`MINION_TYPE` specifying the type of
                                minion who will be given charge or `MINION_TYPE.ALL` for any minion
        """
        super().__init__()
        self.attack = attack
        self.health = health
        self.players = players
        self.minion_type = minion_type

    def apply(self):
        if self.players == "friendly":
            players = [self.target.player]
        elif self.players == "enemy":
            players = [self.target.player.opponent]
        else:
            players = [self.target.player, self.target.player.opponent]
        if self.minion_type == MINION_TYPE.ALL:
            self.target.add_aura(self.attack, self.health, players)
        else:
            self.target.add_aura(self.attack, self.health, players,
                                 lambda minion: minion.card.minion_type == self.minion_type)

    def unapply(self):
        pass

    def __str__(self):
        if self.minion_type == MINION_TYPE.ALL:
            return "StatsAura({0}, {1}, {2}, ALL)".format(self.attack, self.health, self.players)
        return "StatsAura({0}, {1}, {2}, {3})".format(
            self.attack, self.health, self.players, MINION_TYPE.to_str(self.minion_type))


class IncreaseBattlecryMinionCost(Effect):

    def __init__(self, amount):
        super().__init__()
        self.amount = amount
        self.mana_filter = None

    def apply(self):
        amount = self.amount
        target = self.target

        class Filter:
            def __init__(self):
                self.amount = -amount
                self.filter = lambda c: isinstance(c, MinionCard) and \
                    c.create_minion(target.player).battlecry is not None
                self.min = 0

        self.mana_filter = Filter()
        self.target.game.current_player.mana_filters.append(self.mana_filter)
        self.target.game.other_player.mana_filters.append(self.mana_filter)

    def unapply(self):
        self.target.game.current_player.mana_filters.remove(self.mana_filter)
        self.target.game.other_player.mana_filters.remove(self.mana_filter)

    def __str__(self):
        return "IncreaseMinionCost(battlecry, {0})".format(self.amount)


class DoubleDeathrattle(Effect):

    def apply(self):
        if self.target.player.effect_count[DoubleDeathrattle] == 1:
            self.target.player.bind("minion_died", self.trigger_deathrattle)

    def unapply(self):
        if self.target.player.effect_count[DoubleDeathrattle] == 0:
            self.target.player.unbind("minion_died", self.trigger_deathrattle)

    def trigger_deathrattle(self, minion, killed_by):
        minion.deathrattle(minion)

    def __str__(self):
        return "DoubleDeathrattle()"


class HealAsDamage(Effect):

    def apply(self):
        if self.target.player.effect_count[HealAsDamage] == 1:
            self.target.player.heal_does_damage = True

    def unapply(self):
        if self.target.player.effect_count[HealAsDamage] == 0:
            self.target.player.heal_does_damage = False

    def __str__(self):
        return "HealAsDamage()"


class GrowOnSpell(Effect):
    """
    Grows each time a spell is played.  The type of how much attack
    and health should be increased can be specified
    """

    def __init__(self, attack, health):
        """
        Create a new GrowOnSpell

        :param int attack: How much to increase attack when a spell is played
        :param int health: How much to increase health when a spell is played
        """
        super().__init__()
        self.attack = attack
        self.health = health

    def apply(self):
        self.target.player.bind("spell_cast", self.increase_stats)

    def unapply(self):
        self.target.player.unbind("spell_cast", self.increase_stats)

    def increase_stats(self, card):
        if self.attack > 0:
            self.target.change_attack(self.attack)
        if self.health > 0:
            self.target.increase_health(self.health)

    def __str__(self):
        return "GrowOn(spell, {0}, {1})".format(self.attack, self.health)


class ManaFilter(Effect):
    """
    Associates a mana filter with this minion.  A mana filter affects a player by making cards of a certain type
    cost more or less.  The amount to change, player affected, and cards changed can all be customized
    """
    def __init__(self, amount, filter_type="card", minimum=0, player="friendly"):
        """
        Creates a new mana filter

        :param int amount: The amount to reduce mana by (can be negative)
        :param string filter_type: A filter to determine which cards can be affected.  Should be one of "card",
                                   "spell", "secret" or "minion"
        :param int minimum: The least amount that this filter can adjust the card to

        """
        super().__init__()
        self.amount = amount
        self.minimum = minimum
        self.filter_type = filter_type
        self.filter_object = None
        self.player = player

    def apply(self):
        if self.filter_type == "minion":
            my_filter = lambda c: isinstance(c, MinionCard)
        elif self.filter_type == "spell":
            my_filter = lambda c: c.is_spell()
        elif self.filter_type == "secret":
            my_filter = lambda c: isinstance(c, SecretCard)
        else:
            my_filter = lambda c: True

        class Filter:
            def __init__(self, amount, minimum, filter):
                self.amount = amount
                self.min = minimum
                self.filter = filter

        self.filter_object = Filter(self.amount, self.minimum, my_filter)
        if self.player == "friendly" or self.player == "both":
            self.target.player.mana_filters.append(self.filter_object)
        if self.player == "enemy" or self.player == "both":
            self.target.player.opponent.mana_filters.append(self.filter_object)

    def unapply(self):
        if self.player == "friendly" or self.player == "both":
            self.target.player.mana_filters.remove(self.filter_object)
        if self.player == "enemy" or self.player == "both":
            self.target.player.opponent.mana_filters.remove(self.filter_object)

    def __str__(self):
        return "ManaFilter({0}, {1}, {2}, {3})".format(self.amount, self.minimum, self.filter_type, self.player)


class GrowIfSecret(Effect):
    def __init__(self, attack, health):
        super().__init__()
        self.attack = attack
        self.health = health

    def apply(self):
        self.target.player.bind("turn_ended", self.increase_stats)

    def unapply(self):
        self.target.player.unbind("turn_ended", self.increase_stats)

    def increase_stats(self):
        if len(self.target.player.secrets) > 0:
            self.target.change_attack(self.attack)
            self.target.increase_health(self.health)

    def __str__(self):
        return "GrowIf(Secret, {0}, {1})".format(self.attack, self.health)


class AddCardOnSpell(Effect):
    def __init__(self, card):
        super().__init__()
        self.card = card

    def apply(self):
        self.target.player.bind("spell_cast", self.add_card)

    def unapply(self):
        self.target.player.unbind("spell_cast", self.add_card)

    def add_card(self, spell_card):
        if len(self.target.player.hand) < 10:
            self.target.player.hand.append(self.card())

    def __str__(self):
        return "AddOnSpell({0})".format(self.card().name)


class FreezeOnDamage(Effect):
    def __init__(self):
        super().__init__()

    def did_damage(self, amount, damaged_minion):
        damaged_minion.freeze()

    def apply(self):
        self.target.bind("did_damage", self.did_damage)

    def unapply(self):
        self.target.unbind("did_damage", self.did_damage)

    def __str__(self):
        return "OnDamage(freeze)"


class KillOnDamage(Effect):
    def __init__(self):
        super().__init__()

    def did_damage(self, amount, damaged_minion):
        if isinstance(damaged_minion, Minion):
            damaged_minion.die(None)
            self.target.game.check_delayed()

    def apply(self):
        self.target.bind("did_damage", self.did_damage)

    def unapply(self):
        self.target.unbind("did_damage", self.did_damage)

    def __str__(self):
        return "OnDamage(kill)"


class DrawOnAttack(Effect):
    """
    Draw some number of cards when this character attacks.  This effect will always affect a given player, regardless
    of who owns the minion
    """
    def __init__(self, amount=1, first_player=True):
        """
        Creates a new DrawOnAttack effect

        :param int amount: The number of cards to draw when attacking
        :param boolean first_player: True if this will draw cards for the first player, false to draw for the second
        """
        super().__init__()
        self.amount = amount
        self.first_player = first_player

    def apply(self):
        self.target.bind("attack", self.draw)

    def unapply(self):
        self.target.unbind("attack", self.draw)

    def draw(self, attack_target):
        if self.first_player:
            player = self.target.game.players[0]
        else:
            player = self.target.game.players[1]
        for i in range(0, self.amount):
            player.draw()

    def __str__(self):
        return("DrawOn(attack, {0})").format(self.amount)
