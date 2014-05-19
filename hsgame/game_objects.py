import random
import hsgame.powers
import hsgame.targetting
import hsgame.constants
import abc


__author__ = 'Daniel'

card_table = {}


def card_lookup(card_name):
    def card_lookup_rec(card_type):
        subclasses = card_type.__subclasses__()
        if len(subclasses) is 0:
                card = card_type()
                card_table[card.name] = card_type
        for sub_type in subclasses:
            card_lookup_rec(sub_type)

    if len(card_table) == 0:
        for card_type in Card.__subclasses__():
            card_lookup_rec(card_type)

    return card_table[card_name]()


class GameException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Bindable:
    def __init__(self):
        self.events = {}

    def bind(self, event, function, *args, **kwargs):
        class Handler:
            def __init__(self, function, args, kwargs):
                self.args = args
                self.kwargs = kwargs
                self.function = function
                self.remove = False
                self.active = False


        if not event in self.events:
            self.events[event] = []

        self.events[event].append(Handler(function, args, kwargs))

    def bind_once(self, event, function, *args, **kwargs):
        class Handler:
            def __init__(self, function, args, kwargs):
                self.args = args
                self.kwargs = kwargs
                self.function = function
                self.remove = True
                self.active = False

        if not event in self.events:
            self.events[event] = []

        self.events[event].append(Handler(function, args, kwargs))

    def trigger(self, event, *args, **kwargs):
        if event in self.events:
            for handler in self.events[event].copy():
                if not handler.active:
                    pass_args = args + handler.args
                    pass_kwargs = kwargs.copy()
                    pass_kwargs.update(handler.kwargs)
                    handler.active = True
                    handler.function(*pass_args, **pass_kwargs)
                    handler.active = False
                    if handler.remove:
                        self.events[event].remove(handler)
                        if len(self.events[event]) is 0:
                            del (self.events[event])

    def unbind(self, event, function):
        if event in self.events:
            self.events[event] = [handler for handler in self.events[event] if not handler.function == function]
            if len(self.events[event]) is 0:
                del (self.events[event])


class Card(Bindable):
    def __init__(self, name, mana, character_class, status, targetable, target_func=None):
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
        self.character_class = character_class
        self.status = status
        self.cancel = False
        self.targetable = targetable
        if targetable:
            self.targets = []
            self.target = None
            self.get_targets = target_func

    def can_use(self, player, game):
        if self.targetable:
            self.targets = self.get_targets(game)
            if self.targets is not None and len(self.targets) is 0:
                return False

        return player.mana >= self.mana_cost(player)

    def mana_cost(self, player):
        calc_mana = self.mana
        for filter in player.mana_filters:
            if filter.filter(self):
                calc_mana -= filter.amount
                if calc_mana < filter.min:
                    return filter.min
        return calc_mana

    def use(self, player, game):
        if self.targetable:
            if self.targets is None:
                self.target = None
            else:
                self.target = player.agent.choose_target(self.targets)

    def is_spell(self):
        return True

    def __str__(self):
        return self.name + " (" + str(self.mana) + " mana)"


class MinionCard(Card,metaclass=abc.ABCMeta):
    def __init__(self, name, mana, character_class, status, targetable=False, targeting_func=None):
        super().__init__(name, mana, character_class, status, targetable, targeting_func)

    def can_use(self, player, game):
        return super().can_use(player, game)

    def use(self, player, game):
        super().use(player, game)
        self.create_minion(player).add_to_board(self, game, player, player.agent.choose_index(self))

    @abc.abstractmethod
    def create_minion(self, player):
        pass

    def is_spell(self):
        return False


class SecretCard(Card,metaclass=abc.ABCMeta):
    def __init__(self, name, mana, character_class, status):
        super().__init__(name, mana, character_class, status, False, None)
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
    def activate(self, player):
        pass

    @abc.abstractmethod
    def deactivate(self, player):
        pass


class Character(Bindable,metaclass=abc.ABCMeta):
    def __init__(self, attack_power, health, game):
        super().__init__()
        self.health = health
        self.max_health = health
        self.attack_power = attack_power
        self.active = False
        self.dead = False
        self.wind_fury = False
        self.used_wind_fury = False
        self.frozen = False
        self.frozen_this_turn = False
        self.temp_attack = 0
        self.game = game
        self.immune = False
        self.delayed = []

    def turn_complete(self):
        if self.temp_attack > 0:
            self.trigger("attack_decreased", self.temp_attack)
            self.temp_attack = 0

    def attack(self):
        if not self.can_attack():
            raise GameException("That minion cannot attack")

        found_taunt = False
        targets = []
        for enemy in self.game.other_player.minions:
            if enemy.taunt and not enemy.stealth:
                found_taunt = True
            if not enemy.stealth:
                targets.append(enemy)

        if found_taunt:
            targets = [target for target in targets if target.taunt]
        else:
            targets.append(self.game.other_player)

        target = self.choose_target(targets)

        if isinstance(target, Minion):
            self.trigger("attack_minion", target)
            target.trigger("attacked", self)
            if self.dead:
                return
            my_attack = self.attack_power + self.temp_attack #In case the damage causes my attack to grow
            self.physical_damage(target.attack_power, target)
            target.physical_damage(my_attack, self)
            target.activate_delayed()
        else:
            self.trigger("attack_player", target)
            target.trigger("attacked", self)
            if self.dead:
                return
            target.physical_damage(self.attack_power + self.temp_attack, self)
            target.activate_delayed()
            #TODO check if the player's weapon is out in the case of Misdirection

        self.activate_delayed()
        if self.wind_fury and not self.used_wind_fury:
            self.used_wind_fury = True
        else:
            self.active = False
        self.stealth = False

    @abc.abstractmethod
    def choose_target(self, targets):
        pass

    def delayed_trigger(self, event, *args, **kwargs):
        self.delayed.append({'event': event, 'args': args, 'kwargs': kwargs})
        self.game.delayed_minions.append(self)

    def activate_delayed(self):
        for delayed in self.delayed:
            self.trigger(delayed['event'], *delayed['args'], **delayed['kwargs'])

        self.delayed = []

    def damage(self, amount, attacker):
        if not self.immune:
            self.delayed_trigger("damaged", amount, attacker)
            #The response of a secret to damage must happen immediately
            self.trigger("secret_damaged", amount, attacker)
            self.health -= amount
            if type(attacker) is Minion:
                attacker.delayed_trigger("did_damage", amount, self)
            elif type(attacker) is Player:
                attacker.trigger("did_damage", amount, self)
            if self.health <= 0:
                self.die(attacker)

    def increase_attack(self, amount):
        def silence():
            self.attack_power -= amount
        self.trigger("attack_increased", amount)
        self.attack_power += amount
        self.bind_once('silenced', silence)

    def increase_temp_attack(self, amount):

        self.trigger("attack_increased", amount)
        self.temp_attack += amount

    def increase_health(self, amount):
        def silence():
            self.max_health -= amount
            if self.max_health < self.health:
                self.health = self.max_health
        self.trigger("health_increased", amount)
        self.max_health += amount
        self.health += amount
        self.bind_once('silenced', silence)

    def decrease_health(self, amount):
        def silence():
            # I think silence only restores its max health again. It does not heal as well.
            self.max_health += amount
        self.trigger("health_decreased", amount)
        self.max_health -= amount
        if self.health > self.max_health:
            self.health = self.max_health
        self.bind_once('silenced', silence)

    def freeze(self):
        self.frozen_this_turn = True
        self.frozen = True

    def silence(self):
        self.trigger("silenced")
        self.wind_fury = False
        self.frozen = False
        self.frozen_this_turn = False

    def spell_damage(self, amount, spellCard):
        self.trigger("spell_damaged", amount, spellCard)
        self.damage(amount, spellCard)

    def physical_damage(self, amount, attacker):
        self.trigger("physically_damaged", amount, attacker)
        if type(attacker) is Player:
            self.player_damage(amount, attacker)
        else:
            self.minion_damage(amount, attacker)

    def minion_damage(self, amount, minion):
        self.trigger("minion_damaged", amount, minion)
        self.damage(amount, minion)

    def player_damage(self, amount, player):
        self.trigger("player_damaged", amount, player)
        self.damage(amount, player)

    def heal(self, amount):
        self.trigger("healed", amount)
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def die(self, by):
        self.delayed_trigger("died", by)
        self.dead = True

    def can_attack(self):
        return self.attack_power + self.temp_attack > 0 and self.active and not self.frozen


class Minion(Character):
    def __init__(self, attack, health, type=hsgame.constants.MINION_TYPE.NONE):
        super().__init__(attack, health, None)
        self.type = type
        self.taunt = False
        self.stealth = False
        self.player = None
        self.card = None
        self.index = -1
        self.charge = False
        self.spell_power = 0
        self.divine_shield = False

    def add_to_board(self, card, game, player, index):
        self.card = card
        player.minions.insert(index, self)
        self.game = game
        self.player = player
        player.spell_power += self.spell_power
        self.trigger("added_to_board", self)
        self.game.trigger("minion_added", self)
        for minion in player.minions:
            if minion.index >= index:
                minion.index += 1
        self.index = index
        if self.charge:
            self.active = True
        player.bind("turn_ended", self.turn_complete)
        
    def remove_from_board(self):
        self.player.spell_power -= self.spell_power
        for minion in self.player.minions:
            if minion.index > self.index:
                minion.index -= 1
        self.game.remove_minion(self, self.player)
        self.player.unbind("turn_ended", self.turn_complete)

    def attack(self):
        self.player.trigger("attacking", self)
        super().attack()
        self.stealth = False

    def silence(self):
        super().silence()
        self.taunt = False
        self.stealth = False
        self.charge = False
        self.player.spell_power -= self.spell_power
        self.spell_power = 0
        self.divine_shield = False

    def damage(self, amount, attacker):
        if self.divine_shield:
            self.divine_shield = False
        else:
            super().damage(amount, attacker)

    def die(self, by):
        super().die(by)
        self.game.trigger("minion_died", self, by)
        self.remove_from_board()

    def can_be_attacked(self):
        return not self.stealth

    def spell_targettable(self):
        return not self.stealth

    def choose_target(self, targets):
        return self.player.choose_target(targets)

    def __str__(self):
        return "({0}) ({1}) {2} at index {3}".format(self.attack_power, self.health, self.card.name, self.index)


class Deck:
    def __init__(self, cards, character_class):
        self.cards = cards
        self.character_class = character_class
        self.used = [False] * 30
        self.left = 30

    def can_draw(self):
        return self.left > 0

    def draw(self, random):
        if not self.can_draw():
            raise GameException("Cannot draw more than 30 cards")

        index = random(0, self.left - 1)
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


class Player(Character):
    def __init__(self, name, deck, agent, game, random=random.randint):
        super().__init__(0, 30, game)
        self.name = name
        self.mana = 0
        self.max_mana = 0
        self.armour = 0
        self.deck = deck
        self.spell_power = 0
        self.minions = []
        self.weapon = None
        self.character_class = deck.character_class
        self.random = random
        self.hand = []
        self.fatigue = 0
        self.agent = agent
        self.game = game
        self.secrets = []
        self.mana_filters = []
        self.power = hsgame.powers.powers(self.character_class)(self)
        self.bind("turn_ended", self.turn_complete)

    def __str__(self):
        return "Player: " + self.name

    def attack(self):
        self.trigger("attacking", self)
        super().attack()

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
            self.trigger("fatigue_damage", self.fatigue)
            self.damage(self.fatigue, self)
            self.activate_delayed()

    def can_draw(self):
        return self.deck.can_draw()

    def put_back(self, card):
        self.hand.remove(card)
        self.deck.put_back(card)
        self.trigger("card_put_back", card)

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

    def spell_targettable(self):
        return True

    def find_power_target(self):
        targets = hsgame.targetting.find_spell_target(self.game)
        target = self.agent.choose_target(targets)
        self.trigger("found_power_target", target)
        return target

    def choose_target(self, targets):
        return self.agent.choose_target(targets)


class Game(Bindable):
    def __init__(self, decks, agents, random=random.randint):
        super().__init__()
        self.delayed_minions = []
        self.random = random
        first_player = random(0, 1)
        if first_player is 0:
            play_order = [0, 1]
        else:
            play_order = [1, 0]
        self.players = [Player("one", decks[play_order[0]], agents[play_order[0]], self, random),
                        Player("two", decks[play_order[1]], agents[play_order[1]], self, random)]
        agents[0].set_game(self)
        agents[1].set_game(self)
        self.current_player = self.players[0]
        self.other_player = self.players[1]
        self.game_ended = False
        for i in range(0,3):
            self.players[0].draw()

        for i in range(0,4):
            self.players[1].draw()


        self.players[0].bind("died", self.game_over)
        self.players[1].bind("died", self.game_over)

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
        self.current_player.mana = self.current_player.max_mana
        self.current_player.trigger("turn_started")
        self.current_player.draw()

    def game_over(self, attacker):
        self.game_ended = True

    def _end_turn(self):
        self.current_player.trigger("turn_ended")
        if self.current_player.frozen_this_turn:
            self.current_player.frozen_this_turn = False
        else:
            self.current_player.frozen = False

        self.other_player.frozen_this_turn = False
        for minion in self.other_player.minions:
            minion.frozen_this_turn = False

        self.current_player.active = True
        for minion in self.current_player.minions:
            minion.active = True
            minion.used_wind_fury = False
            if minion.frozen_this_turn:
                minion.frozen_this_turn = False
            else:
                minion.frozen = False

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










