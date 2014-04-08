Replay File Format
==================

The replay file format is a text file made up of a series of directives,
one per line.  In general, the file has two components: the [header](#Header), and the [actions](#Actions).
The format is case sensitive.

Header
------
The header consists of three directives: the [`deck`](#deck) directive, the [`random`](#random) directive and the [`keep`](#keep-optional) directive

###Deck
`deck(class, card1, card2,....,card30)`

The `deck` directive specifies the deck used by each player.  The first `deck` directive specifies the deck for the first
player, and the second for the second player.  The first argument specifies the class of this deck, and must be one of

 * Mage
 * Druid
 * Hunter
 * Priest
 * Paladin
 * Warlock
 * Rogue
 * Shaman
 * Warrior

The remaining 30 arguments are the cards that make up this deck, specified by their English card name.
If there are fewer than 30 cards specified, the cards specified will be repeated until the deck is full.
There are no checks to ensure that the deck is a valid Hearthstone deck (at most two of any card, or one of a legendary,
or that the cards match the class)
For example, if the deck is specified as

`deck(Mage, Innervate, Stonetusk Boar, Warsong Commander, Arcane Missiles)`

Then the deck will be a mage deck with 8 Innervates and Stonetusk Boars, and 7 Warsong Commanders and Arcane Missiles.

###Keep (optional)
`keep([index1, [index2, [index3, [index4]]]])`

The  `keep` directive specifies which cards each player keeps at the beginning of the game.
The first `keep` directive specifies the deck for the first player (in play order) and the second specifies the deck for the
second player.  The arguments are 0 to 4 integers specifying the indices of the cards in the hand that the player kept.
For example, if the keep is specified as

`keep(1, 3)`

Then the player (who must be the second player in this example) keeps the second and fourth card of their initial draw.
The other two are put back and re-drawn.

If keep is not specified, then it is assumed that all the cards are kept.

###Random
`random([rint1, rint2, rint3...])`

The `random` directive specifies the random numbers used by the engine for any random choices that must be made
(card draw, random targets, etc).  The arguments are the numbers used to play the game.  The numbers are specific
to this engine, as Hearthstone's engine's randomness is unknown.

Random numbers are used in the following ways:

 * Who will go first (0 for the first specified player, 1 for the other)
 * Card draw (the index of the card from those still remaining in the deck)
 * Target selection (the index of the target, starting with the player's minions, then the opponent's minions, then the player, then the opponent, with invalid targets removed from the array)
 * Random chance (by assigning an outcome to each integer value.  For example, Tinkmaster Overspark will assign the Squirrel to 0 and the Devilsaur to 1)

The first number always dictates the order of play, and the following seven are the opening draw.
From there, their usage varies by user choice (for example, if both players replace their whole hand, the
following seven numbers will also be card draw.

If no arguments are provided, then each time a random number is needed, 0 will be returned.

Actions
-------

Action directives specify user actions.  There are six types of user actions: [`play`](#play), [`summon`](#summon), [`attack`](#attack), [`power`](#power), [`end`](#end) and [`concede`](#concede).

###Play
`play(card_index[:option][, target])`

The `play` directive is used to indicate that a player has played a spell card.  `card_index` indicates the
index of the card in the player's hand, and the optional `option` specifier indicates which of the resulting options the
player chose.  For example, if the player chooses "Power of the Wild" they can choose to either summon a panther or
give all minions +1/+1.  Choosing 0 will result in a panther, 1 will result in +1/+1e. The optional `target` argument
specifies what the target of the spell should be.  If the spell requires a target (e.g. Fireball) then a target must be
provided. If the spell doesn't require a target (i.e. Innervate), then the parameter is ignored.

The `target` parameter uses the syntax `player[:minion_index]`.  The `player` component is either `p1` or `p2`,
`minion_index` is an integer specifying the index of the targeted minion.  If the card is targeting a player, the
`minion_index` component is left out.  For example

`play(0, p2)`

will play the first card in the player's hand, targeting the other player.  Conversely, something like

`play(1, p2:0)`

will play the second card in the player's hand, targeting the first minion on the second player's board.

###Summon
`summon(card_index, board_index[, target])`

The summon directive is similar the the `play` directive above, but summons a minion instead of playing a spell.
The `card_index` parameter is an integer specifying the index of the minion's card in the player's hand, and the optional
`option` specifier indicates which of the resulting options the player chose.  For example, if the player chooses
"Keeper of the Grove" they can choose to either silence a minions or
do two damage.  Choosing 0 will result in silence, 1 will result in two damage.  The
`board_index` parameter is an integer specifying where on the board the minion should be summoned.  0 corresponds to
before the first minion and `len(minions)` corresponds to after the last one.  If there are 3 minions (represented by M)
then the numbering scheme looks like

`0 (M) 1 (M) 2 (M) 3 (M) 4

The `target` parameter handles the case where the minion has a targetable battlecry, and the syntax is identical to the
 syntax for `play`.

###Attack
`attack(attacker, target)`

The `attack` directive indicates that a character has attacked another character.  The `attacker` parameter indicates
who is doing the attacking, and the `target` parameter indicates who is being attacked.  Both follow the format of the
`target` parameter of the `play` directive.

###Power
`power([target])`

The `power` directive indicates that a player has used their hero ability.  If their ability require a target
(Priest, Mage) then the `target` parameter indicates which character to target.  It uses the same syntax as the `play`
directive.

###End
`end()`

The `end` directive indicates that a player has ended their turn.

###Concede
`concede()`

The `concede` directive indicates that the current player has conceded the game.  This event immediately ends the game.
