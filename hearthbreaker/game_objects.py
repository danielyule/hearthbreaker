import copy
import random
import abc

import hearthbreaker.powers
import hearthbreaker.targeting
import hearthbreaker.constants

card_table = {}


def card_lookup(card_name):
    """
    Given a the name of a card as a string, return an object corresponding to that card

    :param str card_name: A string representing the name of the card in English
    :return: An instance of a subclass of Card corresponding to the given card name or None if no Card
             by that name exists.
    :rtype: hearthbreaker.game_objects.Card
    """

    def card_lookup_rec(card_type):
        subclasses = card_type.__subclasses__()
        if len(subclasses) is 0:
            c = card_type()
            card_table[c.name] = card_type
        for sub_type in subclasses:
            card_lookup_rec(sub_type)

    if len(card_table) == 0:
        for card_class in Card.__subclasses__():
            card_lookup_rec(card_class)

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

    def bind(self, event, function):
        """
        Bind a function to an event.  Each time the event is triggered, the function will be called.

        :param string event: The event to bind a function to
        :param function function: The function to bind.  The parameters are not checked until it is called, so
                                  ensure its signature matches the parameters called from :meth:`trigger`
        :see: :class:`Bindable`
        """

        class Handler:
            def __init__(self):
                self.function = function
                self.remove = False
                self.active = False

        if event not in self.events:
            self.events[event] = []

        self.events[event].append(Handler())

    def bind_once(self, event, function):
        """
        Bind a function to an event.  This function will only be called the next time the event is triggered, and
        then ignored.

        :param string event: The event to bind a function to
        :param function function: The function to bind.  The parameters are not checked until it is called, so
                                  ensure its signature matches the parameters called from :meth:`trigger`
        :see: :class:`Bindable`
        """

        class Handler:
            def __init__(self):
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
        :param list args: The arguments to pass to the bound function
        :see: :class:`Bindable`
        """
        if event in self.events:
            for handler in copy.copy(self.events[event]):
                if not handler.active and handler in self.events[event]:
                    handler.active = True
                    handler.function(*args)
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


class Effect (metaclass=abc.ABCMeta):

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

    @abc.abstractmethod
    def __str__(self):
        pass

    # @abc.abstractmethod
    def __to_json__(self):
        pass


class Character(Bindable, metaclass=abc.ABCMeta):
    """
    A Character in Hearthstone is something that can attack, i.e. a :class:`Hero` or :class:`Minion`.

     This common superclass handles all of the status effects and calculations involved in attacking or being attacked.
    """

    def __init__(self, attack_power, health, stealth=False, windfury=False):
        """
        Create a new Character with the given attack power and health

        :param int attack_power: the amount of attack this character has at creation
        :param int health: the maximum health of this character
        :param boolean stealth: (optional) True if this character has stealth, false otherwise.  Default: false
        :param boolean windfury: (optional) True if this character has windfury, false otherwise.  Default: false
        """
        super().__init__()

        # : The current health of this character
        self.health = health
        # : The maximum health of this character
        self.base_health = health
        #: The amount of attack this character has
        self.base_attack = attack_power
        #: Whether or not this character can attack this turn
        self.active = False
        #: Whether or not this character has died
        self.dead = False
        #: If this character has windfury
        self.windfury = windfury
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
        self.stealth = stealth
        #: If this character is enraged
        self.enraged = False
        #: If this character has been removed from the board
        self.removed = False
        #: A list of effects that have been applied to this character
        self.effects = []
        #: An integer describing when this character was created.  The lower, the earlier it was created
        self.born = -1

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

        self.player.trigger("pre_attack", self)
        target = self.choose_target(targets)
        self.player.trigger("attack", self, target)
        self.trigger("attack", target)
        target.trigger("attacked", self)
        if self.removed or self.dead:  # removed won't be set yet if the Character died during this attack
            return
        my_attack = self.calculate_attack()  # In case the damage causes my attack to grow
        self.damage(target.calculate_attack(), target)
        target.damage(my_attack, self)
        self.player.game.check_delayed()
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

    def calculate_attack(self):
        """
        Calculates the amount of attack this :class:`Character` has, including the base attack, any temporary attack
        bonuses for this turn
        """

        return self.base_attack + self.temp_attack

    def calculate_max_health(self):
        """
        Calculates the maximum amount of health this :class:`Character` has, including the base health, and any aura
        effects
        """
        return self.base_health

    def delayed_trigger(self, event, *args):
        """
        Set up a delayed trigger for an event.  Any events triggered with this method will not be called until
        :meth:`activate_delayed` is called.

        The purpose of this method is to allow for simultaneous events.  For example, if a minion is attacked
        then any damage events should be triggered after the attack, and at the same time as each other.

        :param string event: The event to set up a delayed trigger for
        :param list args: The arguments to pass to the handler when it is called.
        :see: :class:`Bindable`
        """
        self.delayed.append({'event': event, 'args': args})
        self.player.game.delayed_minions.add(self)

    def activate_delayed(self):
        """
        Activate any events that were delayed.

        :see: :meth:`delayed_trigger`
        """
        for delayed in self.delayed:
            self.trigger(delayed['event'], *delayed['args'])

        self.delayed = []

    def damage(self, amount, attacker):
        """
        Deal damage to this :class:`Character`.  This method uses the ``attacker`` parameter to determine the nature
        of the damage taken.  If the attacker is a :class:`Character`, then it is assumed to be a physical attack.
        If attacker is a :class:`SpellCard`, then it assumes a spell attack.  If ``None``, then something else
        (hero ability or battlecry).  This method will also trigger the various events associated with taking damage
        or dying.

        If the character has a divine shield, it will be removed, and the character will take no damage.  If the
        character's health is below the max_health, then the character is considered enraged.

        :param int amount: The amount of damage done (should be positive)
        :param Object attacker: The :class:`Character`or :class:`SpellCard that did the damage or ``None``.
        """
        if self.dead:
            return
        if not self.immune:
            if type(attacker) is Minion:
                self.trigger("physically_damaged", amount, attacker)
                self.trigger("damaged_by_minion", amount, attacker)
            elif type(attacker) is Player:
                self.trigger("physically_damaged", amount, attacker)
                self.trigger("damaged_by_player", amount, attacker)
            elif issubclass(type(attacker), Card):
                self.trigger("damaged_by_spell", amount, attacker)
            self.delayed_trigger("damaged", amount, attacker)
            if isinstance(self, Minion):
                self.player.trigger("minion_damaged", self, attacker)
            elif isinstance(self, Hero):
                # The response of a secret to damage must happen immediately
                self.trigger("hero_damaged", amount, attacker)
            self.health -= amount
            if issubclass(type(attacker), Character):
                attacker.trigger("did_damage", self, amount)
            self.trigger("health_changed")
            if not self.enraged and self.health != self.calculate_max_health():
                self.enraged = True
                self.trigger("enraged")
            if self.health <= 0:
                self.die(attacker)

    def change_attack(self, amount):
        """
        Change the amount of attack this :class:`Character` has.  The amount can be either positive or negative.
        This method will automatically undo its effect when silenced, and re-apply its effect when copied

        :param int amount: The amount to change the attack by
        """
        def apply_silence(minion, player=None):
            def silence():
                minion.base_attack -= amount
            minion.bind_once('silenced', silence)
            minion.bind("copied", apply_silence)

        self.trigger("attack_changed", amount)
        self.base_attack += amount
        apply_silence(self)

    def change_temp_attack(self, amount):
        """
        Change the amount of attack this :class:`Character` has on this turn only.  The amount can be either positive
        or negative. This method will automatically undo its effect when silenced, and re-apply its effect when copied

        :param int amount: The amount to change the temporary attack by
        """
        self.trigger("attack_changed", amount)
        self.temp_attack += amount

    def increase_health(self, amount):
        """
        Increase the amount of  total health this :class:`Character` has.  This is a permanent effect (unless the
        Character is silenced).  This effect will increase both the player's current health and maximum health

        :param int amount: the amount to increase health by
        """
        def apply_silence(minion, player=None):
            def silence():
                minion.base_health -= amount
                if minion.calculate_max_health() < minion.health:
                    minion.health = minion.calculate_max_health()
            minion.bind_once('silenced', silence)
            minion.bind("copied", apply_silence)
        self.trigger("health_increased", amount)
        self.base_health += amount
        self.health += amount
        self.trigger("health_changed")
        apply_silence(self)

    def decrease_health(self, amount):
        """
        Decrease the amount of  total health this :class:`Character` has.  This is a permanent effect (unless the
        Character is silenced).  This effect will decrease the player's maximum health, but will only decrease
        the player's health if it is above the new value for maximum health

        :param int amount: the amount to decrease health by
        """
        def apply_silence(minion, player=None):
            def silence():
                if minion.calculate_max_health() == minion.health:
                    minion.base_health += amount
                    minion.health += amount
                else:
                    minion.base_health += amount
            minion.bind_once('silenced', silence)
            minion.bind("copied", apply_silence)

        self.trigger("health_decreased", amount)
        self.base_health -= amount
        if self.health > self.calculate_max_health():
            self.health = self.calculate_max_health()

        if self.enraged and self.health == self.calculate_max_health():
            self.enraged = False
            self.trigger("unenraged")
        self.trigger("health_changed")
        apply_silence(self)

    def freeze(self):
        """
        Causes this :class:`Character` to be frozen.  If this character is frozen on its opponent's turn, it
        will not be able to attack on the next turn.  If frozen on its owner's turn, it will not be able
        to attack this turn or its owner's next turn.
        """
        self.frozen_this_turn = True
        self.frozen = True

    def heal(self, amount, source):
        """
        Heals the :class:`Character`.  The health cannot exceed the character's max health.  If the amount
        being healed is less than 0, then the character is damaged instead.

        If the character's health is brought back to its maximum, then it is no longer enraged.

        :param int amount: The amount this character is being healed by.  Can be negative
        :param source: The source of this healing.  Could be a :class:`Minion`, a :class:`spell card <Card>` or None
        """
        if amount < 0:
            self.damage(-amount, source)
        if amount > 0:
            self.trigger("healed", amount)
            self.health += amount
            if self.health > self.calculate_max_health():
                self.health = self.calculate_max_health()
            if self.enraged and self.health == self.calculate_max_health():
                self.enraged = False
                self.trigger("unenraged")
            self.trigger("health_changed")

    def die(self, by):
        """
        Kills this :class:`Character`.  The death event will not be processed until :meth:`activate_delayed` is called.

        :param by: The object that killed this character.  Could be a :class:`Character`, a :class:`spell card <Card>`
                   or None
        """
        self.delayed_trigger("died", by)
        self.dead = True

    def can_attack(self):
        """
        Checks if this :class:`Character` can attack.  Evaluates whether or not is has already attacked, if its frozen
        and if it has an attack value

        :rtype boolean:
        """
        return self.calculate_attack() > 0 and self.active and not self.frozen

    def spell_targetable(self):
        """
        Checks if a :class:`Character` can be targeted by a spell.  Minions with stealth or whose text say they can't be
        targeted by spells cannot be targeted, but any other character can.
        """
        return True

    def add_effect(self, effect):
        """
        Applies the the given effect to the :class:`Character`.  The effect will be unapplied in the case of silence,
        and will be applied to any copies that are made.

        :param Effect effect: The effect to apply to this :class:`Character
        """
        if type(effect) not in self.player.effect_count:
            self.player.effect_count[type(effect)] = 0

        self.player.effect_count[type(effect)] += 1
        effect.set_target(self)
        effect.apply()
        self.effects.append(effect)


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
                 filter_func=_is_spell_targetable, overload=0):
        """
            Creates a new :class:`Card`.

            ``target_func`` and ``filter_func`` have very specific behavior.  In use, the target function is called with
             the filter function as a parameter to generate the list of possible targets for the card, then ask the
             agent to choose the appropriate target.  The selected target will be available as the :attr:`target`
             attribute of :class:`Card`. As such, it is critical to call :meth:`use` in any overriding implementations.

            :param string name: The name of the card in English
            :param int mana: The base amount of mana this card costs
            :param int character_class: A constant from :class:`hearthbreaker.constants.CHARACTER_CLASS` denoting
                                        which character this card belongs to or
                                        :const:`hearthbreaker.constants.CHARACTER_CLASS.ALL` if neutral
            :param int rarity: A constant from :class:`hearthbreaker.constants.CARD_RARITY` denoting the rarity of the
                               card.
            :param function target_func: A function which takes a game, and returns a list of targets.  If None, then
                                         the card is assumed not to require a target.  If `target_func` returns
                                         an empty list, then the card cannot be played.  If it returns None, then the
                                         card is played, but with no target (i.e. a battlecry which has no valid target
                                         will not stop the minion from being played).

                                         See :mod:`hearthbreaker.targeting` for more details.
            :param function filter_func: A boolean function which can be used to filter the list of targets. An example
                                         for :class:`hearthbreaker.cards.spells.priest.ShadowMadness` might be a
                                         function which returns true if the target's attack is less than 3.
            :param int overload: The amount of overload on the card
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
        self.overload = overload

    def can_use(self, player, game):
        """
        Verifies if the card can be used with the game state as it is.

        Checks that the player has enough mana to play the card, and that the card has a valid
        target if it requires one.

        :return: True if the card can be played, false otherwise.
        :rtype: bool
        """
        if game.game_ended:
            return False
        if self.targetable:
            self.targets = self.get_targets(game, self.filter_func)
            if self.targets is not None and len(self.targets) is 0:
                return False

        return player.mana >= self.mana_cost(player)

    def mana_cost(self, player):
        """
        Calculates the mana cost for this card.

        This cost is the base cost for the card, modified by any effects from the card itself, or
        from other cards (such as :class:`hearthbreaker.cards.minions.neutral.VentureCoMercenary`)

        :param hearthbreaker.game_objects.Player player: The player who is trying to use the card.

        :return: representing the actual mana cost of this card.
        :rtype: int
        """
        calc_mana = self.mana
        for mana_filter in player.mana_filters:
            if mana_filter.filter(self):
                temp_mana = calc_mana
                calc_mana -= mana_filter.amount
                if temp_mana < mana_filter.min:  # Extra logic to handle 0 cost creatures with Summoning portal
                    return temp_mana
                if calc_mana < mana_filter.min:
                    return mana_filter.min
        return calc_mana

    def use(self, player, game):
        """
        Use the card.

        This method will cause the card's effect, but will not update the game state or trigger any events.
        To play a card correctly, use :meth:`Game.play_card`.

        Implementations of new cards should override this method, but be sure to call ``super().use(player, game)``

        :param hearthbreaker.game_objects.Player player: The player who is using the card.
        :param hearthbreaker.game_objects.Game game: The game this card is being used in.
        """
        player.overload += self.overload
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
    """
    Describes a :class:`Card` for summoning a minion.  This is distinct from the :class:`Minion` that represents the
    minion after it has been played.  This class represents the card aspects (mana cost, character class and rarity)
    as well as being responsible for creating the minion that will be added to the table.

    :see: :class:`Card`
    :see: :meth:`create_minion`
    """
    def __init__(self, name, mana, character_class, rarity, minion_type=hearthbreaker.constants.MINION_TYPE.NONE,
                 targeting_func=None, filter_func=lambda target: not target.stealth, overload=0):
        """
        All parameters are passed directly to the :meth:`superclass's __init__ method <Card.__init__>`.

        :param string name: The name of this card in English
        :param int mana: The base mana cost of this card
        :param int character_class: The character class that this card belongs to.  Should be a member of
                                    :class:`hearthbreaker.constants.CHARACTER_CLASS`
        :param int rarity: How rare the card is.  Should be a member of :class:`hearthbreaker.constants.CARD_RARITY`
        :param int minion_type: The type that the summoned minion will have.  Should be a member of
                                :class:`hearthbreaker.constants.MINION_TYPE`
        :param function targeting_func: The function used to select a list of targets for this minion's battlecry, if it
                                        has one.  If it does not, then None.  This function should be taken from
                                        :mod:`hearthbreaker.targeting`, and should return `None` if there are no
                                        feasible targets.
        :param function filter_func: Used to filter targets returned from the targeting function for appropriateness.
                                     Typically used for ensuring that stealthed minions aren't targeted
        """
        super().__init__(name, mana, character_class, rarity, targeting_func, filter_func, overload)
        self.minion_type = minion_type

    def can_use(self, player, game):
        """
        Checks if this minion can be played.  The card must be able to play AND the board must not be full.

        :param hearthbreaker.game_objects.Player player: The player who wants to play this card
        :param hearthbreaker.game_objects.Game game: The game this card might be played in.
        """
        return len(player.minions) < 7 and super().can_use(player, game)

    def use(self, player, game):
        """
        Adds this minion to the board for the given player, if the card is able to be played.  The agent for the
        given player will be consulted about the location on the board of the played minion, about the target
        for the battlecry if necessary, and to choose an option for cards with choose.

        This method operates in the following order:

         1. Battlecry target chosen (if needed)
         2. Board placement chosen
         3. Minion is placed on the board
         4. minion_placed event
         5. Battlecry activated (if needed)
         6. minion_played event
         7. minion_summoned_event
         8. after_minion_added event

        The precise ordering of events is necessary so that various effects (Sword of Justice, Knife Juggler, etc)
        trigger in the correct order, and to distinguish from :meth:`summon`, which is called when a minion is
        played as a side effect of of card (e.g. Feral Spirit)

        :param hearthbreaker.game_objects.Player player: The player who wants to play this card
        :param hearthbreaker.game_objects.Game game: The game this card will be played in.
        """
        if len(player.minions) >= 7:
            raise GameException("Only 7 minions allowed on the field at a time")
        super().use(player, game)
        minion = self.create_minion(player)
        minion.card = self
        minion.player = player
        minion.game = game
        minion.index = player.agent.choose_index(self, player)
        minion.add_to_board(minion.index)
        player.trigger("minion_placed", minion)
        if minion.battlecry is not None:
            minion.battlecry(minion)
        player.trigger("minion_played", minion)
        player.trigger("minion_summoned", minion)
        player.trigger("after_minion_added", minion)

    def summon(self, player, game, index):
        """
        Summons the minion associated with this card onto the board.  This is to be used when a spell
        created a minion, instead of being played from the hand.

        If the player already has 7 minions on the board, this method does nothing.

        This method operates in the following order:

         1. Minion is placed on the board
         2. minion_placed event
         3. minion_summoned_event
         4. after_minion_added event

        The ordering is important so that efects trigger in the correct order.

        :see: :meth:`use`

        :param hearthbreaker.game_objects.Player player: The player the summoned minion will belong to
        :param hearthbreaker.game_objects.Player player: The player the summoned minion will belong to
        :param hearthbreaker.game_objects.Game game: The game the minion is being summoned to
        :param int index: The index where the new minion will be added
        """
        if len(player.minions) < 7:
            minion = self.create_minion(player)
            minion.card = self
            minion.player = player
            minion.game = game
            minion.index = index
            minion.add_to_board(index)
            player.trigger("minion_placed", minion)
            player.trigger("minion_summoned", minion)
            player.trigger("after_minion_added", minion)

    @abc.abstractmethod
    def create_minion(self, player):
        """
        Creates the minion associated with this card.  This method is responsible for creating the :class:`Minion`
        object and adding any necessary effects.  This method must be overridden by a subclass's implementation.  For
        more details, see :doc:`contributing`.

        This method is only responsible for creating the minion and attaching events.  It is not responsible for setting
        the minion's player or game attributes, or correctly setting its index.  That is handled within :meth:`play`
        and :meth:`summon`

        :param hearthbreaker.game_objects.Player player: The player who the newly created minion will belong to.

        :rtype: hearthbreaker.game_objects.Minion
        """
        pass

    def is_spell(self):
        """
        Checks if this card is a spell card.  Always returns false

        :rtype: boolean
        """
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
        self.deactivate(self.player)

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
    def __init__(self, attack, health, battlecry=None,
                 deathrattle=None, taunt=False, charge=False, spell_damage=0, divine_shield=False, stealth=False,
                 windfury=False, spell_targetable=True, effects=None):
        super().__init__(attack, health, windfury=windfury, stealth=stealth)
        self.taunt = taunt
        self.game = None
        self.card = None
        self.index = -1
        self.charge = charge
        self.spell_damage = spell_damage
        self.divine_shield = divine_shield
        self.can_be_targeted_by_spells = spell_targetable
        self.battlecry = battlecry
        self.deathrattle = deathrattle
        self.base_deathrattle = deathrattle
        self.exhausted = True
        self.removed = False
        if effects:
            self._effects_to_add = effects
        else:
            self._effects_to_add = []
        self.bind("did_damage", self.__on_did_damage)

    def __on_did_damage(self, amount, target):
        self.stealth = False

    def add_to_board(self, index):
        self.game.minion_counter += 1
        self.player.minions.insert(index, self)
        self.born = self.game.minion_counter
        self.player.spell_damage += self.spell_damage
        count = 0
        for minion in self.player.minions:
            minion.index = count
            count += 1
        self.index = index
        self.active = True
        self.health += self.calculate_max_health() - self.base_health
        for effect in self._effects_to_add:
            self.add_effect(effect)
        self.trigger("added_to_board", self, index)

    def calculate_attack(self):
        """
        Calculates the amount of attack this :class:`Minion` has, including the base attack, any temporary attack
        bonuses for this turn and any aura effects
        """
        aura_attack = 0
        for aura in self.player.auras:
            if aura.filter(self):
                aura_attack += aura.attack
        return super().calculate_attack() + aura_attack

    def calculate_max_health(self):
        """
        Calculates the maximum amount of health this :class:`Character` has, including the base health, and any aura
        effects
        """
        aura_health = 0
        for aura in self.player.auras:
            if aura.filter(self):
                aura_health += aura.health
        return self.base_health + aura_health

    def remove_from_board(self):
        for minion in self.player.minions:
            if minion.index > self.index:
                minion.index -= 1
        self.game.remove_minion(self, self.player)
        self.removed = True

    def replace(self, new_minion):
        """
        Replaces this minion with another one

        :param hearthbreaker.game_objects.Minion new_minion: The minion to replace this minion with
        """
        self.silence()
        new_minion.index = self.index
        new_minion.player = self.player
        new_minion.game = self.game
        self.removed = True
        self.game.minion_counter += 1
        new_minion.born = self.game.minion_counter
        self.player.minions[self.index] = new_minion
        for effect in new_minion._effects_to_add:
            new_minion.add_effect(effect)
        new_minion.health += new_minion.calculate_max_health() - new_minion.base_health

    def attack(self):
        super().attack()

    def silence(self):
        """
        Silence this :class:`Character`.  This will trigger the silence event, and undo any status effects that have
        affected this character (immune, attack & health increases, frozen, windfury)
        """
        self.temp_attack = 0
        self.immune = False
        self.windfury = False
        self.frozen = False
        self.frozen_this_turn = False
        for effect in reversed(self.effects):
            self.player.effect_count[type(effect)] -= 1
            effect.unapply()
        self.effects = []
        self.taunt = False
        self.stealth = False
        self.charge = False
        self.player.spell_damage -= self.spell_damage
        self.spell_damage = 0
        self.divine_shield = False
        self.battlecry = None
        self.deathrattle = None
        self.can_be_targeted_by_spells = True
        self.trigger("silenced")
        if "copied" in self.events:
            del self.events["copied"]

    def damage(self, amount, attacker):
        if self.divine_shield:
            self.divine_shield = False
        else:
            super().damage(amount, attacker)

    def heal(self, amount, source):
        super().heal(amount, source)
        if amount > 0:
            self.game.trigger("minion_healed")

    def die(self, by):
        # Since deathrattle gets removed by silence, save it
        if not self.dead and not self.removed:
            deathrattle = self.deathrattle

            def delayed_death(c):
                self.player.trigger("minion_died", self, by)
                self.silence()
                if deathrattle is not None:
                    deathrattle(self)
                self.player.graveyard.add(self.card.name)
            self.bind_once("died", delayed_death)
            super().die(by)
            self.player.dead_this_turn.append(self)
            self.remove_from_board()

    def can_attack(self):
        return (self.charge or not self.exhausted) and super().can_attack()

    def can_be_attacked(self):
        return not self.stealth

    def spell_targetable(self):
        return not self.stealth and self.can_be_targeted_by_spells

    def __str__(self):  # pragma: no cover
        return "({0}) ({1}) {2} at index {3}".format(self.calculate_attack(), self.health, self.card.name, self.index)

    def add_aura(self, attack, health, affected_players, filter_func=lambda m: True):
        """
        Adds an aura effect to some minions on the board minions.  This aura can increase the attack or health of
        the minions, or both.  The effect can be limited to only certain minions with the use of a filter
        function, and by specifying which player(s) the aura affects.

        This aura is automatically unapplied in case of silence, and applied to any copies of this minion

        :param int attack: The amount to increase minions' attack by
        :param int health: The amount to increase minion's health AND max health by
        :param list[hearthbreaker.game_objects.Player] affected_players: A list of players whose minions should be
                                                                         affected by this aura
        :param function filter_func: A function that selects which minions to apply this effect to. Takes
                                     one paramter: the minion to test and returns true if the minion should be
                                     affected, and false otherwise.
        """

        complete_filter_func = lambda m: m is not self and filter_func(m)

        class Aura:
            def __init__(self):
                self.attack = attack
                self.health = health
                self.filter = complete_filter_func
        aura = Aura()
        for player in affected_players:
            player.auras.append(aura)
            if health > 0:
                for minion in filter(complete_filter_func, player.minions):
                    minion.health += health
                    minion.trigger("health_changed")

        def silenced():
            for player in affected_players:
                player.auras.remove(aura)
                if health > 0:
                    for filtered_minion in filter(complete_filter_func, player.minions):
                        if filtered_minion.health > filtered_minion.calculate_max_health():
                            filtered_minion.health = filtered_minion.calculate_max_health()
                            filtered_minion.trigger("health_changed")

        self.bind_once("silenced", silenced)

    def add_adjacency_aura(self, attack, health, player):
        """
        Adds an aura to this minion that only affects adjacent minions.  This aura can affect the attack or health of
        adjacent minions or both.

        This aura is automatically unapplied in case of silence, and applied to any copied minions.

        :param int attack: The amount to increase the attack power of the adjacent minions
        :param int health: The amount to increase the health of the adjacent minions
        :param hearthbreaker.game_objects.Player player: The player who the adjacent minions belong to.
        """
        me = self

        class Aura:
            def __init__(self):
                self.attack = attack
                self.health = health
                self.filter = lambda mini: mini.index is me.index - 1 or mini.index is me.index + 1
        aura = Aura()
        player.auras.append(aura)
        if health > 0:
            for minion in filter(aura.filter, player.minions):
                minion.health += health
                minion.trigger("health_changed")

        def silenced():
            player.auras.remove(aura)
            if health > 0:
                for filtered_minion in filter(aura.filter, player.minions):
                    if filtered_minion.health > filtered_minion.calculate_max_health():
                        filtered_minion.health = filtered_minion.calculate_max_health()
                        filtered_minion.trigger("health_changed")

        def copied(new_minion, new_owner):
            new_minion.add_adjacency_aura(attack, health, new_owner)

        self.bind_once("silenced", silenced)
        self.bind("copied", copied)

    def copy(self, new_owner, new_game=None):
        new_minion = Minion(self.base_attack, self.base_health, self.battlecry, self.base_deathrattle)
        new_minion.health = self.health
        new_minion.events = dict()
        new_minion.bind("did_damage", self.__on_did_damage)
        new_minion.stealth = self.stealth
        new_minion.taunt = self.taunt
        new_minion.divine_shield = self.divine_shield
        new_minion.charge = self.charge
        new_minion.can_be_targeted_by_spells = self.can_be_targeted_by_spells
        new_minion.spell_damage = self.spell_damage
        new_minion.temp_attack = self.temp_attack
        new_minion.immune = self.immune
        new_minion.index = self.index
        new_minion.active = self.active
        new_minion.exhausted = self.exhausted
        new_minion.born = self.born
        card_type = type(self.card)
        new_minion.card = card_type()
        new_minion.player = new_owner
        if new_game:
            new_minion.game = new_game
        else:
            new_minion.game = new_owner.game
        new_minion.effects = []
        new_minion._effects_to_add = [copy.copy(effect) for effect in self.effects]
        self.trigger("copied", new_minion, new_owner)
        return new_minion

    def bounce(self):
        if len(self.player.hand) < 10:
            self.silence()
            self.remove_from_board()
            self.player.hand.append(self.card)
        else:
            self.die(None)
            self.game.check_delayed()


class WeaponCard(Card, metaclass=abc.ABCMeta):
    """
    Represents a :class:`Card` for creating a :class:`Weapon`
    """

    def __init__(self, name, mana, character_class, rarity, target_func=None, filter_func=lambda t: not t.stealth,
                 overload=0):
        """
        Create a new :class:`WeaponCard`

        :param string name: The name of the weapon in English
        :param int mana: The base amount of mana this card costs
        :param int character_class: A constant from :class:`hearthbreaker.constants.CHARACTER_CLASS` denoting
                                    which character this card belongs to or
                                    :const:`hearthbreaker.constants.CHARACTER_CLASS.ALL` if neutral
        :param int rarity: A constant from :class:`hearthbreaker.constants.CARD_RARITY` denoting the rarity of the card.
        :param function target_func: A function which takes a game, and returns a list of targets.  If None, then
                                     the weapon is assumed not to require a target for its battlecry.
                                     If `target_func` returns None, then the card is played, but with no target (i.e. a
                                     battlecry which has no valid target will not stop the weapon from being played).
                                     See :mod:`hearthbreaker.targeting` for more details.
        :param function filter_func: A boolean function which can be used to filter the list of targets. An example
                                     for :class:`hearthbreaker.cards.spells.priest.ShadowMadness` might be a function
                                     which returns true if the target's attack is less than 3.  Currently no weapons
                                     require anything but the default
        :param int overload: The amount of overload on the card
        """
        super().__init__(name, mana, character_class, rarity, target_func, filter_func, overload)

    def use(self, player, game):
        """
        Create a new weapon and attach it to the player's hero

        :param Player player: The player who will use this weapon
        :param Game game: The game this weapon will be used in
        """
        super().use(player, game)
        weapon = self.create_weapon(player)
        weapon.card = self
        weapon.player = player
        weapon.game = game
        if weapon.battlecry is not None:
            weapon.battlecry(weapon)
        weapon.equip(player)

    @abc.abstractmethod
    def create_weapon(self, player):
        """
        Create a new weapon.  Any new weapon cards which are created must override this method.
        """
        pass

    def is_spell(self):
        return False


class TheCoin(Card):
    def __init__(self):
        super().__init__("The Coin", 0, hearthbreaker.constants.CHARACTER_CLASS.ALL,
                         hearthbreaker.constants.CARD_RARITY.SPECIAL)

    def use(self, player, game):
        super().use(player, game)
        if player.mana < 10:
            player.mana += 1


class Weapon(Bindable):
    """
    Represents a Hearthstone weapon.  All weapons have attack power and durability.  The logic for handling the
    attacks is handled by :class:`Hero`, but it can be modified through the use of events.
    """

    def __init__(self, attack_power, durability, battlecry=None, deathrattle=None):
        """
        Creates a new weapon with the given attack power and durability.  A battlecry and deathrattle can also
        optionally be set.
        :param int attack_power: The amount of attack this weapon gives the hero
        :param int durability: The number of times this weapon can be used to attack before being discarded
        :param function battlecry: Called when this weapon is equipped
        :param function deathrattle: Called when the weapon is destroyed
        """
        super().__init__()
        # : The amount of attack this weapon gives the hero
        self.base_attack = attack_power
        # : The number of times this weapon can be used to attack before being discarded
        self.durability = durability
        #: Called when this weapon is equipped
        self.battlecry = battlecry
        #: Called when the weapon is destroyed
        self.deathrattle = deathrattle
        #: The :class:`Player` associated with this weapon
        self.player = None
        #: The :class:`WeaponCard` that created this weapon
        self.card = None

    def copy(self, new_owner):
        new_weapon = copy.copy(self)
        new_weapon.events = copy.copy(self.events)
        new_weapon.player = new_owner
        self.trigger("copied", new_weapon, new_owner)
        return new_weapon

    def destroy(self):
        self.trigger("destroyed")
        # Deathrattle is triggered no matter how the weapon is destroyed, see
        # http://www.hearthhead.com/card=1805/deaths-bite#comments:id=1983510
        if self.deathrattle is not None:
            self.deathrattle(self)
        self.player.hero.weapon = None
        if self.player.game.current_player is self.player:
            self.player.hero.change_temp_attack(-self.base_attack)
        self.player.hero.windfury = False

    def equip(self, player):
        self.player = player
        if self.player.hero.weapon is not None:
            self.player.hero.weapon.destroy()
        self.player.hero.weapon = self
        if self.player.game.current_player is self.player:
            self.player.hero.change_temp_attack(self.base_attack)
        self.player.hero.trigger("weapon_equipped")


class Deck:
    def __init__(self, cards, character_class):
        if len(cards) != 30:
            raise GameException("Deck must have exactly 30 cards in it")
        self.cards = cards
        self.character_class = character_class
        self.used = [False] * 30
        self.left = 30

    def copy(self):
        return copy.deepcopy(self)

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

        self.armor = 0
        self.weapon = None
        self.character_class = character_class
        self.player = player
        self.power = hearthbreaker.powers.powers(self.character_class)(self)

    def copy(self, new_owner, new_game):
        new_hero = copy.copy(self)
        new_hero.events = dict()
        if self.weapon:
            new_hero.weapon = self.weapon.copy(new_owner)
        new_hero.player = new_owner
        new_hero.power = copy.copy(self.power)
        new_hero.power.hero = new_hero
        return new_hero

    def attack(self):
        super().attack()
        if self.weapon is not None:
            self.weapon.durability -= 1
            if self.weapon.durability is 0:
                self.weapon.destroy()

    def damage(self, amount, attacker):
        self.armor -= amount
        if self.armor < 0:
            new_amount = -self.armor
            self.armor = 0
            super().damage(new_amount, attacker)

    def increase_armor(self, amount):
        self.trigger("armor_increased", amount)
        self.armor += amount

    def die(self, by):
        super().die(by)
        self.player.game.game_over()

    def find_power_target(self):
        targets = hearthbreaker.targeting.find_spell_target(self.player.game, lambda t: t.spell_targetable())
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
        self.graveyard = set()
        self.random = random_func
        self.hand = []
        self.auras = []
        self.fatigue = 0
        self.agent = agent
        self.game = game
        self.effects = []
        self.secrets = []
        self.spell_multiplier = 1
        self.heal_multiplier = 1
        self.heal_does_damage = False
        self.mana_filters = []
        self.overload = 0
        self.effect_count = dict()
        self.opponent = None
        self.cards_played = 0
        self.dead_this_turn = []

    def __str__(self):  # pragma: no cover
        return "Player: " + self.name

    def copy(self, new_game):
        copied_player = copy.copy(self)
        copied_player.events = dict()
        copied_player.auras = []
        copied_player.mana_filters = []
        copied_player.effects = []
        for effect in self.effects:
            copied_player.add_effect(effect)
        copied_player.hero = self.hero.copy(copied_player, new_game)
        copied_player.deck = self.deck.copy()
        copied_player.graveyard = copy.copy(self.graveyard)
        copied_player.minions = [minion.copy(copied_player, new_game) for minion in self.minions]
        copied_player.hand = [type(card)() for card in self.hand]
        copied_player.game = new_game
        copied_player.secrets = [type(secret)() for secret in self.secrets]
        copied_player.effect_count = dict()
        return copied_player

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
            return -(base_heal + self.spell_damage) * self.spell_multiplier
        else:
            return base_heal * self.heal_multiplier

    def put_back(self, card):
        self.hand.remove(card)
        self.deck.put_back(card)
        self.trigger("card_put_back", card)

    def discard(self):
        if len(self.hand) > 0:
            targets = self.hand
            target = targets[self.random(0, len(targets) - 1)]
            self.hand.remove(target)
            self.trigger("card_discarded", target)

    def add_effect(self, effect):
        self.effects.append(effect)
        effect.apply(self)

    def choose_target(self, targets):
        return self.agent.choose_target(targets)


class Game(Bindable):
    def __init__(self, decks, agents, random_func=random.randint):
        super().__init__()
        self.delayed_minions = set()
        self.random = random_func
        first_player = random_func(0, 1)
        if first_player is 0:
            play_order = [0, 1]
        else:
            play_order = [1, 0]
        self.players = [Player("one", decks[play_order[0]], agents[play_order[0]], self, random_func),
                        Player("two", decks[play_order[1]], agents[play_order[1]], self, random_func)]
        self.current_player = self.players[0]
        self.other_player = self.players[1]
        self.current_player.opponent = self.other_player
        self.other_player.opponent = self.current_player
        self.game_ended = False
        self.minion_counter = 0
        for i in range(0, 3):
            self.players[0].draw()

        for i in range(0, 4):
            self.players[1].draw()

    def check_delayed(self):
        sorted_minions = sorted(self.delayed_minions, key=lambda m: m.born)
        self.delayed_minions = set()
        for minion in sorted_minions:
            minion.activate_delayed()

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

        self.players[1].hand.append(TheCoin())

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
        for minion in self.current_player.minions:
            minion.active = True
        self.current_player.mana = self.current_player.max_mana - self.current_player.overload
        self.current_player.overload = 0
        self.current_player.cards_played = 0
        self.current_player.dead_this_turn = []
        self.current_player.trigger("turn_started")
        if self.current_player.hero.weapon is not None:
            self.current_player.hero.change_temp_attack(self.current_player.hero.weapon.base_attack)
        self.current_player.hero.power.used = False
        self.current_player.hero.active = True
        self.current_player.draw()

    def game_over(self):
        self.game_ended = True

    def _end_turn(self):
        self.current_player.trigger("turn_ended")
        self.current_player.hero.temp_attack = 0
        self.other_player.hero.temp_attack = 0

        if self.current_player.hero.frozen_this_turn:
            self.current_player.hero.frozen_this_turn = False
        else:
            self.current_player.hero.frozen = False

        self.other_player.hero.frozen_this_turn = False
        for minion in self.other_player.minions:
            minion.frozen_this_turn = False
            minion.temp_attack = 0

        for minion in self.current_player.minions:
            minion.active = False
            minion.exhausted = False
            minion.used_windfury = False
            minion.temp_attack = 0
            if minion.frozen_this_turn:
                minion.frozen_this_turn = False
            else:
                minion.frozen = False

        for secret in self.other_player.secrets:
            secret.deactivate(self.other_player)

        self.check_delayed()

    def copy(self):
        copied_game = copy.copy(self)
        copied_game.players = [player.copy(copied_game) for player in self.players]
        if self.current_player is self.players[0]:
            copied_game.current_player = copied_game.players[0]
            copied_game.other_player = copied_game.players[1]
        else:
            copied_game.current_player = copied_game.players[1]
            copied_game.other_player = copied_game.players[0]

        copied_game.current_player.opponent = copied_game.other_player
        copied_game.other_player.opponent = copied_game.current_player

        for player in copied_game.players:
            for minion in player.minions:
                for effect in minion._effects_to_add:
                    minion.add_effect(effect)
                minion._effects_to_add = []

        for secret in copied_game.other_player.secrets:
            secret.activate(copied_game.other_player)
        return copied_game

    def play_card(self, card):
        if self.game_ended:
            raise GameException("The game has ended")
        if not card.can_use(self.current_player, self):
            raise GameException("That card cannot be used")
        card_index = self.current_player.hand.index(card)
        self.current_player.hand.pop(card_index)
        self.current_player.trigger("card_played", card, card_index)
        self.current_player.mana -= card.mana_cost(self.current_player)
        if card.overload != 0:
            self.current_player.trigger("overloaded")

        if card.is_spell():
            self.current_player.trigger("spell_cast", card)

        if not card.cancel:
            card.use(self.current_player, self)
            self.current_player.trigger("card_used", card)
            self.current_player.cards_played += 1
            self.check_delayed()

    def remove_minion(self, minion, player):
        player.minions.remove(minion)
        player.trigger("minion_removed", minion)
