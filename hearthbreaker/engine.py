import copy
import random
from hearthbreaker.cards.heroes import hero_from_name
import hearthbreaker.constants
from hearthbreaker.game_objects import Bindable, GameException, Minion, Hero
import hearthbreaker.tags
from hearthbreaker.tags.base import Effect, AuraUntil
import hearthbreaker.targeting


card_table = {}


def __create_card_table():
    from hearthbreaker.cards.base import WeaponCard, SpellCard, MinionCard, SecretCard, ChoiceCard, HeroCard

    def __card_lookup_rec(card_type):
        subclasses = card_type.__subclasses__()
        for sc in subclasses:
            c = sc()
            card_table[c.ref_name] = sc

    for card_class in [WeaponCard, SpellCard, MinionCard, SecretCard, ChoiceCard, HeroCard]:
        __card_lookup_rec(card_class)


def card_lookup(card_name):
    """
    Given a the name of a card as a string, return an object corresponding to that card

    :param str card_name: A string representing the name of the card in English
    :return: An instance of a subclass of Card corresponding to the given card name or None if no Card
             by that name exists.
    :rtype: hearthbreaker.game_objects.Card
    """

    card = card_table[card_name]
    if card is not None:
        return card()
    return None


def get_cards():
    card_list = filter(lambda c: c.collectible,
                       [card() for card in card_table.values()])
    return card_list


class Game(Bindable):
    def __init__(self, decks, agents):
        super().__init__()
        self.delayed_minions = set()
        self.first_player = self._generate_random_between(0, 1)
        if self.first_player is 0:
            play_order = [0, 1]
        else:
            play_order = [1, 0]
        self.players = [Player("one", decks[play_order[0]], agents[play_order[0]], self),
                        Player("two", decks[play_order[1]], agents[play_order[1]], self)]
        self.current_player = self.players[0]
        self.other_player = self.players[1]
        self.current_player.opponent = self.other_player
        self.other_player.opponent = self.current_player
        self.game_ended = False
        self.minion_counter = 0
        self.__pre_game_run = False
        self.last_card = None
        self._has_turn_ended = True
        self._all_cards_played = []

    def random_draw(self, cards, requirement):
        filtered_cards = [card for card in filter(requirement, cards)]
        if len(filtered_cards) > 0:
            return filtered_cards[self._generate_random_between(0, len(filtered_cards) - 1)]
        return None

    def random_choice(self, choice):
        return choice[self._generate_random_between(0, len(choice) - 1)]

    def random_amount(self, minimum, maximum):
        return self._generate_random_between(minimum, maximum)

    def _generate_random_between(self, lowest, highest):
        return random.randint(lowest, highest)

    def check_delayed(self):
        sorted_minions = sorted(self.delayed_minions, key=lambda m: m.born)
        self.delayed_minions = set()
        for minion in sorted_minions:
            minion.activate_delayed()

    def pre_game(self):
        if self.__pre_game_run:
            return
        self.__pre_game_run = True

        p1_draw = [self.players[0].deck.draw(self) for i in range(3)]
        p2_draw = [self.players[1].deck.draw(self) for i in range(4)]

        card_keep_index = self.players[0].agent.do_card_check(p1_draw)
        self.trigger("kept_cards", p1_draw, card_keep_index)
        put_back_cards = []
        for card_index in range(0, 3):
            if not card_keep_index[card_index]:
                put_back_cards.append(p1_draw[card_index])
                p1_draw[card_index] = self.players[0].deck.draw(self)
        self.players[0].hand = p1_draw
        for card in put_back_cards:
            self.players[0].put_back(card)
        for card in self.players[0].hand:
            card.attach(card, self.players[0])

        card_keep_index = self.players[1].agent.do_card_check(p2_draw)
        self.trigger("kept_cards", p2_draw, card_keep_index)
        put_back_cards = []
        for card_index in range(0, 4):
            if not card_keep_index[card_index]:
                put_back_cards.append(p2_draw[card_index])
                p2_draw[card_index] = self.players[1].deck.draw(self)
        self.players[1].hand = p2_draw
        for card in put_back_cards:
            self.players[1].put_back(card)

        for card in self.players[1].hand:
            card.attach(card, self.players[1])

        coin = card_lookup("The Coin")
        coin.player = self.players[1]
        self.players[1].hand.append(coin)

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
        if not self._has_turn_ended:  # when a game is copied, the turn isn't ended before the next one starts
            self._end_turn()
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
            minion.attacks_performed = 0
        self.current_player.mana = self.current_player.max_mana - self.current_player.overload
        self.current_player.overload = 0
        self.current_player.cards_played = 0
        self.current_player.dead_this_turn = []
        self.current_player.hero.power.used = False
        self.current_player.hero.attacks_performed = 0
        self.current_player.draw()
        self.current_player.trigger("turn_started", self.current_player)
        self._has_turn_ended = False

    def game_over(self):
        self.game_ended = True

    def _end_turn(self):
        from hearthbreaker.tags.status import Frozen
        self.current_player.trigger("turn_ended")
        if self.current_player.hero.frozen and \
                self.current_player.hero.attacks_performed < self.current_player.hero.attacks_allowed():
            self.current_player.hero.frozen = 0
            self.current_player.hero.buffs = \
                [buff for buff in self.current_player.hero.buffs if not isinstance(buff, Frozen)]

        for minion in self.current_player.minions:
            if minion.attacks_performed < minion.attacks_allowed() and minion.frozen:
                minion.frozen = False
                minion.buffs = [buff for buff in minion.buffs if not isinstance(buff, Frozen)]
            minion.exhausted = False
            minion.used_windfury = False
            minion.attacks_performed = 0

        for aura in copy.copy(self.current_player.object_auras):
            if isinstance(aura, AuraUntil):
                self.current_player.object_auras.remove(aura)
                aura.unapply()

        for secret in self.other_player.secrets:
            secret.deactivate(self.other_player)

        self.check_delayed()
        self._has_turn_ended = True

    def copy(self):
        copied_game = copy.copy(self)
        copied_game.events = {}
        copied_game._all_cards_played = []
        copied_game.players = [player.copy(copied_game) for player in self.players]
        if self.current_player is self.players[0]:
            copied_game.current_player = copied_game.players[0]
            copied_game.other_player = copied_game.players[1]
        else:
            copied_game.current_player = copied_game.players[1]
            copied_game.other_player = copied_game.players[0]

        copied_game.current_player.opponent = copied_game.other_player
        copied_game.other_player.opponent = copied_game.current_player
        copied_game._has_turn_ended = self._has_turn_ended

        for player in copied_game.players:
            player.hero.attach(player.hero, player)
            if player.hero.weapon:
                player.hero.weapon.attach(player.hero, player)
            for minion in player.minions:
                minion.attach(minion, player)

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
        self.current_player.mana -= card.mana_cost(self.current_player)
        self._all_cards_played.append(card)
        card.target = None
        card.current_target = None
        if card.targetable and card.targets:
            card.target = self.current_player.agent.choose_target(card.targets)

        self.last_card = card
        if card.is_minion():
            card._placeholder = Minion(0, 0)
            index = self.current_player.agent.choose_index(card, self.current_player)
            self.current_player.minions.insert(index, card._placeholder)
            card._placeholder.index = index
        self.current_player.trigger("card_played", card, card_index)

        if not card.cancel:
            card.use(self.current_player, self)
            card.unattach()
            self.current_player.trigger("card_used", card)
            self.current_player.cards_played += 1
            self.check_delayed()
        card.current_target = None

        # overload is applied regardless of counterspell, but after the card is played
        self.current_player.overload += card.overload

    def __to_json__(self):
        if self.current_player == self.players[0]:
            active_player = 1
        else:
            active_player = 2
        return {
            'players': self.players,
            'active_player': active_player,
            'current_sequence_id': self.minion_counter,
        }

    @staticmethod
    def __from_json__(d, agents):
        new_game = Game.__new__(Game)
        new_game._all_cards_played = []
        new_game.minion_counter = d["current_sequence_id"]
        new_game.delayed_minions = set()
        new_game.game_ended = False
        new_game.random_func = random.randint
        new_game.events = {}
        new_game.players = [Player.__from_json__(pd, new_game, None) for pd in d["players"]]
        new_game._has_turn_ended = False
        if d["active_player"] == 1:
            new_game.current_player = new_game.players[0]
            new_game.other_player = new_game.players[1]
            new_game.current_player.opponent = new_game.players[1]
            new_game.other_player.opponent = new_game.players[0]
        else:
            new_game.current_player = new_game.players[1]
            new_game.other_player = new_game.players[0]
            new_game.current_player.opponent = new_game.players[0]
            new_game.other_player.opponent = new_game.players[1]

        index = 0
        for player in new_game.players:
            player.agent = agents[index]
            for effect_json in d['players'][index]['effects']:
                player.add_effect(Effect.from_json(**effect_json))
            player.player_auras = []
            for aura_json in d['players'][index]['auras']:
                player.add_aura(AuraUntil.from_json(**aura_json))
            player.hero.attach(player.hero, player)
            if player.hero.weapon:
                player.hero.weapon.attach(player.hero, player)

            for minion in player.minions:
                minion.attach(minion, player)
                if minion.health != minion.calculate_max_health():
                    minion.enraged = True
            index += 1
        return new_game


class Player(Bindable):
    def __init__(self, name, deck, agent, game):
        super().__init__()
        self.game = game
        self.hero = deck.hero.create_hero(self)
        self.hero.card = deck.hero
        self.name = name
        self.mana = 0
        self.max_mana = 0
        self.deck = deck
        self.spell_damage = 0
        self.minions = []
        self.graveyard = set()
        self.hand = []
        self.object_auras = []
        self.player_auras = []
        self.fatigue = 0
        self.agent = agent
        self.effects = []
        self.secrets = []
        self.spell_multiplier = 1
        self.heal_multiplier = 1
        self.heal_does_damage = 0
        self.double_deathrattle = 0
        self.mana_filters = []
        self.overload = 0
        self.opponent = None
        self.cards_played = 0
        self.dead_this_turn = []

    def __str__(self):  # pragma: no cover
        return "Player: " + self.name

    def copy(self, new_game):
        copied_player = Player(self.name, self.deck.copy(), self.agent, new_game)

        copied_player.hero = self.hero.copy(copied_player)
        copied_player.graveyard = copy.copy(self.graveyard)
        copied_player.minions = [minion.copy(copied_player, new_game) for minion in self.minions]
        copied_player.hand = [copy.copy(card) for card in self.hand]
        for card in copied_player.hand:
            card._attached = False
            card.attach(card, copied_player)
        copied_player.spell_damage = self.spell_damage
        copied_player.mana = self.mana
        copied_player.max_mana = self.max_mana
        copied_player.overload = self.overload
        copied_player.dead_this_turn = copy.copy(self.dead_this_turn)
        for effect in self.effects:
            effect = copy.copy(effect)
            copied_player.add_effect(effect)
        copied_player.secrets = []
        for secret in self.secrets:
            new_secret = type(secret)()
            new_secret.player = copied_player
            copied_player.secrets.append(new_secret)
        for aura in filter(lambda a: isinstance(a, AuraUntil), self.player_auras):
            aura = copy.deepcopy(aura)
            aura.owner = copied_player.hero
            copied_player.add_aura(aura)
        for aura in filter(lambda a: isinstance(a, AuraUntil), self.object_auras):
            aura = copy.deepcopy(aura)
            aura.owner = copied_player.hero
            copied_player.add_aura(aura)
        copied_player.effect_count = dict()
        return copied_player

    def draw(self):
        if self.can_draw():
            card = self.deck.draw(self.game)
            self.trigger("card_drawn", card)
            if len(self.hand) < 10:
                self.hand.append(card)
                card.attach(card, self)
                card.trigger("drawn")
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
        card.unattach()
        self.deck.put_back(card)
        self.trigger("card_put_back", card)

    def discard(self):
        if len(self.hand) > 0:
            targets = self.hand
            target = self.game.random_choice(targets)
            self.hand.remove(target)
            self.trigger("card_discarded", target)

    def add_effect(self, effect):
        def remove_effect(*args):
            effect.unapply()
            self.effects.remove(effect)
            effect.event.unbind(self.hero, remove_effect)
        self.effects.append(effect)
        effect.set_owner(self.hero)
        effect.apply()
        effect.event.bind(self.hero, remove_effect)

    def add_aura(self, aura):
        if isinstance(aura.selector, hearthbreaker.tags.selector.PlayerSelector):
            self.player_auras.append(aura)
        else:
            self.object_auras.append(aura)
        if not aura.owner:
            aura.set_owner(self.hero)
        aura.apply()

    def remove_aura(self, aura):
        if isinstance(aura.selector, hearthbreaker.tags.selector.PlayerSelector):
            self.player_auras = [au for au in filter(lambda a: a is not aura, self.player_auras)]
        else:
            for an_aura in self.object_auras:
                if an_aura.eq(aura):
                    self.object_auras.remove(an_aura)
                    aura = an_aura
                    break
        aura.unapply()

    def choose_target(self, targets):
        return self.agent.choose_target(targets)

    def is_valid(self):
        return True

    def __to_json__(self):
        auras = copy.copy(self.player_auras)
        auras.extend(self.object_auras)
        return {
            'hero': self.hero,
            'deck': self.deck,
            'graveyard': [card for card in self.graveyard],
            'hand': self.hand,
            'secrets': [secret.name for secret in self.secrets],
            'effects': self.effects,
            'auras': [aura for aura in filter(lambda a: isinstance(a, AuraUntil), auras)],
            'minions': self.minions,
            'mana': self.mana,
            'max_mana': self.max_mana,
            'name': self.name,
        }

    @classmethod
    def __from_json__(cls, pd, game, agent):
        deck = Deck.__from__to_json__(pd["deck"],
                                      hero_from_name(pd["hero"]["name"]))
        player = Player("whatever", deck, agent, game)
        hero = Hero.__from_json__(pd["hero"], player)
        player.hero = hero
        hero.player = player
        if hero.weapon:
            hero.weapon.player = player
        player.mana = pd["mana"]
        player.max_mana = pd["max_mana"]
        player.name = pd['name']
        player.hand = []
        for card_def in pd['hand']:
            card = card_lookup(card_def['name'])
            card.__from_json__(card, **card_def)
            card.attach(card, player)
            player.hand.append(card)
        player.graveyard = set()
        for card_name in pd["graveyard"]:
            player.graveyard.add(card_name)

        player.secrets = []
        for secret_name in pd["secrets"]:
            secret = card_lookup(secret_name)
            secret.player = player
            player.secrets.append(secret)
        i = 0
        player.minions = []
        for md in pd["minions"]:
            minion = Minion.__from_json__(md, player, game)
            minion.index = i
            player.minions.append(minion)
            i += 1
        return player


class Deck:
    def __init__(self, cards, hero):
        if len(cards) != 30:
            raise GameException("Deck must have exactly 30 cards in it")
        self.cards = cards
        self.hero = hero
        for card in cards:
            card.drawn = False
        self.left = 30

    def copy(self):
        def copy_card(card):
            new_card = type(card)()
            new_card.drawn = card.drawn
            return new_card
        new_deck = Deck.__new__(Deck)
        new_deck.cards = [copy_card(card) for card in self.cards]
        new_deck.hero = self.hero
        new_deck.left = self.left
        return new_deck

    def can_draw(self):
        return self.left > 0

    def draw(self, game):
        if not self.can_draw():
            raise GameException("Cannot draw more than 30 cards")
        card = game.random_draw(self.cards, lambda c: not c.drawn)
        card.drawn = True
        self.left -= 1
        return card

    def put_back(self, card):
        for deck_card in self.cards:
            if deck_card == card:
                if not card.drawn:
                    raise GameException("Tried to put back a card that hadn't been used yet")
                deck_card.drawn = False
                self.left += 1
                return
        self.cards.append(card)
        self.left += 1

    def __to_json__(self):
        card_list = []
        for card in self.cards:
            card_list.append({
                'name': card.name,
                'used': card.drawn
            })
        return card_list

    @classmethod
    def __from__to_json__(cls, dd, hero):
        cards = []
        used = []
        left = 30
        for entry in dd:
            card = card_lookup(entry["name"])
            card.drawn = entry["used"]
            cards.append(card)
            used.append(entry["used"])
            if entry["used"]:
                left -= 1
        deck = Deck.__new__(Deck)
        deck.cards = cards
        deck.used = used
        deck.left = left
        deck.hero = hero
        return deck


__create_card_table()
