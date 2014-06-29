import copy
import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import Card, Minion, MinionCard
from hsgame.cards.minions.warlock import VoidWalker, FlameImp, DreadInfernal, \
    Succubus, Felguard

__author__ = 'randomflyingtaco'


class MortalCoil(Card):
    def __init__(self):
        super().__init__("Mortal Coil", 1, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.COMMON,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        if self.target.health <= player.effective_spell_damage(1):
            self.target.damage(player.effective_spell_damage(1), self)
            player.draw()
        else:
            self.target.damage(player.effective_spell_damage(1), self)
            # not sure how necessary this is, making sure damage before
            # draw but need to compare health before dealing damage


class Hellfire(Card):
    def __init__(self):
        super().__init__("Hellfire", 4, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        targets = game.other_player.minions.copy()
        targets.extend(game.current_player.minions)
        targets.append(game.other_player.hero)
        targets.append(game.current_player.hero)
        for minion in targets:
            minion.damage(player.effective_spell_damage(3), self)


class ShadowBolt(Card):
    def __init__(self):
        super().__init__("Shadow Bolt", 3, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.FREE,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(4), self)


class DrainLife(Card):
    def __init__(self):
        super().__init__("Drain Life", 3, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.FREE, hsgame.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(2), self)
        player.hero.heal(player.effective_heal_power(2))


class Soulfire(Card):
    def __init__(self):
        super().__init__("Soulfire", 0, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.COMMON,
                         hsgame.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(4), self)
        player.discard()


class TwistingNether(Card):
    def __init__(self):
        super().__init__("Twisting Nether", 8, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)
        targets = game.other_player.minions.copy()
        targets.extend(game.current_player.minions)
        for minion in targets:
            minion.die(self)


class Demonfire(Card):
    def __init__(self):
        super().__init__("Demonfire", 2, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.COMMON,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if isinstance(self.target, Minion) and self.target.type is MINION_TYPE.DEMON:
            self.target.change_attack(2)
            self.target.increase_health(2)
        else:
            self.target.damage(player.effective_spell_damage(2), self)
            """
            Jaraxxus is a minion
            class LordJaraxxus(Card):
              def __init__(self):
                 super().__init__("Lord Jaraxxus", 9, CHARACTER_CLASS.WARLOCK, CARD_RARITY.LEGENDARY)

            def use(self, player, game):
              super().use(player, game)
            #self.hero.max_health = 15
            self.hero.health = 15
            player.hero.power = hsgame.powers.JaraxxusPower(player.hero)
            """
            # weapons not in yet, need to give 3/8 Blood Fury


class SacrificialPact(Card):
    def __init__(self):
        super().__init__("Sacrificial Pact", 0, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.COMMON,
                         hsgame.targeting.find_minion_spell_target,
                         lambda minion: minion.minion_type is MINION_TYPE.DEMON)

    def use(self, player, game):
        super().use(player, game)
        self.target.die(self)
        player.hero.heal(player.effective_heal_power(5))


class SiphonSoul(Card):
    def __init__(self):
        super().__init__("Siphon Soul", 6, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.RARE,
                         hsgame.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.die(self)
        player.hero.heal(player.effective_heal_power(3))


class SenseDemons(Card):
    def __init__(self):
        super().__init__("Sense Demons", 3, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        class WorthlessImp(MinionCard):
            def __init__(self):
                super().__init__("Worthless Imp", 1, CHARACTER_CLASS.WARLOCK,
                                 CARD_RARITY.SPECIAL)

            def create_minion(self, p):
                minion = Minion(1, 1, MINION_TYPE.DEMON)
                return minion

        minions = []

        for index in range(0, 30):
            if not game.current_player.deck.used[index] and not game.current_player.deck.cards[index].is_spell():
                # and minion.minion_type is MINION_TYPE.DEMON:
                # I know this won't work, but how do I pull type info from the
                # deck of cards
                minions.append(game.other_player.deck.cards[index])

        if len(minions) == 1:
            minions.append(WorthlessImp())
        if len(minions) == 0:
            minions.append(WorthlessImp())
            minions.append(WorthlessImp())

        for i in range(0, 2):
            rand = game.random(0, len(minions) - 1)
            card = copy.copy(minions.pop(rand))
            # can i have triggers here?  how do i command specific draws
            self.trigger("card_drawn", card)
            if len(player.hand) < 10:
                player.hand.append(card)
            else:
                player.trigger("card_destroyed", card)


class BaneofDoom(Card):
    def __init__(self):
        super().__init__("Bane of Doom", 5, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.EPIC,
                         hsgame.targeting.find_spell_target)

    def use(self, player, game):
        demon_list = [VoidWalker(), FlameImp, DreadInfernal(), Succubus(),
                      Felguard()]
        card = copy.copy(demon_list[game.random(0, len(demon_list) - 1)])
        if self.target.health <= player.effective_spell_damage(2):
            self.target.damage(player.effective_spell_damage(2), self)
            self.target.create_minion(player).add_to_board(card, game, player,
                                                           0)
        else:
            self.target.damage(player.effective_spell_damage(2), self)


class Shadowflame(Card):
    def __init__(self):
        super().__init__("Shadowflame", 4, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.RARE,
                         hsgame.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        shadowflame_damage = self.target.attack_power + self.target.temp_attack
        targets = game.other_player.minions.copy()
        self.target.die(self)
        for minion in targets:
            minion.damage(player.effective_spell_damage(shadowflame_damage),
                          self)


class Corruption(Card):
    def __init__(self):
        super().__init__("Corruption", 1, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.COMMON,
                         hsgame.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        def remove_minion(p):
            game.remove_minion(self.target, self.target.player)

        player.bind_once("turn_started", remove_minion)
        self.target.bind_once("silenced",
                              lambda minion: player.unbind("turn_started",
                                                           remove_minion))


class PowerOverwhelming(Card):
    def __init__(self):
        super().__init__("Power Overwhelming", 1, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.COMMON,
                         hsgame.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        def remove_minion(p):
            game.remove_minion(self.target, self.target.player)
        player.bind_once("turn_ended", remove_minion)
        self.target.bind_once("silenced",
                              lambda minion: player.unbind("turn_ended",
                                                           remove_minion))
        self.target.change_attack(4)
        self.target.increase_health(4)
