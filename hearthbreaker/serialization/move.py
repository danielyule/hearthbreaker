import hearthbreaker.game_objects

__author__ = 'dyule'


class Move:
    def __init__(self):
        super().__init__()
        self.random_numbers = []

    def play(self, game):
        pass

    @staticmethod
    def from_json(name, random=[], **json):
        cls = None
        if name == 'play':
            cls = PlayMove
        elif name == 'attack':
            cls = AttackMove
        elif name == 'power':
            cls = PowerMove
        elif name == 'end':
            cls = TurnEndMove
        elif name == 'start':
            cls = TurnStartMove
        elif name == 'concede':
            cls = ConcedeMove

        obj = cls.__new__(cls)
        cls.__from_json__(obj, **json)
        obj.random_numbers = []
        for num in random:
            if isinstance(num, dict):
                obj.random_numbers.append(hearthbreaker.proxies.ProxyCharacter.from_json(**num))
            else:
                obj.random_numbers.append(num)
        return obj

    def __to_json__(self):
        pass

    def __update_json__(self, json):
        if len(self.random_numbers) > 0:
            json.update({
                'random': self.random_numbers
            })
        return json


class PlayMove(Move):
    def __init__(self, card, index=-1, target=None):
        super().__init__()
        self.card = card
        self.index = index
        if target is not None:
            self.target = hearthbreaker.proxies.ProxyCharacter(target)
        else:
            self.target = None

    def play(self, game):
        if self.target is not None:
            game.current_player.agent.next_target = self.target.resolve(game)

        game.current_player.agent.next_index = self.index
        game.play_card(self.card.resolve(game))
        game.current_player.agent.nextIndex = -1

    def to_output_string(self):
        if self.index > -1:
            if self.target is not None:
                return 'summon({0},{1},{2})'.format(self.card.to_output(), self.index, self.target.to_output())
            return 'summon({0},{1})'.format(self.card.to_output(), self.index)
        else:
            if self.target is not None:
                return 'play({0},{1})'.format(self.card.to_output(), self.target.to_output())
            return 'play({0})'.format(self.card.to_output())

    def __to_json__(self):
        if self.target is not None:
            if self.index > -1:
                json = {
                    'name': 'play',
                    'card': self.card,
                    'index': self.index,
                    'target': self.target,
                }
            else:
                json = {
                    'name': 'play',
                    'card': self.card,
                    'target': self.target,
                }
        else:
            if self.index > -1:
                json = {
                    'name': 'play',
                    'card': self.card,
                    'index': self.index,
                }
            else:
                json = {
                    'name': 'play',
                    'card': self.card,
                }
        return self.__update_json__(json)

    def __from_json__(self, card, index=-1, target=None):
        self.card = hearthbreaker.proxies.ProxyCard.from_json(**card)
        self.index = index
        if target:
            self.target = hearthbreaker.proxies.ProxyCharacter.from_json(**target)
        else:
            self.target = None


class AttackMove(Move):
    def __init__(self, character, target):
        super().__init__()
        self.character = hearthbreaker.proxies.ProxyCharacter(character)
        self.target = hearthbreaker.proxies.ProxyCharacter(target)

    def to_output_string(self):
        return 'attack({0},{1})'.format(self.character.to_output(), self.target.to_output())

    def play(self, game):
        game.current_player.agent.next_target = self.target.resolve(game)
        self.character.resolve(game).attack()
        game.current_player.agent.next_target = None

    def __to_json__(self):
        return self.__update_json__({
            'name': 'attack',
            'character': self.character,
            'target': self.target,
        })

    def __from_json__(self, character, target):
        self.character = hearthbreaker.proxies.ProxyCharacter.from_json(**character)
        self.target = hearthbreaker.proxies.ProxyCharacter.from_json(**target)


class PowerMove(Move):
    def __init__(self, target=None):
        super().__init__()
        self.target = target
        if target is not None:
            self.target = hearthbreaker.proxies.ProxyCharacter(target)
        else:
            self.target = None

    def to_output_string(self):
        if self.target is not None:
            return 'power({0})'.format(self.target.to_output())
        else:
            return 'power()'

    def play(self, game):
        if self.target is not None:
            game.current_player.agent.next_target = self.target.resolve(game)
        game.current_player.hero.power.use()
        game.current_player.agent.next_target = None

    def __to_json__(self):
        if self.target:
            json = {
                'name': 'power',
                'target': self.target,
            }
        else:
            json = {
                'name': 'power',
            }
        return self.__update_json__(json)

    def __from_json__(self, target=None):
        if target is not None:
            self.target = hearthbreaker.proxies.ProxyCharacter.from_json(**target)
        else:
            self.target = None


class TurnEndMove(Move):
    def __init__(self):
        super().__init__()
        pass

    def to_output_string(self):
        return 'end()'

    def play(self, game):
        pass

    def __to_json__(self):
        return self.__update_json__({
            'name': 'end',
        })

    def __from_json__(self):
        pass


class TurnStartMove(Move):
    def __init__(self):
        super().__init__()

    def to_output_string(self):
        return 'start()'

    def play(self, game):
        pass

    def __to_json__(self):
        return self.__update_json__({
            'name': 'start',
        })

    def __from_json__(self):
        pass


class ConcedeMove(Move):
    def __init__(self):
        super().__init__()

    def to_output_string(self):
        return "concede()"

    def play(self, game):
        game.current_player.hero.die(None)
        game.current_player.hero.activate_delayed()

    def __to_json__(self):
        return self.__update_json__({
            'name': 'concede',
        })

    def __from_json__(self):
        pass
