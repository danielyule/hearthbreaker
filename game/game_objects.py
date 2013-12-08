from game.constants import CHARACTER_CLASS
from random import shuffle, randint

__author__ = 'Daniel'


class GameException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Bindable:
    def __init__(self):
        self.events = {}

    def bind(self, event, function):
        if not event in self.events:
            self.events[event] = []
        self.events[event].append(function)

    def trigger(self, event, *args, **kwargs):
        if event in self.events:
            for handler in self.events[event]:
                handler(*args, **kwargs)

    def unbind(self, event, function):
        self.events[event].remove(function)


class Card(Bindable):
    def __init__(self, name, mana, gold, character_class, status):
        """
            @name: string
            @mana: int
            @gold: int
            @character_class: CHARACTER_CLASS
            @status: CARD_STATUS
        """
        super().__init__()
        self.name = name
        self.mana = mana
        self.gold = gold
        self.character_class = character_class
        self.status = status

    def can_use(self, player, board):
        return player.mana >= self.mana

    def use(self, player, board):
        if self.can_use(player, board):
            player.mana -= self.mana
        else:
            raise GameException("Tried to play card that could not be played")

    def bind(self, event, function):
        if not event in self.events:
            self.events[event] = []
        self.events[event].append(function)

    def trigger(self, event, **args):
        for handler in self.events[event]:
            handler(args)


class MinionCard(Card):
    def __init__(self, name, mana, gold, character_class, status, minion):
        super().__init__(name, mana, gold, character_class, status)
        self.minion = minion

    def can_use(self, player, board):
        return super().can_use(player, board) and self.minion.can_use(player, board)

    def use(self, player, board):
        super().use(player, board)
        self.minion.add_to_board(self, board, player)


class Minion(Bindable):
    def __init__(self, attack, defense, type):
        self.attack = self.max_attack = attack
        self.defense = self.max_defense = defense
        self.type = type
        self.active = False
        self.dead = False
        self.taunt = False
        self.wind_fury = False
        self.used_wind_fury = False
        self.frozen = False
        self.stealth = False
        super().__init__()

    def can_use(self, player, board):
        return True

    def add_to_board(self, card, board, player):
        board.minions[player].append(self)
        self.board = board
        self.player = player
        self.card = card
        self.trigger("added_to_board")

    def attack(self, what):
        if isinstance(what, Minion):
            if not what.can_be_attacked():
                raise GameException("Cannot attack that minion")
            if not self.can_attack():
                raise GameException("That minion cannot attack")
            if self.game.is_active_taunt() and not what.taunt:
                raise GameException("Must attack a minion with taunt")
            self.board.trigger("minion_on_minion_attack", self, what)
        else:
            if not self.can_attack():
                raise GameException("That minion cannot attack")
            if self.game.is_active_taunt():
                raise GameException("Must attack a minion with taunt")

        self.trigger("attack_minion", what)
        if self.wind_fury and not self.used_wind_fury:
            self.used_wind_fury = True
        else:
            self.active = False
        self.stealth = False

        self.damage(what.attack, what)
        what.damage(self.attack, self)

    def damage(self, amount, attacker):
        self.trigger("damaged", amount, attacker)
        self.defense -= amount
        if self.defense <= 0:
            self.die(attacker)

    def die(self, by):
        self.trigger("death", by)
        self.game.trigger("minion_died", self, by)
        self.dead = True
        self.game.remove_minion(self)

    def can_attack(self):
        return self.active and not self.frozen

    def can_be_attacked(self):
        return not self.stealth


class Deck:
    def __init__(self, cards, character_class):
        self.cards = cards
        self.character_class = character_class
        self.used = [False] * 30
        self.left = 30

    def can_draw(self):
        return self.left > 0

    def draw(self):
        if not self.can_draw():
            raise GameException("Cannot draw more than 30 cards")

        index = randint(0, 29)
        while self.used[index]:
            index = randint(0, 29)

        self.used[index] = True
        return self.cards[index]

    def put_back(self, card):
        for index in range(0, 29):
            if self.cards[index] == card:
                if self.used[index] is False:
                    raise GameException("Tried to put back a card that hadn't been used yet")
                self.used[index] = False
                return
        raise GameException("Tried to put back a card that didn't come from this deck")


class Player(Bindable):
    def __init__(self, name, deck):
        self.name = name
        self.mana = 1
        self.health = 30
        self.deck = deck
        self.max_mana = 1
        self.armour = 0
        self.character_class = deck.character_class
        super().__init__()

    def __str__(self):
        return "Player: " + self.name

    def draw(self):
        return self.deck.draw()

    def can_draw(self):
        return self.deck.can_draw()

    def put_back(self, card):
        return self.deck.put_back(card)

    def damage(self, amount):
        self.trigger("damaged", amount)
        self.armour -= amount
        if self.armour < 0:
            self.health += self.armour
            self.armour = 0
        if self.health <= 0:
            self.die()

    def die(self):
        self.trigger("death")
        print(str(self) + " died")


class Board:
    def __init__(self, players):
        self.players = players
        self.minions = {players[0]: [], players[1]: []}
        self.weapons = {}


class Game(Bindable):
    def __init__(self, decks, agents):
        play_order = [0, 1]
        shuffle(play_order)
        self.players = [Player("one", decks[play_order[0]]), Player("two", decks[play_order[1]])]
        self.agents = {self.players[0]: agents[play_order[0]], self.players[1]: agents[play_order[1]]}
        self.current_player = self.players[0]
        self.board = Board(self.players)
        self.hands = {self.players[0]: [self.players[0].draw(), self.players[0].draw(), self.players[0].draw()],
                      self.players[1]: [self.players[1].draw(), self.players[1].draw(), self.players[1].draw(),
                                        self.players[1].draw()]}

        card_keep_index = self.agents[self.players[0]].do_card_check(self.hands[self.players[0]])
        for card_index in range(0, 3):
            if not card_keep_index[card_index]:
                self.hands[self.players[0]].append(self.players[0].draw())
                self.players[0].put_back(self.hands[self.players[0]][card_index])
                del self.hands[self.players[0]][card_index]

        card_keep_index = self.agents[self.players[1]].do_card_check(self.hands[self.players[1]])
        for card_index in range(0, 4):
            if not card_keep_index[card_index]:
                self.hands[self.players[1]].append(self.players[1].draw())
                self.players[1].put_back(self.hands[self.players[1]][card_index])
                del (self.hands[self.players[1]][card_index])

    def _start_turn(self):
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
        else:
            self.current_player = self.players[0]

        self.current_player.max_mana += 1
        self.current_player.mana = self.current_player.max_mana
        self.current_player.trigger("turn_start")
        if self.current_player.can_draw():
            self.hands[self.current_player].append(self.current_player.draw())
        else:
            self.current_player.damage(1)
        self.agents[self.current_player].do_turn()

    def end_turn(self):
        self.trigger("turn_ended")
        for minion in self.board.minions[self.current_player]:
            minion.active = True
            minion.used_wind_fury = False
            minion.frozen = False

    def play_card(self, card):
        if not card.can_use():
            raise GameException("That card cannot be used")
        self.trigger("card_played", card)
        card.use(self.current_player, self)
        self.hands[self.current_player].remove(card)





