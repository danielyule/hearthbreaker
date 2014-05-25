import copy
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import Card, Minion, MinionCard, SecretCard
import hsgame.targetting
__author__ = 'Daniel'


class ArcaneMissiles(Card):
    def __init__(self):
        super().__init__("Arcane Missiles", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, 3 + player.spell_power):
            targets = game.other_player.minions.copy()
            targets.append(game.other_player.hero)
            target = targets[game.random(0, len(targets) - 1)]
            target.spell_damage(1, self)


class IceLance(Card):
    def __init__(self):
        super().__init__("Ice Lance", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON,
                         hsgame.targetting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if self.target.frozen:
            self.target.spell_damage(4, self)
        else:
            self.target.freeze()


class MirrorImage(Card):
    def __init__(self):
        super().__init__("Mirror Image", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        class MirrorImageMinion(MinionCard):
            def __init__(self):
                super().__init__("Mirror Image", 0, CHARACTER_CLASS.MAGE, CARD_RARITY.SPECIAL)

            def create_minion(self, p):
                minion = Minion(0, 2)
                minion.taunt = True
                return minion
        for i in range(0, 2):
            mirror_image = MirrorImageMinion()
            mirror_image.create_minion(player).add_to_board(mirror_image, game, player, 0)


class ArcaneExplosion(Card):
    def __init__(self):
        super().__init__("Arcane Explosion", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        for minion in game.other_player.minions.copy():
            minion.spell_damage(1 + player.spell_power, self)


class Frostbolt(Card):
    def __init__(self):
        super().__init__("Frostbolt", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE,
                         hsgame.targetting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.spell_damage(3 + player.spell_power, self)
        self.target.freeze()


class ArcaneIntellect(Card):
    def __init__(self):
        super().__init__("Arcane Intellect", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        for c in range(0, 2):
            player.draw()


class FrostNova(Card):
    def __init__(self):
        super().__init__("Frost Nova", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        for minion in game.other_player.minions:
            minion.freeze()


class Counterspell(SecretCard):
    def __init__(self):
        super().__init__("Counterspell", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)

    def _reveal(self, card):
        card.cancel = True
        super().reveal()

    def activate(self, player):
        player.game.current_player.bind_once("spell_cast", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("spell_cast", self._reveal)


class IceBarrier(SecretCard):
    def __init__(self):
        super().__init__("Ice Barrier", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def _reveal(self, attacker, player):
        player.hero.armour += 8
        super().reveal()

    def activate(self, player):
        player.hero.bind_once("attacked", self._reveal, player)

    def deactivate(self, player):
        player.hero.unbind("attacked", self._reveal)


class MirrorEntity(SecretCard):
    def __init__(self):
        super().__init__("Mirror Entity", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def _reveal(self, minion, player):
        if minion.player is not player:
            mirror = copy.copy(minion)
            mirror.player = player
            mirror.card = copy.copy(minion.card)
            mirror.index = len(player.minions)
            player.minions.append(mirror)
            player.game.trigger("minion_added", mirror)
            super().reveal()
        else:
            self.activate(player)

    def activate(self, player):
        player.game.bind_once("minion_added", self._reveal, player)

    def deactivate(self, player):
        player.game.unbind("minion_added", self._reveal)


class Spellbender(SecretCard):
    def __init__(self):
        super().__init__("Spellbender", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC)

    def _reveal(self, card, player):
        if card.targetable:
            class SpellbenderMinion(MinionCard):
                def __init__(self):
                    super().__init__("Spellbender", 0, CHARACTER_CLASS.MAGE, CARD_RARITY.SPECIAL)

                def create_minion(self, p):
                    return Minion(1, 3)

            def choose_bender(targets):
                minion_card = SpellbenderMinion()
                minion = minion_card.create_minion(player)
                minion.add_to_board(minion_card, player.game, player, 0)
                player.game.current_player.agent.choose_target = old_target
                return minion

            old_target = player.game.current_player.agent.choose_target
            player.game.current_player.agent.choose_target = choose_bender
            super().reveal()
        else:
            self.activate(player)

    def activate(self, player):
        player.game.current_player.bind_once("spell_cast", self._reveal, player)

    def deactivate(self, player):
        player.game.current_player.unbind("spell_cast", self._reveal)


class Vaporize(SecretCard):
    def __init__(self):
        super().__init__("Vaporize", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def _reveal(self, attacker):
        if type(attacker) is Minion:
            attacker.die(self)
            super().reveal()
        else:
            self.activate(attacker.player.game.other_player)

    def activate(self, player):
        player.hero.bind_once("attacked", self._reveal)

    def deactivate(self, player):
        player.hero.unbind("attacked", self._reveal)


class IceBlock(SecretCard):
    def __init__(self):
        super().__init__("Ice Block", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC)

    def _reveal_if_fatal(self, amount, attacker, player):
        if player.hero.health - amount <= 0:
            player.hero.immune = True
            player.hero.health += amount
            #TODO Check if this spell will also prevent damage to armour.
            super().reveal()
            player.hero.unbind("secret_damaged", self._reveal_if_fatal)

    def activate(self, player):
        player.hero.bind("secret_damaged", self._reveal_if_fatal, player)

    def deactivate(self, player):
        player.hero.unbind("secret_damaged", self._reveal_if_fatal)


class ConeOfCold(Card):
    def __init__(self):
        super().__init__("Cone of Cold", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON,
                         hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.spell_damage(1 + player.spell_power, self)
        self.target.freeze()
        index = self.target.index
        if self.target.index > 0:
            self.target.player.minions[index - 1].spell_damage(1 + player.spell_power, self)
            self.target.player.minions[index - 1].freeze()

        if self.target.index < len(self.target.player.minions) - 1:
            self.target.player.minions[index + 1].spell_damage(1 + player.spell_power, self)
            self.target.player.minions[index + 1].freeze()


class Fireball(Card):
    def __init__(self):
        super().__init__("Fireball", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE,
                         hsgame.targetting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.spell_damage(6 + player.spell_power, self)


class Polymorph(Card):
    def __init__(self):
        super().__init__("Polymorph", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE,
                         hsgame.targetting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        class Sheep(MinionCard):
            def __init__(self):
                super().__init__("Sheep", 0, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL)

            def create_minion(self, p):
                return Minion(1, 1, MINION_TYPE.BEAST)

        sheep = Sheep()
        minion = sheep.create_minion(None)
        minion.index = self.target.index
        minion.card = sheep
        self.target.player.minions[minion.index] = minion


