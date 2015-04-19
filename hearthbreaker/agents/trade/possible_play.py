from hearthbreaker.agents.trade.util import Util
from functools import reduce


class PossiblePlay:
    def __init__(self, cards, available_mana):
        if len(cards) == 0:
            raise Exception("PossiblePlay cards is empty")

        self.cards = cards
        self.available_mana = available_mana

    def card_mana(self):
        def eff_mana(card):
            if card.name == "The Coin":
                return -1
            else:
                return card.mana_cost()

        return reduce(lambda s, c: s + eff_mana(c), self.cards, 0)

    def sorted_mana(self):
        return Util.reverse_sorted(map(lambda c: c.mana_cost(), self.cards))

    def wasted(self):
        return self.available_mana - self.card_mana()

    def value(self):
        res = self.card_mana()
        wasted = self.wasted()
        if wasted < 0:
            raise Exception("Too Much Mana")

        res += wasted * -100000000000

        factor = 100000000
        for card_mana in self.sorted_mana():
            res += card_mana * factor
            factor = factor / 10

        if self.has_hero_power() and self.available_mana < 6:
            res -= 10000000000000000

        if any(map(lambda c: c.name == "The Coin", self.cards)):
            res -= 100

        return res

    def has_hero_power(self):
        for card in self.cards:
            if card.name == 'Hero Power':
                return True
        return False

    def first_card(self):
        if self.has_hero_power():
            for card in self.cards:
                if card.name == 'Hero Power':
                    return card
            raise Exception("bad")
        else:
            return self.cards[0]

    def __str__(self):
        names = [c.name for c in self.cards]
        s = str(names)
        return "{} {}".format(s, self.value())


class CoinPlays:
    def coin(self):
        cards = [c for c in filter(lambda c: c.name == 'The Coin', self.cards)]
        return cards[0]

    def raw_plays_with_coin(self):
        res = []
        if self.has_coin():
            coinPlays = self.after_coin().raw_plays()

            for play in coinPlays:
                cards = [self.coin()] + play
                res.append(cards)

        return res

    def raw_plays(self):
        res = []
        for play in self.raw_plays_without_coin():
            res.append(play)

        for play in self.raw_plays_with_coin():
            res.append(play)

        return res

    def has_coin(self):
        return any(map(lambda c: c.name == "The Coin", self.cards))

    def cards_without_coin(self):
        return Util.filter_out_one(self.cards, lambda c: c.name == "The Coin")

    def after_coin(self):
        return PossiblePlays(self.cards_without_coin(), self.mana + 1)

    def without_coin(self):
        return PossiblePlays(self.cards_without_coin(), self.mana)


class HeroPowerCard:
    def __init__(self):
        self.mana = 2
        self.name = "Hero Power"
        self.player = None

    def can_use(self, player, game):
        return True

    def mana_cost(self):
        return 2


class PossiblePlays(CoinPlays):
    def __init__(self, cards, mana, allow_hero_power=True):
        self.cards = cards
        self.mana = mana
        self.allow_hero_power = allow_hero_power

    def possible_is_pointless_coin(self, possible):
        if len(possible) != 1 or possible[0].name != "The Coin":
            return False

        cards_playable_after_coin = [card for card in filter(lambda c: c.mana - 1 == self.mana, self.cards)]
        return len(cards_playable_after_coin) == 0

    def raw_plays_without_coin(self):
        res = []

        def valid_card(card):
            saved_mana = card.player.mana
            card.player.mana = self.mana
            usable = card.can_use(card.player, card.player.game)
            card.player.mana = saved_mana
            return usable

        possible = [card for card in
                    filter(valid_card, self.cards)]

        if self.possible_is_pointless_coin(possible):
            possible = []

        if self.mana >= 2 and self.allow_hero_power:
            possible.append(HeroPowerCard())

        if len(possible) == 0:
            return [[]]

        for card in possible:
            rest = self.cards[0:99999]

            if card.name == 'Hero Power':
                f_plays = PossiblePlays(rest,
                                        self.mana - card.mana_cost(),
                                        allow_hero_power=False).raw_plays()
            else:
                rest.remove(card)
                f_plays = PossiblePlays(rest,
                                        self.mana - card.mana_cost(),
                                        allow_hero_power=self.allow_hero_power).raw_plays()

            for following_play in f_plays:
                combined = [card] + following_play
                res.append(combined)

        res = Util.uniq_by_sorted(res)

        return res

    def plays_inner(self):
        res = [PossiblePlay(raw, self.mana) for raw in self.raw_plays() if len(raw) > 0]
        res = sorted(res, key=PossiblePlay.value)
        res.reverse()

        return res

    def plays(self):
        return self.plays_inner()

    def __str__(self):
        res = []
        for play in self.plays():
            res.append(play.__str__())
        return str.join("\n", res)


class PlayMixin:
    def play_one_card(self, player):
        if len(player.minions) == 7:
            return
        if player.game.game_ended:
            return

        allow_hero_power = (not player.hero.power.used) and player.hero.health > 2
        plays = PossiblePlays(player.hand, player.mana, allow_hero_power=allow_hero_power).plays()

        if len(plays) > 0:
            play = plays[0]
            if len(play.cards) == 0:
                raise Exception("play has no cards")

            card = play.first_card()

            if card.name == 'Hero Power':
                player.hero.power.use()
            else:
                self.last_card_played = card
                player.game.play_card(card)

            return card

    def play_cards(self, player):
        card = self.play_one_card(player)
        if card:
            self.play_cards(player)
