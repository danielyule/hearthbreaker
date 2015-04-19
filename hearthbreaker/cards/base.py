import abc
from functools import reduce
import hearthbreaker.constants
from hearthbreaker.constants import CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Bindable, GameObject, GameException, Hero


def _battlecry_targetable(target):
    return target.player is target.player.game.current_player or not target.stealth


def _is_spell_targetable(target):
    return target.spell_targetable() and not target.dead


class Card(Bindable, GameObject):
    """
    Represents a card in Heathstone.  Every card is implemented as a subclass, either directly or through
    :class:`MinionCard`, :class:`SecretCard` or :class:`WeaponCard`.  If it is a direct subclass of this
    class then it is a standard spell, whereas if it is a subclass of one of :class:`MinionCard`, :class:`SecretCard`
    or :class:`WeaponCard`., then it is a minion, secret or weapon respectively.

    In order to play a card, it should be passed to :meth:`Game.play_card`.  Simply calling :meth:`use` will
    cause its effect, but not update the game state.
    """

    def __init__(self, name, mana, character_class, rarity, collectible, target_func=None,
                 filter_func=_is_spell_targetable, overload=0, ref_name=None, effects=None, buffs=None):
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
            :param effects:  The effects that will be triggered for this card
            :type effects: [:class:`hearthbreaker.tags.base.Effect`]
            :param buffs:  The buffs that will be applied directly to this card
            :type buffs: [:class:`hearthbreaker.tags.base.Buff`]
        """
        Bindable.__init__(self)
        GameObject.__init__(self, effects=effects, buffs=buffs)
        self.name = name
        if ref_name:
            self.ref_name = ref_name
        else:
            self.ref_name = name
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
        self.drawn = True
        self.current_target = None
        self.collectible = collectible

    def can_choose(self, player):
        """
        Verifies if this card can be chosen from a list of options (i.e. in Tracking)

        :return: True if the card can be chosen, false otherwise.
        :rtype: bool
        """
        return True

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
        return player.mana >= self.mana_cost()

    def mana_cost(self):
        """
        Calculates the mana cost for this card.

        This cost is the base cost for the card, modified by any tags from the card itself, or
        from other cards (such as :class:`hearthbreaker.cards.minions.neutral.VentureCoMercenary`)


        :return: representing the actual mana cost of this card.
        :rtype: int
        """
        from hearthbreaker.tags.status import ManaChange
        # Mana appears to be calculated in reverse order from other stats (auras first, then buffs)

        mana = reduce(lambda a, b: b.update(self, a), [aura.status
                                                       for p in self.player.game.players
                                                       for aura in p.object_auras
                                                       if aura.match(self) and isinstance(aura.status, ManaChange)],
                      self.mana)
        mana = reduce(lambda a, b: b.update(self, a), [buff.status for buff in self.buffs
                                                       if isinstance(buff.status, ManaChange) and
                                                       (not buff.condition or buff.condition.evaluate(self, self))],
                      mana)

        return mana

    def use(self, player, game):
        """
        Use the card.

        This method will cause the card's effect, but will not update the game state or trigger any events.
        To play a card correctly, use :meth:`Game.play_card`.

        Implementations of new cards should override this method, but be sure to call ``super().use(player, game)``

        :param hearthbreaker.game_objects.Player player: The player who is using the card.
        :param hearthbreaker.game_objects.Game game: The game this card is being used in.
        """
        pass

    @staticmethod
    def is_card():
        return True

    def __to_json__(self):
        r_val = super().__to_json__()
        r_val['name'] = self.name
        return r_val

    def __str__(self):  # pragma: no cover
        """
        Outputs a description of the card for debugging purposes.
        """
        return self.name + " (" + str(self.mana) + " mana)"

    def replace(self, new_card):
        index = self.player.hand.index(self)
        self.unattach()
        new_card.attach(new_card, self.player)
        self.player.hand[index] = new_card


class MinionCard(Card, metaclass=abc.ABCMeta):
    """
    Describes a :class:`Card` for summoning a minion.  This is distinct from the :class:`Minion` that represents the
    minion after it has been played.  This class represents the card aspects (mana cost, character class and rarity)
    as well as being responsible for creating the minion that will be added to the table.

    :see: :class:`Card`
    :see: :meth:`create_minion`
    """
    def __init__(self, name, mana, character_class, rarity, collectible=True,
                 minion_type=hearthbreaker.constants.MINION_TYPE.NONE, ref_name=None, battlecry=None, choices=None,
                 combo=None, overload=0, effects=None, buffs=None):
        """
        All parameters are passed directly to the :meth:`superclass's __init__ method <Card.__init__>`.

        :param string name: The name of this card in English
        :param int mana: The base mana cost of this card
        :param int character_class: The character class that this card belongs to.  Should be a member of
                                    :class:`hearthbreaker.constants.CHARACTER_CLASS`
        :param int rarity: How rare the card is.  Should be a member of :class:`hearthbreaker.constants.CARD_RARITY`
        :param int minion_type: The type that the summoned minion will have.  Should be a member of
                                :class:`hearthbreaker.constants.MINION_TYPE`
        :param string ref_name: The name used for reference for this card.  If None (the default), the reference name
                                will be the same as its name.  Otherwise, this name must be unique across all cards.
        :param battlecry: Describes the battlecry this minion will use when it enters the field, or None for no
                          battlecry
        :type battlecry: :class:`hearthbreaker.tags.base.Battlecry`
        :param choices: Gives a list of :class:`hearthbreaker.tags.base.Choice` s for the user to pick between
        :type choices: [:class:`hearthbreaker.tags.base.Choice`]
        :param combo: Describes the battlecry this minion will have if played after another card.  Note that this
                      does not count as a battlecry for cards such as Nerub'ar Weblord.
        :type combo: :class:`hearthbreaker.tags.base.Battlecry`
        :param effects:  The effects that will be triggered for this card (as opposed to the minion this card creates)
            :type effects: [:class:`hearthbreaker.tags.base.Effect`]
        :param buffs:  The buffs that will be applied directly to this card (as opposed to the minion this card creates)
            :type buffs: [:class:`hearthbreaker.tags.base.Buff`]
        """
        super().__init__(name, mana, character_class, rarity, collectible, None, None, overload, ref_name,
                         effects, buffs)
        self.minion_type = minion_type
        if battlecry:
            if isinstance(battlecry, tuple):
                self.battlecry = battlecry
            else:
                self.battlecry = (battlecry,)
        else:
            self.battlecry = ()
        self.choices = choices
        self.combo = combo
        self._placeholder = None

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
         8. after_added event

        The precise ordering of events is necessary so that various tags (Sword of Justice, Knife Juggler, etc)
        trigger in the correct order, and to distinguish from :meth:`summon`, which is called when a minion is
        played as a side effect of of card (e.g. Feral Spirit)

        :param hearthbreaker.game_objects.Player player: The player who wants to play this card
        :param hearthbreaker.game_objects.Game game: The game this card will be played in.
        """
        from hearthbreaker.tags.status import ChangeAttack
        from hearthbreaker.tags.base import Buff
        super().use(player, game)
        if (len(player.minions) >= 7 and not self._placeholder) or len(player.minions) >= 8:
            raise GameException("Cannot place a minion on a board with more than 7 minons on it")
        minion = self.create_minion(player)
        minion.card = self
        minion.player = player
        minion.game = game
        # TODO Add a test to make sure that this is a valid index, or things shall explode
        if self._placeholder:
            minion.index = self._placeholder.index
            player.minions.remove(self._placeholder)
            for m in player.minions[minion.index:]:
                m.index -= 1
        else:
            minion.index = player.agent.choose_index(self, player)
        minion.add_to_board(minion.index)
        card_attack = self.calculate_stat(ChangeAttack, 0)
        if card_attack:
            minion.add_buff(Buff(ChangeAttack(card_attack)))
        player.trigger("minion_placed", minion)
        if self.choices:
            choice = player.agent.choose_option(self.choices, player)
            choice.do(minion)
        if self.combo and player.cards_played > 0:
            self.combo.do(minion)
        else:
            for battlecry in self.battlecry:
                if not battlecry.do(minion, minion):
                    break
        game.check_delayed()
        # In case the minion has been replaced by its battlecry (e.g. Faceless Manipulator)
        minion = minion.replaced_by if minion.replaced_by else minion
        if not minion.removed:
            player.trigger("minion_played", minion)
            player.trigger("minion_summoned", minion)
            player.trigger("after_added", minion)

    def summon(self, player, game, index):
        """
        Summons the minion associated with this card onto the board.  This is to be used when a spell
        created a minion, instead of being played from the hand.

        If the player already has 7 minions on the board, this method does nothing.

        This method operates in the following order:

         1. Minion is placed on the board
         2. minion_placed event
         3. minion_summoned_event
         4. after_added event

        The ordering is important so that efects trigger in the correct order.

        :see: :meth:`use`

        :param hearthbreaker.game_objects.Player player: The player the summoned minion will belong to
        :param hearthbreaker.game_objects.Player player: The player the summoned minion will belong to
        :param hearthbreaker.game_objects.Game game: The game the minion is being summoned to
        :param int index: The index where the new minion will be added
        """
        if len(player.minions) < 7:
            self.attach(self, player)
            minion = self.create_minion(player)
            minion.card = self
            minion.player = player
            minion.game = game
            minion.index = index
            minion.add_to_board(index)
            player.trigger("minion_placed", minion)
            player.trigger("minion_summoned", minion)
            player.trigger("after_added", minion)
            return minion

    @abc.abstractmethod
    def create_minion(self, player):
        """
        Creates the minion associated with this card.  This method is responsible for creating the :class:`Minion`
        object and adding any necessary tags.  This method must be overridden by a subclass's implementation.  For
        more details, see :doc:`contributing`.

        This method is only responsible for creating the minion and attaching events.  It is not responsible for setting
        the minion's player or game attributes, or correctly setting its index.  That is handled within :meth:`play`
        and :meth:`summon`

        :param hearthbreaker.game_objects.Player player: The player who the newly created minion will belong to.

        :rtype: hearthbreaker.game_objects.Minion
        """
        pass

    @staticmethod
    def is_spell():
        return False

    @staticmethod
    def is_minion():
        return True


class HeroCard(Card, metaclass=abc.ABCMeta):
    def __init__(self, name, character_class, health, power, minion_type=MINION_TYPE.NONE, ref_name=None):
        super().__init__(name, 0, character_class, CARD_RARITY.FREE, False, ref_name=ref_name)
        self.health = health
        self.power = power
        self.short_name = name.split(" ")[0]
        self.minion_type = minion_type

    def use(self, player, game):
        pass

    def create_hero(self, player):
        return Hero(self.health, self.character_class, self.power(), player)


class SpellCard(Card, metaclass=abc.ABCMeta):
    """
    Represents a card in Heathstone.  Every card is implemented as a subclass, either directly or through
    :class:`MinionCard`, :class:`SecretCard` or :class:`WeaponCard`.  If it is a direct subclass of this
    class then it is a standard spell, whereas if it is a subclass of one of :class:`MinionCard`, :class:`SecretCard`
    or :class:`WeaponCard`., then it is a minion, secret or weapon respectively.

    In order to play a card, it should be passed to :meth:`Game.play_card`.  Simply calling :meth:`use` will
    cause its effect, but not update the game state.
    """

    def __init__(self, name, mana, character_class, rarity, collectible=True, target_func=None,
                 filter_func=_is_spell_targetable, overload=0, ref_name=None, effects=None, buffs=None):
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
            :param effects:  The effects that will be triggered for this card
            :type effects: [:class:`hearthbreaker.tags.base.Effect`]
            :param buffs:  The buffs that will be applied directly to this card
            :type buffs: [:class:`hearthbreaker.tags.base.Buff`]
        """
        super().__init__(name, mana, character_class, rarity, collectible, target_func, filter_func,
                         overload, ref_name, effects, buffs)

    def can_choose(self, player):
        """
        Verifies if this card can be chosen from a list of options (i.e. in Tracking)

        :return: True if the card can be chosen, false otherwise.
        :rtype: bool
        """
        return True

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

        return super().can_use(player, game)

    def mana_cost(self):
        """
        Calculates the mana cost for this card.

        This cost is the base cost for the card, modified by any tags from the card itself, or
        from other cards (such as :class:`hearthbreaker.cards.minions.neutral.VentureCoMercenary`)

        :return: representing the actual mana cost of this card.
        :rtype: int
        """
        from hearthbreaker.tags.status import ManaChange
        return self.calculate_stat(ManaChange, self.mana)

    def use(self, player, game):
        """
        Use the card.

        This method will cause the card's effect, but will not update the game state or trigger any events.
        To play a card correctly, use :meth:`Game.play_card`.

        Implementations of new cards should override this method, but be sure to call ``super().use(player, game)``

        :param hearthbreaker.game_objects.Player player: The player who is using the card.
        :param hearthbreaker.game_objects.Game game: The game this card is being used in.
        """
        pass

    @staticmethod
    def is_spell():
        return True

    @staticmethod
    def is_card():
        return True

    def __to_json__(self):
        r_val = super().__to_json__()
        r_val['name'] = self.name
        return r_val


class SecretCard(Card, metaclass=abc.ABCMeta):
    def __init__(self, name, mana, character_class, rarity, collectible=True):
        super().__init__(name, mana, character_class, rarity, collectible, None)
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

    @staticmethod
    def is_secret():
        return True

    @staticmethod
    def is_spell():
        return True


class WeaponCard(Card, metaclass=abc.ABCMeta):
    """
    Represents a :class:`Card` for creating a :class:`Weapon`
    """

    def __init__(self, name, mana, character_class, rarity, collectible=True, overload=0, battlecry=None, combo=None):
        """
        Create a new :class:`WeaponCard`

        :param string name: The name of the weapon in English
        :param int mana: The base amount of mana this card costs
        :param int character_class: A constant from :class:`hearthbreaker.constants.CHARACTER_CLASS` denoting
                                    which character this card belongs to or
                                    :const:`hearthbreaker.constants.CHARACTER_CLASS.ALL` if neutral
        :param int rarity: A constant from :class:`hearthbreaker.constants.CARD_RARITY` denoting the rarity of the card.
        :param int overload: The amount of overload on the card
        :param battlecry: A battlecry that will activate when this weapon is equipped
        :type battlecry: :class:`hearthbreaker.tags.base.Battlecry`
        :param combo: A battlecry that will activate when this weapon is equipped and at least one other card has
                      been played.  If combo activates, battlecry will not
        :type combo: :class:`hearthbreaker.tags.base.Battlecry`
        """
        super().__init__(name, mana, character_class, rarity, collectible, None, None, overload)
        self.battlecry = battlecry
        self.combo = combo

    def use(self, player, game):
        """
        Create a new weapon and attach it to the player's hero

        :param Player player: The player who will use this weapon
        :param hearthbreaker.engine.Game game: The game this weapon will be used in
        """
        super().use(player, game)
        weapon = self.create_weapon(player)
        weapon.card = self
        weapon.player = player
        weapon.game = game
        if self.combo and player.cards_played > 0:
            self.combo.do(weapon)
        else:
            if self.battlecry:
                self.battlecry.do(weapon)

        weapon.equip(player)

    @abc.abstractmethod
    def create_weapon(self, player):
        """
        Create a new weapon.  Any new weapon cards which are created must override this method.
        """
        pass

    @staticmethod
    def is_spell():
        return False

    @staticmethod
    def is_weapon():
        return True


class ChoiceCard(Card):
    def __init__(self, name, mana, character_class, rarity, collectible=False, target_func=None,
                 filter_func=_is_spell_targetable, overload=0, ref_name=None, effects=None, buffs=None):
        super().__init__(name, mana, character_class, rarity, collectible, target_func, filter_func, overload,
                         ref_name, effects, buffs)

    def can_choose(self, player):
        self.player = player
        return self.can_use(player, player.game)
