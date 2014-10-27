import re
import json

import hearthbreaker
import hearthbreaker.constants
from hearthbreaker.constants import CHARACTER_CLASS
import hearthbreaker.game_objects
import hearthbreaker.cards
import hearthbreaker.game_objects
import hearthbreaker.proxies
from hearthbreaker.serialization.move import Move, SpellMove, MinionMove, AttackMove, PowerMove, TurnEndMove, \
    TurnStartMove, ConcedeMove


class ReplayException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Replay:
    def __init__(self, filename=None):
        self.actions = []
        self.last_card = None
        self.card_class = None
        self.last_target = None
        self.last_index = None
        self.decks = []
        self.keeps = []
        self.header_random = []
        if filename is not None:
            self.read_replay_json(filename)

    def save_decks(self, deck1, deck2):
        self.decks = [deck1, deck2]

    def record_random(self, result):
        if len(self.actions) > 0:
            self.actions[-1].random_numbers.append(result)
        else:
            self.header_random.append(result)

    def _save_played_card(self):
        if self.last_card is not None:
            if issubclass(self.card_class, hearthbreaker.game_objects.MinionCard):
                if self.last_card.targetable:
                    self.actions.append(MinionMove(self.last_card, self.last_index, self.last_target))
                    self.last_card = None
                    self.last_index = None
                    self.last_target = None
                else:
                    self.actions.append(MinionMove(self.last_card, self.last_index))
                    self.last_card = None
                    self.last_index = None
            else:
                if self.last_card.targetable:
                    self.actions.append(SpellMove(self.last_card, self.last_target))
                    self.last_card = None
                    self.last_target = None
                else:
                    self.actions.append(SpellMove(self.last_card))
                    self.last_card = None

    def record_card_played(self, card, index):
        self._save_played_card()
        self.last_card = hearthbreaker.proxies.ProxyCard(index)
        self.last_card.targetable = card.targetable
        self.card_class = type(card)

    def record_option_chosen(self, option):
        self.last_card.set_option(option)

    def record_attack(self, attacker, target):
        self._save_played_card()
        self.actions.append(AttackMove(attacker, target))

    def record_power(self):
        self._save_played_card()
        self.actions.append(PowerMove())

    def record_power_target(self, target):
        self.actions[len(self.actions) - 1].target = hearthbreaker.proxies.ProxyCharacter(target)

    def record_kept_index(self, cards, card_index):
        k_arr = []
        for index in range(0, len(cards)):
            if card_index[index]:
                k_arr.append(index)
        self.keeps.append(k_arr)

    def __shorten_deck(self, cards):
        """
        Mostly for testing, this function will check if the deck is made up of a repeating pattern  and if so, shorten
        the output, since the parser will generate the pattern from a shorter sample
        :param cards: The deck of cards to replace
        :return: an array of cards that represents the deck if repeated until 30 cards are found
        """
        for pattern_length in range(1, 15):
            matched = True
            for index in range(pattern_length, 30):
                if not isinstance(cards[index % pattern_length], type(cards[index])):
                    matched = False
                    break
            if matched:
                return cards[0:pattern_length]

    def write_replay(self, file):
        if 'write' not in dir(file):
            writer = open(file, 'w')
        else:
            writer = file

        for deck in self.decks:
            writer.write("deck(")
            writer.write(hearthbreaker.constants.CHARACTER_CLASS.to_str(deck.character_class))
            writer.write(",")
            writer.write(",".join([card.name for card in self.__shorten_deck(deck.cards)]))
            writer.write(")\n")
        found_random = False
        if self.header_random.count(0) == len(self.header_random):
            for action in self.actions:
                if action.random_numbers.count(0) != len(action.random_numbers):
                    found_random = True
                    break
        else:
            found_random = True
        if not found_random:
            writer.write("random()\n")
        else:
            writer.write("random(")
            writer.write(",".join([str(num) for num in self.header_random]))
            writer.write(")\n")

        for keep in self.keeps:
            writer.write("keep(")
            writer.write(",".join([str(k) for k in keep]))
            writer.write(")\n")

        for action in self.actions:
            writer.write(action.to_output_string() + "\n")
            if len(action.random_numbers) > 0:
                writer.write("random(")
                writer.write(",".join([str(num) for num in action.random_numbers]))
                writer.write(")\n")

    def write_replay_json(self, file):
        if 'write' not in dir(file):
            writer = open(file, 'w')
        else:
            writer = file

        header_cards = [{"cards": [card.name for card in self.__shorten_deck(deck.cards)],
                         "class": CHARACTER_CLASS.to_str(deck.character_class)} for deck in self.decks]

        header = {
            'decks': header_cards,
            'keep': self.keeps,
            'random': self.header_random,
        }
        json.dump({'header': header, 'actions': self.actions}, writer, default=lambda o: o.__to_json__(), indent=2)

    def read_replay_json(self, file):
        if 'read' not in dir(file):
            file = open(file, 'r')

        jd = json.load(file)
        self.decks = []
        for deck in jd['header']['decks']:
            deck_size = len(deck['cards'])
            cards = [hearthbreaker.game_objects.card_lookup(deck['cards'][index % deck_size]) for index in range(0, 30)]
            self.decks.append(
                hearthbreaker.game_objects.Deck(cards, CHARACTER_CLASS.from_str(deck['class'])))

        self.header_random = jd['header']['random']
        self.keeps = jd['header']['keep']
        if len(self.keeps) == 0:
            self.keeps = [[0, 1, 2], [0, 1, 2, 3]]
        self.actions = [Move.from_json(**js) for js in jd['actions']]

    def parse_replay(self, replayfile):

        if 'read' not in dir(replayfile):
            replayfile = open(replayfile, 'r')
        line_pattern = re.compile("\s*(\w*)\s*\(([^)]*)\)\s*(;.*)?$")
        for line in replayfile:
            (action, args) = line_pattern.match(line).group(1, 2)
            args = [arg.strip() for arg in args.split(",")]
            if action == 'play':
                card = args[0]
                if len(args) > 1:
                    target = args[1]
                else:
                    target = None
                self.actions.append(SpellMove(hearthbreaker.proxies.ProxyCard(card), target))

            elif action == 'summon':
                card = args[0]

                index = int(args[1])

                if len(args) > 2:
                    target = args[2]
                else:
                    target = None

                self.actions.append(MinionMove(hearthbreaker.proxies.ProxyCard(card), index, target))
            elif action == 'attack':
                self.actions.append(AttackMove(args[0], args[1]))
            elif action == 'power':
                if len(args) > 0 and args[0] != '':
                    self.actions.append(PowerMove(args[0]))
                else:
                    self.actions.append(PowerMove())
            elif action == 'end':
                self.actions.append(TurnEndMove())
            elif action == 'start':
                self.actions.append(TurnStartMove())
            elif action == 'random':
                if len(self.actions) == 0:
                    if len(args[0]) > 0:
                        for num in args:
                            self.header_random.append(int(num))

                else:
                    for num in args:
                        if num.isdigit():
                            self.actions[-1].random_numbers.append(int(num))
                        else:
                            self.actions[-1].random_numbers.append(hearthbreaker.proxies.ProxyCharacter(num))

            elif action == 'deck':
                if len(self.decks) > 1:
                    raise ReplayException("Maximum of two decks per file")
                deck_size = len(args) - 1
                cards = [hearthbreaker.game_objects.card_lookup(args[1 + index % deck_size]) for index in range(0, 30)]
                self.decks.append(
                    hearthbreaker.game_objects.Deck(cards, hearthbreaker.constants.CHARACTER_CLASS.from_str(args[0])))

            elif action == 'keep':
                if len(self.keeps) > 1:
                    raise ReplayException("Maximum of two keep directives per file")
                self.keeps.append([int(a) for a in args])

            elif action == 'concede':
                self.actions.append(ConcedeMove())
        replayfile.close()
        if len(self.keeps) is 0:
            self.keeps = [[0, 1, 2], [0, 1, 2, 3]]


def record(game):

    class RecordingAgent:
        __slots__ = ['agent']

        def __init__(self, proxied_agent):
            object.__setattr__(self, "agent", proxied_agent)

        def choose_index(self, card, player):
            index = self.agent.choose_index(card, player)
            replay.last_index = index
            return index

        def choose_target(self, targets):
            target = self.agent.choose_target(targets)
            replay.last_target = target
            return target

        def choose_option(self, *options):
            option = self.agent.choose_option(options)

            replay.record_option_chosen(options.index(option))
            return option

        def __getattr__(self, item):
            return self.agent.__getattribute__(item)

        def __setattr__(self, key, value):
            setattr(self.__getattribute__("agent"), key, value)

    replay = hearthbreaker.replay.Replay()
    replay.header_random.append(game.first_player)

    game.players[0].agent = RecordingAgent(game.players[0].agent)
    game.players[1].agent = RecordingAgent(game.players[1].agent)

    if game.first_player == 0:
        replay.save_decks(game.players[0].deck, game.players[1].deck)
    else:
        replay.save_decks(game.players[1].deck, game.players[0].deck)

    game.bind("kept_cards", replay.record_kept_index)

    for player in game.players:
        player.bind("used_power", replay.record_power)
        player.hero.bind("found_power_target", replay.record_power_target)
        player.bind("card_played", replay.record_card_played)
        player.bind("attack", replay.record_attack)

    _old_random_choice = game.random_choice
    _old_generate_random_between = game._generate_random_between
    _old_start_turn = game._start_turn
    _old_end_turn = game._end_turn

    def random_choice(choice):
        result = _old_random_choice(choice)
        if isinstance(result, hearthbreaker.game_objects.Character):
            replay.actions[-1].random_numbers[-1] = hearthbreaker.proxies.ProxyCharacter(result)
        return result

    def _generate_random_between(lowest, highest):
        result = _old_generate_random_between(lowest, highest)
        replay.record_random(result)
        return result

    def _end_turn():
        replay._save_played_card()
        replay.actions.append(TurnEndMove())
        _old_end_turn()

    def _start_turn():
        replay.actions.append(TurnStartMove())
        _old_start_turn()

    game.random_choice = random_choice
    game._generate_random_between = _generate_random_between
    game._end_turn = _end_turn
    game._start_turn = _start_turn

    return replay


def playback(replay):

    action_index = -1
    k_index = 0
    random_index = 0
    game = None

    class ReplayAgent:

        def __init__(self):
            self.next_target = None
            self.next_index = -1
            self.next_option = None

        def do_card_check(self, cards):
            nonlocal k_index
            keep_arr = [False] * len(cards)
            for index in replay.keeps[k_index]:
                keep_arr[int(index)] = True
            k_index += 1
            return keep_arr

        def do_turn(self, player):
            nonlocal action_index, random_index
            while action_index < len(replay.actions) and not player.hero.dead and type(
                    replay.actions[action_index]) is not hearthbreaker.serialization.move.TurnEndMove:
                random_index = 0
                replay.actions[action_index].play(game)
                action_index += 1

        def set_game(self, game):
            pass

        def choose_target(self, targets):
            return self.next_target

        def choose_index(self, card, player):
            return self.next_index

        def choose_option(self, *options):
            return options[self.next_option]
    game = hearthbreaker.game_objects.Game.__new__(hearthbreaker.game_objects.Game)
    _old_random_choice = game.random_choice
    _old_start_turn = game._start_turn
    _old_end_turn = game._end_turn
    _old_pre_game = game.pre_game

    def _generate_random_between(lowest, highest):
        nonlocal random_index
        if len(replay.header_random) == 0:
            return 0
        else:
            random_index += 1
            if action_index == -1:
                return replay.header_random[random_index - 1]
            return replay.actions[action_index].random_numbers[random_index - 1]

    def random_choice(choice):
        nonlocal action_index, random_index
        if isinstance(replay.actions[action_index].random_numbers[random_index], hearthbreaker.proxies.ProxyCharacter):
            result = replay.actions[action_index].random_numbers[random_index].resolve(game)
            random_index += 1
            return result
        return _old_random_choice(choice)

    def _start_turn():
        nonlocal action_index, random_index
        random_index = 0
        _old_start_turn()
        action_index += 1

    def _end_turn():
        nonlocal action_index, random_index
        random_index = 0
        _old_end_turn()
        action_index += 1

    def pre_game():
        nonlocal action_index
        _old_pre_game()
        action_index = 0

    game.random_choice = random_choice
    game._generate_random_between = _generate_random_between
    game._end_turn = _end_turn
    game._start_turn = _start_turn
    game.pre_game = pre_game

    game.__init__(replay.decks, [ReplayAgent(), ReplayAgent()])
    return game
