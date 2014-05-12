import copy
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY
from hsgame.game_objects import Card, Minion, MinionCard, SecretCard
import hsgame.targetting
__author__ = 'Daniel'


class ArcaneMissiles(Card):
    def __init__(self):
        super().__init__("Arcane Missiles", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE, False)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, 3 + player.spell_power):
            targets = game.other_player.minions.copy()
            targets.append(game.other_player)
            target = targets[game.random(0, len(targets) -1)]
            target.spell_damage(1, self)


class IceLance(Card):
    def __init__(self):
        super().__init__("Ice Lance", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON, True, hsgame.targetting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if self.target.frozen:
            self.target.spell_damage(4, self)
        else:
            self.target.freeze()


class MirrorImage(Card):
    def __init__(self):
        super().__init__("Mirror Image", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON, False)

    def use(self, player, game):
        super().use(player, game)
        class MirrorImageMinion(MinionCard):
            def __init__(self):
                super().__init__("Mirror Image", 0, CHARACTER_CLASS.MAGE, CARD_RARITY.SPECIAL, False)

            def create_minion(self, player):
                minion = Minion(0, 2)
                minion.taunt = True
                return minion

        minion1 = Minion(0, 2)
        minion2 = Minion(0, 2)
        minion1.taunt = True
        minion2.taunt = True
        minion1.add_to_board(MirrorImageMinion(), game, player, 0)
        minion2.add_to_board(MirrorImageMinion(), game, player, 0)


class ArcaneExplosion(Card):
    def __init__(self):
        super().__init__("Arcane Explosion", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE, False)

    def use(self, player, game):
        super().use(player, game)
        for minion in game.other_player.minions.copy():
            minion.spell_damage(1 + player.spell_power, self)


class Frostbolt(Card):
    def __init__(self):
        super().__init__("Frostbolt", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE, True, hsgame.targetting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.spell_damage(3 + player.spell_power, self)
        self.target.freeze()


class ArcaneIntellect(Card):
    def __init__(self):
        super().__init__("Arcane Intellect", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE, False)

    def use(self, player, game):
        super().use(player, game)
        for c in range(0, 2):
            player.draw()


class FrostNova(Card):
    def __init__(self):
        super().__init__("Frost Nova", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE, False)

    def use(self, player, game):
        super().use(player, game)
        for minion in game.other_player.minions:
            minion.freeze()


class Counterspell(SecretCard):
    def __init__(self):
        super().__init__("Counterspell", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)

    def reveal(self, card):
        card.cancel = True
        super().reveal()

    def activate(self, player):
        player.game.current_player.bind_once("spell_cast", self.reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("spell_cast", self.reveal)


class IceBarrier(SecretCard):
    def __init__(self):
        super().__init__("Ice Barrier", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def reveal(self, attacker, player):
        player.armour += 8
        super().reveal()

    def activate(self, player):
        player.bind_once("attacked", self.reveal, player)

    def deactivate(self, player):
        player.unbind("attacked", self.reveal)


class MirrorEntity(SecretCard):
    def __init__(self):
        super().__init__("Mirror Entity", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def reveal(self, minion, player):
        if minion.player is not player:
            mirror = copy.copy(minion)
            mirror.player = player
            mirror.card = copy.copy(minion.card)
            player.minions.append(mirror)
            player.game.trigger("minion_added", mirror)
            super().reveal()
        else:
            player.game.bind_once("minion_added", self.reveal, player)

    def activate(self, player):
        player.game.bind_once("minion_added", self.reveal, player)

    def deactivate(self, player):
        player.game.unbind("minion_added", self.reveal)


class Spellbender(SecretCard):
    def __init__(self):
        super().__init__("Spellbender", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC)

    def reveal(self, card, player):
        if card.targetable:
            class SpellbenderMinion(MinionCard):
                    def __init__(self):
                        super().__init__("Spellbender", 0, CHARACTER_CLASS.MAGE, CARD_RARITY.SPECIAL)

                    @staticmethod
                    def create_minion(player):
                        return Minion(1, 3)

            def choose_bender(targets):
                minion = SpellbenderMinion.create_minion(player)
                minion.add_to_board(self, player.game, player, 0)
                player.game.current_player.agent.choose_target = old_target
                return minion

            old_target = player.game.current_player.agent.choose_target
            player.game.current_player.agent.choose_target = choose_bender
            super().reveal()
        else:
            self.activate(player)

    def activate(self, player):
        player.game.current_player.bind_once("spell_cast", self.reveal, player)

    def deactivate(self, player):
        player.game.current_player.unbind("spell_cast", self.reveal)
