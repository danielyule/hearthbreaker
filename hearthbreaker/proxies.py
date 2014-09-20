import hearthbreaker.game_objects


class ProxyCharacter:
    def __init__(self, character_ref):
        if type(character_ref) is str:
            if character_ref.find(":") > -1:
                [self.player_ref, self.minion_ref] = character_ref.split(':')
                self.minion_ref = int(self.minion_ref)
            else:
                self.player_ref = character_ref
                self.minion_ref = None
        elif type(character_ref) is hearthbreaker.game_objects.Hero:
            if character_ref == character_ref.player.game.players[0].hero:
                self.player_ref = "p1"
            else:
                self.player_ref = "p2"
            self.minion_ref = None
        elif type(character_ref) is hearthbreaker.game_objects.Minion:
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


class TrackingProxyCharacter(ProxyCharacter):
    def __init__(self, character_ref, game):
        super().__init__(character_ref)
        if self.minion_ref is not None:
            if self.player_ref == "p1":
                player = game.players[0]
            else:
                player = game.players[1]
            player.bind("minion_played", self.__minion_added)
            player.bind("minion_removed", self.__minion_removed)

    def __minion_added(self, minion):
        if minion.index < self.minion_ref:
            self.minion_ref += 1

    def __minion_removed(self, minion):
        if minion.index == self.minion_ref:
            self.minion_ref = -1
            minion.player.unbind("minion_played", self.__minion_added)
            minion.player.unbind("minion_removed", self.__minion_removed)
        elif minion.index < self.minion_ref:
            self.minion_ref -= 1


class ProxyCard:
    def __init__(self, card_reference, game=None):
        self.card_ref = -1
        if isinstance(card_reference, str):
            self.card_ref = card_reference
        else:
            self.card_ref = str(card_reference)

        self.targetable = False

    def set_option(self, option):
        self.card_ref = ":" + str(option)

    def resolve(self, game):
        ref = self.card_ref.split(':')
        if len(ref) > 1:
            game.current_player.agent.next_option = int(ref[1])
        return game.current_player.hand[int(ref[0])]

    def __str__(self):
        return str(self.card_ref)

    def to_output(self):
        return str(self)
