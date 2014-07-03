import random
import abc

import hsgame.powers
import hsgame.targeting
import hsgame.constants

card_table = {}


def card_lookup(card_name):
    """
    Given a the name of a card as a string, return an object corresponding to that card

    :param str card_name: A string representing the name of the card in English
    :return: An instance of a subclass of Card corresponding to the given card name or None if no Card
             by that name exists.
    :rtype: hsgame.game_objects.Card
    """

    def card_lookup_rec(card_type):
        subclasses = card_type.__subclasses__()
        if len(subclasses) is 0:
            c = card_type()
            card_table[c.name] = card_type
        for sub_type in subclasses:
            card_lookup_rec(sub_type)

    if len(card_table) == 0:
        for card_type in Card.__subclasses__():
            card_lookup_rec(card_type)

    card = card_table[card_name]
    if card is not None:
        return card()
    return None


class GameException(Exception):
    """
    An :class:`Exception` relating to the operation of the game
    """

    def __init__(self, message):
        super().__init__(message)


class Bindable:
    """
    A class which inherits from Bindable has an event structure added to it.

    This event structure follows the observer pattern.  It consists of two parts: binding and triggering.
    A function handler is bound to an event using the :meth:`bind` or :meth:`bind_once` methods.  When the event is
    triggered using the :meth:`trigger` method, then any function handlers which have been bound to that event are
    called.

    Arguments can be passed to a bound function when binding or when triggering, or both.  Arguments from triggering
    are passed first, followed by arguments from binding.

    Functions can be bound such that they are called each time an event is triggered, or so that they are only called
    the next time a function is triggered.  The former case is handled by :meth:`bind` and the latter by
    :meth:`bind_once`

    **Examples**:

    Simple Binding::

       class EventTarget(Bindable):
           def __init__(self):
               super().__init__()

       def handler(fangs, scales):
           print("fangs: {:d}, scales: {:d}".format(fangs, scales))

       target = EventTarget()
       target.bind("attack", handler, 1001)
       target.trigger("attack", 2)             # outputs "fangs: 2, scales: 1001"
       target.trigger("attack", 6)             # outputs "fangs: 6, scales: 1001"

    Binding Once::

       class EventTarget(Bindable):
           def __init__(self):
               super().__init__()

       def handler(joke):
            print("{:s}! HAHAHA".format(joke))

       target = EventTarget()
       target.bind_once("joke_told", handler)

       # outputs "Well, I'd better replace it then! HAHAHA"
       target.trigger("joke_told", "Well, I'd better replace it then")

       # outputs nothing
       target.trigger("joke_told", "What a senseless waste of human life")

    Any class which subclasses this class must be sure to call :meth:`__init__`
    """

    def __init__(self):
        """
        Set up a new :class:`Bindable`.  Must be called by any subclasses.
        """
        self.events = {}

    def bind(self, event, function, *args):
        """
        Bind a function to an event.  Each time the event is triggered, the function will be called.

        Any parameters passed to this method will be appended to the paramters passed to the trigger function
        and passed to the bound function.

        :param event str: The event to bind a function to
        :param function function: The function to bind.  The parameters are not checked until it is called, so
                                  ensure its signature matches the parameters called from :meth:`trigger`
        :param list args: Any other parameters to be called
        :see: :class:`Bindable`
        """

        class Handler:
            def __init__(self):
                self.args = args
                self.function = function
                self.remove = False
                self.active = False

        if event not in self.events:
            self.events[event] = []

        self.events[event].append(Handler())

    def bind_once(self, event, function, *args):
        """
        Bind a function to an event.  This function will only be called the next time the event is triggered, and
        then ignored.

        Any parameters passed to this method will be appended to the paramters passed to the trigger function
        and passed to the bound function.

        :param event str: The event to bind a function to
        :param function function: The function to bind.  The parameters are not checked until it is called, so
                                  ensure its signature matches the parameters called from :meth:`trigger`
        :param args: Any other parameters to be called
        :see: :class:`Bindable`
        """

        class Handler:
            def __init__(self):
                self.args = args
                self.function = function
                self.remove = True
                self.active = False

        if event not in self.events:
            self.events[event] = []

        self.events[event].append(Handler())

    def trigger(self, event, *args):
        """
        Trigger an event.  Any functions which have been bound to that event will be called.

        The parameters passed to this function as `args` will be passed along to the bound functions.

        :param string event: The name of the event to trigger
        :param list args: The remaining arguments to pass to the bound function
        :see: :class:`Bindable`
        """
        if event in self.events:
            for handler in self.events[event].copy():
                if not handler.active:
                    pass_args = args + handler.args
                    handler.active = True
                    handler.function(*pass_args)
                    handler.active = False
                    if handler.remove:
                        self.events[event].remove(handler)
                        # tidy up the events dict so we don't have entries for events with no handlers
                        if len(self.events[event]) is 0:
                            del (self.events[event])

    def unbind(self, event, function):
        """
        Unbind a function from an event.  When this event is triggered, the function is no longer called.

        `function` must be the same function reference as was passed in to :meth:`bind` or :meth:`bind_once`

        :param string event: The event to unbind the function from
        :param function function: The function to unbind.
        """
        if event in self.events:
            self.events[event] = [handler for handler in self.events[event] if not handler.function == function]
            if len(self.events[event]) is 0:
                del (self.events[event])


class Character(Bindable, metaclass=abc.ABCMeta):
    """
    A Character in Hearthstone is something that can attack, i.e. a :class:`Hero` or :class:`Minion`.

     This common superclass handles all of the status effects and calculations involved in attacking or being attacked.
    """

    def __init__(self, attack_power, health):
        """
        Create a new Character with the given attack power and health

        :param int attack_power: the amount of attack this character has at creation
        :param int health: the maximum health of this character
        """
        super().__init__()

        # : The current health of this character
        self.health = health
        # : The maximum health of this character
        self.max_health = health
        #: The amount of attack this character has
        self.attack_power = attack_power
        #: Whether or not this character can attack this turn
        self.active = False
        #: Whether or not this character has died
        self.dead = False
        #: If this character has windfury
        self.windfury = False
        #: If this character has used their first windfury attack
        self.used_windfury = False
        #: If this character is currently frozen
        self.frozen = False
        #: If the character was frozen this turn (and so won't be unfrozen before the next turn)
        self.frozen_this_turn = False
        #: The amount this character's attack is raised this turn
        self.temp_attack = 0
        #: The :class:`Player` that owns this character
        self.player = None
        #: Whether or not this character is immune to damage (but not other effects)
        self.immune = False
        #: The list of delayed events
        self.delayed = []
        #: If this character has stealth
        self.stealth = False

    def _turn_complete(self):
        """
        Called at the end of the turn.  Takes care of any end of turn cleanup that should happen
        outside of any specifically bound handlers
        """
        if self.temp_attack > 0:
            self.trigger("attack_decreased", self.temp_attack)
            self.temp_attack = 0

    def attack(self):
        """
        Causes this :class:`Character` to attack.

        The Character will assemble a list of possible targets and then ask the agent associated with this Character to
        select which target from the list it would like to attack.

        This method will not succeed if the Character can't attack, either because it is not active, or it is frozen,
        or some other factor.  All of the damage and death triggers will be processed at the end of this method, so that
        the order or evaluation doesn't affect the calculations.  For example, if Amani Berserker is damaged in the
        attack, its attack power shouldn't go up before the damage to its attacker is calculated.

        The attack will not take place if the Character dies or is otherwise removed as a result of attacking
        (e.g. various secrets)
        """
        if not self.can_attack():
            raise GameException("That minion cannot attack")

        found_taunt = False
        targets = []
        for enemy in self.player.game.other_player.minions:
            if enemy.taunt and enemy.can_be_attacked():
                found_taunt = True
            if enemy.can_be_attacked():
                targets.append(enemy)

        if found_taunt:
            targets = [target for target in targets if target.taunt]
        else:
            targets.append(self.player.game.other_player.hero)

        self.player.trigger("attacking", self)
        target = self.choose_target(targets)
        self.trigger("attack", target)
        if isinstance(target, Minion):
            self.trigger("attack_minion", target)

        else:
            self.trigger("attack_player", target)
        target.trigger("attacked", self)
        if self.dead:
            return
        my_attack = self.attack_power + self.temp_attack  # In case the damage causes my attack to grow
        self.damage(target.attack_power + target.temp_attack, target)
        target.damage(my_attack, self)
        target.activate_delayed()

        self.activate_delayed()
        self.trigger("attack_completed")
        if self.windfury and not self.used_windfury:
            self.used_windfury = True
        else:
            self.active = False
        self.stealth = False

    def choose_target(self, targets):
        """
        Consults the associated player to select a target from a list of targets

        :param list[Character] targets: the targets to choose a target from
        """
        return self.player.choose_target(targets)

    def delayed_trigger(self, event, *args):
        """
        Set up a delayed trigger for an event.  Any events triggered with this method will not be called until
        :meth:`activate_delayed` is called.

        The purpose of this method is to allow for simeltaneous events.  For example, if a minion is attacked
        then any damage events should be triggered after the attack, and at the same time as each other.

        :param string event: The event to set up a delayed trigger for
        :param list args: The arguments to pass to the handler when it is called.
        :see: :class:`Bindable`
        """
        self.delayed.append({'event': event, 'args': args})
        self.player.game.delayed_minions.append(self)

    def activate_delayed(self):
        for delayed in self.delayed:
            self.trigger(delayed['event'], *delayed['args'])

        self.delayed = []

    def damage(self, amount, attacker):
        if self.dead:
            return
        if not self.immune:
            if type(attacker) is Minion:
                self.trigger("physically_damaged", amount, attacker)
                self.trigger("minion_damaged", amount, attacker)
            elif type(attacker) is Player:
                self.trigger("physically_damaged", amount, attacker)
                self.trigger("player_damaged", amount, attacker)
            elif issubclass(type(attacker), Card):
                self.trigger("spell_damaged", amount, attacker)
            self.delayed_trigger("damaged", amount, attacker)
            # The response of a secret to damage must happen immediately
            self.trigger("secret_damaged", amount, attacker)
            self.health -= amount
            if issubclass(type(attacker), Character):
                attacker.delayed_trigger("did_damage", amount, self)
            self.trigger("health_changed")
            if self.health <= 0:
                self.die(attacker)

    def change_attack(self, amount):
        def silence():
            self.attack_power -= amount

        self.trigger("attack_changed", amount)
        self.attack_power += amount
        self.bind_once('silenced', silence)

    def change_temp_attack(self, amount):

        self.trigger("attack_changed", amount)
        self.temp_attack += amount

    def increase_health(self, amount):
        def silence():
            self.max_health -= amount
            if self.max_health < self.health:
                self.health = self.max_health

        self.trigger("health_increased", amount)
        self.max_health += amount
        self.health += amount
        self.trigger("health_changed")
        self.bind_once('silenced', silence)

    def decrease_health(self, amount):
        def silence():
            if self.max_health == self.health:
                self.max_health += amount
                self.health += amount
            else:
                self.max_health += amount

        self.trigger("health_decreased", amount)
        self.max_health -= amount
        if self.health > self.max_health:
            self.health = self.max_health
        self.trigger("health_changed")
        self.bind_once('silenced', silence)

    def freeze(self):
        self.frozen_this_turn = True
        self.frozen = True

    def silence(self):
        self.trigger("silenced")
        self.temp_attack = 0
        self.immune = False
        self.windfury = False
        self.frozen = False
        self.frozen_this_turn = False

    def heal(self, amount, card):
        if amount < 0:
            self.damage(-amount, card)
        if amount > 0:
            self.trigger("healed", amount)
            self.health += amount
            if self.health > self.max_health:
                self.health = self.max_health
            self.trigger("health_changed")

    def die(self, by):
        self.delayed_trigger("died", by)
        self.dead = True

    def can_attack(self):
        return self.attack_power + self.temp_attack > 0 and self.active and not self.frozen

    def spell_targetable(self):
        return True


def _is_spell_targetable(target):
    return target.spell_targetable()


class Card(Bindable):
    """
    Represents a card in Heathstone.  Every card is implemented as a subclass, either directly or through
    :class:`MinionCard`, :class:`SecretCard` or :class:`WeaponCard`.  If it is a direct subclass of this
    class then it is a standard spell, whereas if it is a subclass of one of :class:`MinionCard`, :class:`SecretCard`
    or :class:`WeaponCard`., then it is a minion, secret or weapon respectively.

    In order to play a card, it should be passed to :meth:`Game.play_card`.  Simply calling :meth:`use` will
    cause its effect, but not update the game state.
    """

    def __init__(self, name, mana, character_class, rarity, target_func=None,
                 filter_func=_is_spell_targetable):
        """
            Creates a new :class:`Card`.

            ``target_func`` and ``filter_func`` have very specific behavior.  In use, the target function is called with
             the filter function as a parameter to generate the list of possible targets for the card, then ask the
             agent to choose the appropriate target.  The selected target will be available as the :attr:`target`
             attribute of :class:`Card`. As such, it is critical to call :meth:`use` in any overriding implementations.

            :param string name: The name of the card in English
            :param int mana: The base amount of mana this card costs
            :param int character_class: A constant from :class:`hsgame.constants.CHARACTER_CLASS` denoting
                                        which character this card belongs to or
                                        :const:`hsgame.constants.CHARACTER_CLASS.ALL` if neutral
            :param int rarity: A constant from :class:`hsgame.constants.CARD_RARITY` denoting the rarity of the card.
            :param function target_func: A function which takes a game, and returns a list of targets.  If None, then
                                         the card is assumed not to require a target.  If `target_func` returns
                                         an empty list, then the card cannot be played.  If it returns None, then the
                                         card is played, but with no target (i.e. a battlecry which has no valid target
                                         will not stop the minion from being played).

                                         See :mod:`hsgame.targeting` for more details.
            :param function filter_func: A boolean function which can be used to filter the list of targets. An example
                                         for :class:`hsgame.cards.spells.priest.ShadowMadness` might be a function which
                                         returns true if the target's attack is less than 3.
        """
        super().__init__()
        self.name = name
        self.mana = mana
        self.character_class = character_class
        self.rarity = rarity
        self.cancel = False
        self.targetable = target_func is not None
        if self.targetable:
            self.targets = []
            self.target = None
            self.get_targets = target_func
            self.filter_func = filter_func

    def can_use(self, player, game):
        """
        Verifies if the card can be used with the game state as it is.

        Checks that the player has enough mana to play the card, and that the card has a valid
        target if it requires one.

        :return: True if the card can be played, false otherwise.
        :rtype: bool
        """
        if self.targetable:
            self.targets = self.get_targets(game, self.filter_func)
            if self.targets is not None and len(self.targets) is 0:
                return False

        return player.mana >= self.mana_cost(player)

    def mana_cost(self, player):
        """
        Calculates the mana cost for this card.

        This cost is the base cost for the card, modified by any effects from the card itself, or
        from other cards (such as :class:`hsgame.cards.minions.neutral.VentureCoMercenary`)

        :param hsgame.game_objects.Player player: The player who is trying to use the card.

        :return: representing the actual mana cost of this card.
        :rtype: int
        """
        calc_mana = self.mana
        for mana_filter in player.mana_filters:
            if mana_filter.filter(self):
                calc_mana -= mana_filter.amount
                if calc_mana < mana_filter.min:
                    return mana_filter.min
        return calc_mana

    def use(self, player, game):
        """
        Use the card.

        This method will cause the card's effect, but will not update the game state or trigger any events.
        To play a card correctly, use :meth:`Game.play_card`.

        Implementations of new cards should override this method, but be sure to call ``super().use(player, game)``

        :param hsgame.game_objects.Player player: The player who is using the card.
        :param hsgame.game_objects.Game game: The game this card is being used in.
        """
        if self.targetable:
            if self.targets is None:
                self.target = None
            else:
                self.target = player.agent.choose_target(self.targets)

    def is_spell(self):
        """
        Verifies if this is a spell card (or a secret card)

        :return: True if the card is a spell card, false otherwise
        :rtype: bool
        """
        return True

    def __str__(self):  # pragma: no cover
        """
        Outputs a description of the card for debugging purposes.
        """
        return self.name + " (" + str(self.mana) + " mana)"


class MinionCard(Card, metaclass=abc.ABCMeta):
    def __init__(self, name, mana, character_class, rarity, targeting_func=None,
                 filter_func=lambda target: not target.stealth):
        super().__init__(name, mana, character_class, rarity, targeting_func, filter_func)

    def can_use(self, player, game):
        return super().can_use(player, game)

    def use(self, player, game):
        if len(player.minions) >= 7:
            raise GameException("Only 7 minions allowed on the field at a time")
        super().use(player, game)
        minion = self.create_minion(player)
        minion.card = self
        minion.player = player
        minion.game = game
        if minion.battlecry is not None:
            minion.battlecry(minion)
        minion.add_to_board(player.agent.choose_index(self))
        player.trigger("minion_played", minion)

    def summon(self, player, game, index):
        """
        Summons the minion associated with this card onto the board.  This is to be used when a spell
        created a minion, instead of being played from the hand.

        If the player already has 7 minions on the board, this method does nothing

        :param hsgame.game_objects.Player player: The player the summoned minion will belong to
        :param hsgame.game_objects.Game game: The game the minion is being summoned to
        :param int index: The index where the new minion will be added
        """
        if len(player.minions) < 7:
            minion = self.create_minion(player)
            minion.card = self
            minion.player = player
            minion.game = game
            minion.add_to_board(index)
            player.trigger("minion_summoned", minion)

    @abc.abstractmethod
    def create_minion(self, player):
        pass

    def is_spell(self):
        return False


class SecretCard(Card, metaclass=abc.ABCMeta):
    def __init__(self, name, mana, character_class, rarity):
        super().__init__(name, mana, character_class, rarity, None)
        self.player = None

    def can_use(self, player, game):
        return super().can_use(player, game) and self.name not in [secret.name for secret in player.secrets]

    def use(self, player, game):
        super().use(player, game)
        player.secrets.append(self)
        self.player = player

    def reveal(self):
        self.player.trigger("secret_revealed", self)
        self.player.secrets.remove(self)

    @abc.abstractmethod
    def _reveal(self, *args):
        pass

    @abc.abstractmethod
    def activate(self, player):
        pass

    @abc.abstractmethod
    def deactivate(self, player):
        pass


class Minion(Character):
    def __init__(self, attack, health, minion_type=hsgame.constants.MINION_TYPE.NONE, battlecry=None, deathrattle=None):
        super().__init__(attack, health)
        self.minion_type = minion_type
        self.taunt = False
        self.game = None
        self.card = None
        self.index = -1
        self.charge = False
        self.spell_damage = 0
        self.divine_shield = False
        self.battlecry = battlecry
        self.deathrattle = deathrattle
        self.silenced = False

    def add_to_board(self, index):
        self.player.minions.insert(index, self)
        self.player.spell_damage += self.spell_damage
        for minion in self.player.minions:
            if minion.index >= index:
                minion.index += 1
        self.index = index
        if self.charge:
            self.active = True
        self.game.trigger("minion_added", self)
        self.trigger("added_to_board", self, index)

    def remove_from_board(self):
        self.silence()  # Neutralize all possible effects
        for minion in self.player.minions:
            if minion.index > self.index:
                minion.index -= 1
        self.game.remove_minion(self, self.player)

    def attack(self):
        super().attack()

    def silence(self):
        super().silence()
        self.taunt = False
        self.stealth = False
        self.charge = False
        self.player.spell_damage -= self.spell_damage
        self.spell_damage = 0
        self.divine_shield = False
        self.battlecry = None
        self.deathrattle = None
        self.silenced = True

    def damage(self, amount, attacker):
        if self.divine_shield:
            self.divine_shield = False
        else:
            super().damage(amount, attacker)

    def heal(self, amount, card):
        super().heal(amount, card)
        if amount > 0:
            self.game.trigger("minion_healed")

    def die(self, by):
        # Since deathrattle gets removed by silence, save it
        deathrattle = self.deathrattle
        self.bind_once("died", lambda c: self.silence())
        super().die(by)
        if deathrattle is not None:
            deathrattle(self)
        self.remove_from_board()
        self.game.trigger("minion_died", self, by)

    def can_be_attacked(self):
        return not self.stealth

    def spell_targetable(self):
        return not self.stealth

    def __str__(self):  # pragma: no cover
        return "({0}) ({1}) {2} at index {3}".format(self.attack_power, self.health, self.card.name, self.index)

    def add_board_effect(self, effect, effect_silence, filter_func=lambda m: True):
        """
        Adds an effect to this minion that will affect minions on its side of the board

        This method sets up the effect so that it will update when new minions are added
        or other minions die, or the original minion is silenced

        :param function effect: the effect to apply to other minions.  Takes one paramter: the minion to affect.
        :param function effect_silence: a function which will undo the effect when this minion is silenced. Takes
                                        one parameter: the minion to affect.
        :param function filter_func: A function that selects which minions to apply this effect to. Takes
                                     one paramter: the minion to test and returns true if the minion should be
                                     affected, and false otherwise.
        """

        def minion_added(m):
            board_changed()

        def minion_died(m, by):
            board_changed()

        def board_changed():
            nonlocal affected_minions
            silenced()
            affected_minions = []
            for m in filter(filter_func, self.player.minions):
                effect(m)
                affected_minions.append(m)

        def silenced():
            for m in affected_minions:
                effect_silence(m)

        affected_minions = []
        for minion in filter(filter_func, self.player.minions):
            effect(minion)
            affected_minions.append(minion)

        self.player.game.bind("minion_added", minion_added)
        self.player.game.bind("minion_died", minion_died)
        self.bind_once("silenced", silenced)

    def copy(self, new_owner):
        new_minion = Minion(self.attack_power, self.max_health, self.minion_type, self.battlecry, self.deathrattle)
        new_minion.health = self.health
        new_minion.events = self.events.copy()
        new_minion.stealth = self.stealth
        new_minion.taunt = self.taunt
        new_minion.divine_shield = self.divine_shield
        new_minion.charge = self.charge
        new_minion.silenced = self.silenced
        new_minion.spell_damage = self.spell_damage
        if self.charge and new_owner is self.game.current_player:
            self.active = True
        card_type = type(self.card)
        new_minion.card = card_type()
        new_minion.player = new_owner
        new_minion.game = new_owner.game
        self.trigger("copied", new_minion, new_owner)
        return new_minion


class WeaponCard(Card, metaclass=abc.ABCMeta):
    """
    Represents a :class:`Card` for creating a :class:`Weapon`
    """

    def __init__(self, name, mana, character_class, rarity, target_func=None, filter_func=lambda t: not t.stealth):
        """
        Create a new :class:`WeaponCard`

        :param string name: The name of the weapon in English
        :param int mana: The base amount of mana this card costs
        :param int character_class: A constant from :class:`hsgame.constants.CHARACTER_CLASS` denoting
                                    which character this card belongs to or
                                    :const:`hsgame.constants.CHARACTER_CLASS.ALL` if neutral
        :param int rarity: A constant from :class:`hsgame.constants.CARD_RARITY` denoting the rarity of the card.
        :param function target_func: A function which takes a game, and returns a list of targets.  If None, then
                                     the weapon is assumed not to require a target for its battlecry.
                                     If `target_func` returns None, then the card is played, but with no target (i.e. a
                                     battlecry which has no valid target will not stop the weapon from being played).
                                     See :mod:`hsgame.targeting` for more details.
        :param function filter_func: A boolean function which can be used to filter the list of targets. An example
                                     for :class:`hsgame.cards.spells.priest.ShadowMadness` might be a function which
                                     returns true if the target's attack is less than 3.  Currently no weapons require
                                     anything but the default
        """
        super().__init__(name, mana, character_class, rarity, target_func, filter_func)

    def use(self, player, game):
        """
        Create a new weapon and attach it to the player's hero

        :param Player player: The player who will use this weapon
        :param Game game: The game this weapon will be used in
        """
        super().use(player, game)
        weapon = self.create_weapon(player)
        weapon.equip(player)

    @abc.abstractmethod
    def create_weapon(self, player):
        """
        Create a new weapon.  Any new weapon cards which are created must override this method.
        """
        pass

    def is_spell(self):
        return False


class Weapon(Bindable):
    """
    Represents a Hearthstone weapon.  All weapons have been attacked power and durability.  The logic for handling the
    attacks is handled by :class:`Hero`, but it can be modified through the use of events.
    """

    def __init__(self, attack_power, durability, battlecry=None):
        """
        Creates a new weapon with the given attack power and durability.  A battlecry can also optionally be set.
        :param int attack_power: The amount of attack this weapon gives the hero
        :param int durability: The number of times this weapon can be used to attack before being discarded
        :param function battlecry: Called when this weapon is first placed
        """
        super().__init__()
        # : The amount of attack this weapon gives the hero
        self.attack_power = attack_power
        # : The number of times this weapon can be used to attack before being discarded
        self.durability = durability
        #: Called when this weapon is first placed
        self.battlecry = battlecry
        #: The :class:`Player` associated with this weapon
        self.player = None
        #: The :class:`WeaponCard` that created this weapon
        self.card = None

    def destroy(self):
        self.trigger("destroyed")
        self.player.hero.weapon = None
        self.player.hero.change_temp_attack(-self.attack_power)

    def equip(self, player):
        self.player = player
        if self.player.hero.weapon is not None:
            self.player.hero.weapon.destroy()
        self.player.hero.weapon = self
        self.player.hero.change_temp_attack(self.attack_power)


class Deck:
    def __init__(self, cards, character_class):
        self.cards = cards
        self.character_class = character_class
        self.used = [False] * 30
        self.left = 30

    def can_draw(self):
        return self.left > 0

    def draw(self, random_func):
        if not self.can_draw():
            raise GameException("Cannot draw more than 30 cards")

        index = random_func(0, self.left - 1)
        count = 0
        i = 0
        while count <= index:
            if not self.used[i]:
                count += 1
            i += 1

        self.used[i - 1] = True
        self.left -= 1
        return self.cards[i - 1]

    def put_back(self, card):
        for index in range(0, 30):
            if self.cards[index] == card:
                if self.used[index] is False:
                    raise GameException("Tried to put back a card that hadn't been used yet")
                self.used[index] = False
                self.left += 1
                return
        raise GameException("Tried to put back a card that didn't come from this deck")


class Hero(Character):
    def __init__(self, character_class, player):
        super().__init__(0, 30)

        self.armour = 0
        self.weapon = None
        self.character_class = character_class
        self.player = player
        self.power = hsgame.powers.powers(self.character_class)(self)
        self.weapon = None

    def attack(self):
        super().attack()
        if self.weapon is not None:
            self.weapon.durability -= 1
            if self.weapon.durability is 0:
                self.weapon.destroy()

    def damage(self, amount, attacker):
        self.armour -= amount
        if self.armour < 0:
            new_amount = -self.armour
            self.armour = 0
            super().damage(new_amount, attacker)

    def increase_armour(self, amount):
        self.trigger("armour_increased", amount)
        self.armour += amount

    def die(self, by):
        super().die(by)

    def find_power_target(self):
        targets = hsgame.targeting.find_spell_target(self.player.game, lambda t: t.spell_targetable())
        target = self.choose_target(targets)
        self.trigger("found_power_target", target)
        return target


class Player(Bindable):
    def __init__(self, name, deck, agent, game, random_func=random.randint):
        super().__init__()
        self.hero = Hero(deck.character_class, self)
        self.name = name
        self.mana = 0
        self.max_mana = 0
        self.deck = deck
        self.spell_damage = 0
        self.minions = []
        self.random = random_func
        self.hand = []
        self.fatigue = 0
        self.agent = agent
        self.game = game
        self.secrets = []
        self.spell_multiplier = 1
        self.heal_multiplier = 1
        self.heal_does_damage = False
        self.mana_filters = []
        self.overload = 0

    def __str__(self):  # pragma: no cover
        return "Player: " + self.name

    def draw(self):
        if self.can_draw():
            card = self.deck.draw(self.random)
            self.trigger("card_drawn", card)
            if len(self.hand) < 10:
                self.hand.append(card)
            else:
                self.trigger("card_destroyed", card)
        else:
            self.fatigue += 1
            self.hero.trigger("fatigue_damage", self.fatigue)
            self.hero.damage(self.fatigue, None)
            self.hero.activate_delayed()

    def can_draw(self):
        return self.deck.can_draw()

    def effective_spell_damage(self, base_damage):
        return (base_damage + self.spell_damage) * self.spell_multiplier

    def effective_heal_power(self, base_heal):
        if self.heal_does_damage:
            return (base_heal + self.spell_damage) * self.spell_multiplier
        else:
            return base_heal * self.heal_multiplier

    def put_back(self, card):
        self.hand.remove(card)
        self.deck.put_back(card)
        self.trigger("card_put_back", card)

    def discard(self):
        targets = self.hand
        target = targets[self.random(0, len(targets) - 1)]
        self.hand.remove(target)
        self.trigger("card_discarded", target)

    def choose_target(self, targets):
        return self.agent.choose_target(targets)


class Game(Bindable):
    def __init__(self, decks, agents, random_func=random.randint):
        super().__init__()
        self.delayed_minions = []
        self.random = random_func
        first_player = random_func(0, 1)
        if first_player is 0:
            play_order = [0, 1]
        else:
            play_order = [1, 0]
        self.players = [Player("one", decks[play_order[0]], agents[play_order[0]], self, random_func),
                        Player("two", decks[play_order[1]], agents[play_order[1]], self, random_func)]
        agents[0].set_game(self)
        agents[1].set_game(self)
        self.current_player = self.players[0]
        self.other_player = self.players[1]
        self.game_ended = False
        for i in range(0, 3):
            self.players[0].draw()

        for i in range(0, 4):
            self.players[1].draw()

        self.players[0].hero.bind("died", self.game_over)
        self.players[1].hero.bind("died", self.game_over)

    def pre_game(self):
        card_keep_index = self.players[0].agent.do_card_check(self.players[0].hand)
        self.trigger("kept_cards", self.players[0].hand, card_keep_index)
        put_back_cards = []
        for card_index in range(0, 3):
            if not card_keep_index[card_index]:
                self.players[0].draw()
                put_back_cards.append(self.players[0].hand[card_index])

        for card in put_back_cards:
            self.players[0].put_back(card)

        card_keep_index = self.players[1].agent.do_card_check(self.players[1].hand)
        self.trigger("kept_cards", self.players[1].hand, card_keep_index)
        put_back_cards = []
        for card_index in range(0, 4):
            if not card_keep_index[card_index]:
                self.players[1].draw()
                put_back_cards.append(self.players[1].hand[card_index])

        for card in put_back_cards:
            self.players[1].put_back(card)

    def start(self):
        self.pre_game()
        self.current_player = self.players[1]
        while not self.game_ended:
            self.play_single_turn()

    def play_single_turn(self):
        self._start_turn()
        self.current_player.agent.do_turn(self.current_player)
        self._end_turn()

    def _start_turn(self):
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
            self.other_player = self.players[0]
        else:
            self.current_player = self.players[0]
            self.other_player = self.players[1]
        if self.current_player.max_mana < 10:
            self.current_player.max_mana += 1

        for secret in self.other_player.secrets:
            secret.activate(self.other_player)
        self.current_player.mana = self.current_player.max_mana - self.current_player.overload
        self.current_player.overload = 0
        self.current_player.trigger("turn_started")
        if self.current_player.hero.weapon is not None:
            self.current_player.hero.change_temp_attack(self.current_player.hero.weapon.attack_power)
        self.current_player.draw()

    def game_over(self, attacker):
        self.game_ended = True

    def _end_turn(self):
        self.current_player.trigger("turn_ended")
        self.current_player.hero._turn_complete()
        self.other_player.hero._turn_complete()

        if self.current_player.hero.frozen_this_turn:
            self.current_player.hero.frozen_this_turn = False
        else:
            self.current_player.hero.frozen = False

        self.other_player.hero.frozen_this_turn = False
        for minion in self.other_player.minions:
            minion.frozen_this_turn = False
            minion._turn_complete()

        self.current_player.hero.active = True
        for minion in self.current_player.minions:
            minion.active = True
            minion.used_wind_fury = False
            if minion.frozen_this_turn:
                minion.frozen_this_turn = False
            else:
                minion.frozen = False
                minion._turn_complete()

        for secret in self.other_player.secrets:
            secret.deactivate(self.other_player)

    def play_card(self, card):
        if self.game_ended:
            raise GameException("The game has ended")
        if not card.can_use(self.current_player, self):
            raise GameException("That card cannot be used")
        self.current_player.trigger("card_played", card)
        self.current_player.hand.remove(card)
        if card.can_use(self.current_player, self):
            self.current_player.mana -= card.mana_cost(self.current_player)
        else:
            raise GameException("Tried to play card that could not be played")

        if card.is_spell():
            self.current_player.trigger("spell_cast", card)

        if not card.cancel:
            card.use(self.current_player, self)
            self.current_player.trigger("card_used", card)
            for minion in self.delayed_minions:
                minion.activate_delayed()

            self.delayed_minions = []

    def remove_minion(self, minion, player):
        player.minions.remove(minion)
        self.trigger("minion_removed", minion, player)
