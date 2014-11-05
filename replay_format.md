# Replay Format

There are two replay formats that hearthbreaker recognizes: the [compact format](#compact-replay-file-format) and the
[complete format](#complete-format).  Either one can be used, although by default, hearthbreaker uses the complete 
format.  Further, the complete format has more robust validation applied.  There are examples of each in [`tests/replays`](tests/replays)

Documentation on how to use the replays can be found in the [Replays module](http://danielyule.github.io/hearthbreaker/hearthbreaker.replays.html).

Complete Replay File Format
===========================

The complete replay file format is based on JSON and is based on the Hearthstone Network Protocol.  The JSON object
that forms the basis of the replay has two properties: [header](#header) and [moves](#moves).  **Header** is an object
that describes the set up of the game, including the deck used by each player, and which cards they were shown and kept
during the mulligan phase.  **Moves** is an array of objects that describe the actions taken by each player throughout
the game.

```json
{
    "header": {...},
    "moves": [...]
}
```

Header
-----
The header is an object that describes the initial setup of the game.  It has three properties: [decks](#decks), [keep](#keep) and [random](#random)

```json
{
     "decks": [...],
     "keep": [...],
     "random": [...],
}
```

### Decks
The deck array consists of objects that specify which cards each player is using, as well as which class each player
is playing as.  The order of the decks given is not in play order.  Play order will be determined by the first number in
the [random](#random) property below.  Each object has two properties: `class` and `cards`.  

`class` is a string representation of the classes
in Hearthstone:
 
 * Mage
 * Druid
 * Hunter
 * Priest
 * Paladin
 * Warlock
 * Rogue
 * Shaman
 * Warrior

`cards` is a list of strings, each of which gives the name of a card to be used in the deck.  If there are fewer than
30 card names given, the cards are repeated until the deck is complete.  If more than 30 cards are given, only the
first 30 are used.

```json
{
    "character": "Mage" | "Druid" | "Hunter" | "Priest" | "Paladin" | "Warlock" | "Rogue" | "Shaman" | "Warrior",
    "cards": ["card_name_1", "card_name_2", ... , "card_name_30"]
}
```

### Keep

Keep gives a list of which cards each player chose to keep during the Mulligan phase.  Each player has an array of
integers which correspond to the indices of the cards they chose to keep.  The keep array **is** in play order, i.e.
the first entry in the array is the first player (who choses from three cards to keep) and the second is the second
player (who choses from four cards to keep, and gets the coin).

For example, if the first player keeps the first and last card, while the second player keeps all their cards, the `keep`
array would appear as follows:

```json
[
    [0, 2],
    [0, 1, 2, 3]
]
```

### Random

The `random` array is a list of the random numbers used during the initial phase of the game.  These numbers are used
to select which player goes first, which cards will be shown to each player for their mulligan, and which cards
are drawn to replace the mulliganed cards.  Note that this assumes that the replacement cards are chosen before the
cards they are replacing are put back.

If this array is empty, then every random number is assumed to be 0.

For more details on the meaning of the random numbers, see the note on [random semantics](#random-semantics)

Moves
-----
Moves is an array of move objects.  Each move object has two attributes: `name` (required) and `random` (optional).

`name` specifies the type of this move.  Can be one of [play](#play), [power](#power), [attack](#attack), [start](#start),
[end](#end) or [concede](#concede).

`random`, if present, specifies any random numbers needed to resolve this action.  For example, with [start](#start) this typically
 means a number corresponding to the card to draw, but can also be a character for effects which trigger at turn start.
 For example, if a Demolisher is present, the array of random numbers will need to contain a character reference for 
 which character is hit by the Demolisher's ability.
 
 ```json
 {
    "name": "play" | "use" | "attack" | "start" | "end" | "concede"
    "random": [...]
    .
    .
    .
 }
 ```
 For more details on the meaning of the random numbers, see the note on [random semantics](#random-semantics)
 
### Play
The play move corresponds to the current player playing a card from their hand.  This move three properties:
`card` (required), `index` (optional) and `target` (optional).

`card` specifies the index of the card in the player's hand.  This is from all cards, not just the cards that can be
played at the moment.

`index` specifies the location on the board that the minion should be inserted into, if the card being played is a minion

`target` is a [character reference](#character-reference) that specifies the target of the spell or battlecry if the card is a spell or minion with a battlecry that requires a target.

### Power
The power move corresponds to the current player using their hero power.  It has one optional property: `target`

`target` is a [character reference](#character-reference) that specifies the target of the hero power if the power requires a target (Mage and Priest)
 
### Attack
The attack move corresponds to a character belonging to the current player attacking a character belonging to the opposing player.  It has two required properties:
`character` and `target`

`character` is a [character reference](#character-reference) that specifies which character is performing the attack.

`target` is a [character reference](#character-reference) that specifies which character is being attacked

### Start
The start move corresponds to the beginning of the current player's turn.  It has no required properties.

### End
The end move corresponds to the end of the current player's turn.  It has no required properties.

### Concede
The concede move corresponds to a player giving up.  It should be the last move in a replay.  It has no required properties.

Compact Replay File Format
==========================

The compact replay file format is a text file made up of a series of directives,
one per line.  In general, the file has two components: the [header](#header-1), and the [moves](#moves-1).
The format is case sensitive.

Each header directive corresponds to a property in the complete format's header.  Each move directive corresponds to
a move object in the complete format, except that the `play` and `summon` directive are both handled by the 
`play` move object.

Header
------
The header consists of three directives: the [`deck`](#deck) directive, the [`random`](#random-1) directive and the [`keep`](#keep-optional) directive

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
(card draw, random targets, etc).  The arguments are the numbers used to play the game.

Random numbers are used in the following ways:

 * Who will go first (0 for the first specified player, 1 for the other)
 * Card draw (the index of the card from those still remaining in the deck)
 * Target selection (the index of the target, starting with the player's minions, then the opponent's minions, then the player, then the opponent, with invalid targets removed from the array)
 * Random chance (by assigning an outcome to each integer value.  For example, Tinkmaster Overspark will assign the Squirrel to 0 and the Devilsaur to 1)

The first number always dictates the order of play, and the following seven are the opening draw.
From there, their usage varies by user choice (for example, if both players replace their whole hand, the
following seven numbers will also be card draw.

If no arguments are provided, then each time a random number is needed, 0 will be returned.

There should be a `random` directive in the header to provide for the random draws during the game opening.
 
From there, and random directive will be associated with the directive before it.  So, each [`start`](#start) directive
should be followed by a `random` directive that gives which card is drawn.  For more details on the meaning of the 
random numbers, see the note on [random semantics](#random-semantics) 

Moves
-----
Move directives specify user actions.  There are six types of user moves: [`play`](#play-1), [`summon`](#summon), [`attack`](#attack-1), [`power`](#power-1), [`start`](#start-1), [`end`](#end-1) and [`concede`](#concede-1).

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

###Start
`start`
The `start` directive indicates that a player has started their turn.

###End
`end()`

The `end` directive indicates that a player has ended their turn.

###Concede
`concede()`

The `concede` directive indicates that the current player has conceded the game.  This event immediately ends the game.

Character Reference
-------------------
A character reference is an object that refers to a specific character on the game board.
It is represented as an object with two properties: `player` and `index`.  `player` is an integer indicating which
player the character belongs to.  `index` is optional.  If present, it indicates the index of the minion selected, left 
to right as represented on the Hearthstone gameboard.  If not present, it indicates that the hero should be selected.

The compact format represents a character reference as either `player` or `player:index` where `player` is either "p1" or "p2" and `index`, if present,
is an integer as above.  

Random Semantics
----------------
Random numbers are used in a number of different ways in Hearthstone.

 * Random card draws (at the start of each turn)
 * Random card selection (such as Voidcaller)
 * Random target selection (such as Demolisher)
 * Random amounts (such as Lightning Storm)
 * Probability selection (such as Nat Paggle)
 * Random choice (such as Tinkmaster Overspark)

All except random target selection are implemented as an integer chosen in a range.

### Random card draws
Random card draws are cards taken from the deck.  This happens every turn, but also happens with cards like Mad Scientist
and Deathlord.  The integer represents the location in the list of eligible cards.  So, if a Mad Scientist dies and a
player has Freezing Trap, Explosive Trap and Snipe in their deck, then the integer given must be between 0 and 2 inclusive.
However, if the player also has an explosive trap currently active, then only Freezing Trap and Snipe will be in the 
list, meaning the number must be either 0 or 1.  The order in the list corresponds to their order in the deck (as determined
by the `deck` property).

### Random card selection
Random card selection is used to chose a card from the hand.  This can be for stealing, or playing or discarding.  The 
integer represents the index of the selected card from among eligible cards, in order drawn (or left to right on the
Hearthstone screen).

For example, if the player has two demons in their hand and a Voidcaller dies, then the integer will be either 0 or 1,
with 0 corresponding to the demon that was drawn first, and 1 corresponding to the demon drawn second.

### Random character selection
Character selection can't be conveniently represented as a single integer without imposing an ordering on all characters
in the game.  Instead, it is represented as a [character reference](#character-reference).

### Random amounts
Used only for Lightning Storm, this indicates how much an amount should be, when chosen from a range.  For example, with
lightning storm and no modifiers, there will be one of these for each minion on the board, either 2 or 3.


### Probability Selection
Probability selection is used to decide if an action should happen.  This corresponds to a 1 in `n` chance that an action
occurs.  The if the integer is 0, then the action occurs, otherwise it does not.  The integer should be between 0 and 
`n` - 1 inclusive. 

### Random Choice
Random choice is used to choose between several options.  The choices are ordered as written on the card.  The integer
represents the index of the option chosen.
