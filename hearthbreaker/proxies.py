

class ProxyCharacter:
    def __init__(self, character_ref):
        if type(character_ref) is str:
            if character_ref.find(":") > -1:
                [self.player_ref, self.minion_ref] = character_ref.split(':')
                self.minion_ref = int(self.minion_ref)
            else:
                self.player_ref = character_ref
                self.minion_ref = None
        elif character_ref.is_hero():
            if character_ref == character_ref.player.game.players[0].hero:
                self.player_ref = "p1"
            else:
                self.player_ref = "p2"
            self.minion_ref = None
        elif character_ref.is_minion():
            if character_ref.player == character_ref.game.players[0]:
                self.player_ref = "p1"
            else:
                self.player_ref = "p2"
            self.minion_ref = character_ref.index

    def resolve(self, game):
        if self.player_ref == "p1":
            char = game.players[0].hero
        else:
            char = game.players[1].hero
        if self.minion_ref is not None:
            if self.minion_ref == -1:
                return None
            if self.player_ref == "p1":
                char = game.players[0].minions[self.minion_ref]
            else:
                char = game.players[1].minions[self.minion_ref]

        return char

    def __str__(self):
        if self.minion_ref is not None:
            return "{0}:{1}".format(self.player_ref, self.minion_ref)
        return self.player_ref

    def to_output(self):
        return str(self)

    def __to_json__(self):
        if self.minion_ref is not None:
            return {
                'player': self.player_ref,
                'minion': self.minion_ref
            }
        else:
            return {
                'player': self.player_ref
            }

    @staticmethod
    def from_json(player, minion=None):
        rval = ProxyCharacter.__new__(ProxyCharacter)
        rval.player_ref = player
        rval.minion_ref = minion
        return rval


class ProxyCard:
    def __init__(self, card_reference):
        self.option = None
        if isinstance(card_reference, str):
            if str.find(card_reference, ":") > -1:
                card_arr = str.split(card_reference, ":")
                self.card_ref = int(card_arr[0])
                self.option = int(card_arr[1])
            else:
                self.card_ref = int(card_reference)
        else:
            self.card_ref = card_reference
        self.targetable = False

    def set_option(self, option):
        self.option = option

    def resolve(self, game):
        if self.option is not None:
            game.current_player.agent.next_option = int(self.option)
        return game.current_player.hand[int(self.card_ref)]

    def __str__(self):
        if self.option is not None:
            return str(self.card_ref) + ':' + str(self.option)
        return str(self.card_ref)

    def to_output(self):
        return str(self)

    def __to_json__(self):
        if self.option is not None:
            return {
                'card_index': self.card_ref,
                'option': self.option
            }
        else:
            return {
                'card_index': self.card_ref
            }

    @staticmethod
    def from_json(card_index, option=None):
        rval = ProxyCard(card_index)
        rval.set_option(option)
        return rval
