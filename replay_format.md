Replay File Format
==================

The replay file format is a text file made up of a series of directives,
one per line.  In general, the file has two components: the header, and the actions.
The format is case sensitive.

The Header
----------
The header consists of three directives: the `deck` directive, the `random` directive and the `keep` directive

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

*deck(Mage, Innervate, Stonetusk Boar, Warsong Commander, Arcane Missiles)*

Then the deck will be a mage deck with 8 Innervates and Stonetusk Boars, and 7 Warsong Commanders and Arcane Missiles.

###Keep
`keep([index1, [index2, [index3, [index4]]]])`

The  **keep** directive specifies which cards each player keeps at the beginning of the game.
The first **keep** directive specifies the deck for the first player (in play order) and the second specifies the deck for the
second player.  The arguments are 0 to 4 integers specifying the indices of the cards in the hand that the player kept.
For example, if the keep is specified as

*keep(1, 3)*

Then the player (who must be the second player in this example) keeps the second and fourth card of their initial draw.
The other two are put back and re-drawn.

###

