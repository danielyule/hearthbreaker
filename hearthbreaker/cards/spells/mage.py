import copy
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Card, Minion, MinionCard, SecretCard, Hero
from hearthbreaker.tags.base import BuffUntil
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import CurrentPlayer
from hearthbreaker.tags.status import Immune
import hearthbreaker.targeting


class ArcaneMissiles(Card):
    def __init__(self):
        super().__init__("Arcane Missiles", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, player.effective_spell_damage(3)):
            targets = copy.copy(game.other_player.minions)
            targets.append(game.other_player.hero)
            target = game.random_choice(targets)
            target.damage(1, self)


class IceLance(Card):
    def __init__(self):
        super().__init__("Ice Lance", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if self.target.frozen:
            self.target.damage(4, self)
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
            mirror_image.summon(player, game, len(player.minions))


class ArcaneExplosion(Card):
    def __init__(self):
        super().__init__("Arcane Explosion", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(1), self)


class Frostbolt(Card):
    def __init__(self):
        super().__init__("Frostbolt", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(3), self)
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
        super().__init__("Frost Nova", 3, CHARACTER_CLASS.MAGE,
                         CARD_RARITY.COMMON)

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
        player.game.current_player.bind("spell_cast", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("spell_cast", self._reveal)


class IceBarrier(SecretCard):
    def __init__(self):
        super().__init__("Ice Barrier", 3, CHARACTER_CLASS.MAGE,
                         CARD_RARITY.COMMON)

    def _reveal(self, attacker, target):
        if target is self.player.hero and not attacker.removed:
            attacker.player.game.other_player.hero.armor += 8
            super().reveal()

    def activate(self, player):
        player.opponent.bind("attack", self._reveal)

    def deactivate(self, player):
        player.opponent.unbind("attack", self._reveal)


class MirrorEntity(SecretCard):
    def __init__(self):
        super().__init__("Mirror Entity", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)
        self.player = None

    def _reveal(self, minion):
        mirror = minion.copy(self.player)
        mirror.add_to_board(len(self.player.minions))
        super().reveal()

    def activate(self, player):
        player.game.current_player.bind("minion_played", self._reveal)
        self.player = player

    def deactivate(self, player):
        player.game.current_player.unbind("minion_played", self._reveal)
        self.player = None


class Spellbender(SecretCard):
    def __init__(self):
        super().__init__("Spellbender", 3, CHARACTER_CLASS.MAGE,
                         CARD_RARITY.EPIC)
        self.player = None

    def _reveal(self, card):
        if len(self.player.minions) < 7 and isinstance(card.target, Minion):
            class SpellbenderMinion(MinionCard):
                def __init__(self):
                    super().__init__("Spellbender", 0, CHARACTER_CLASS.MAGE, CARD_RARITY.SPECIAL)

                def create_minion(self, p):
                    return Minion(1, 3)

            spell_bender = SpellbenderMinion()
            # According to http://us.battle.net/hearthstone/en/forum/topic/10070927066, Spellbender
            # will not activate if there are too many minions
            spell_bender.summon(self.player, self.player.game, len(self.player.minions))
            card.target = self.player.minions[-1]
            super().reveal()

    def activate(self, player):
        player.game.current_player.bind("spell_cast", self._reveal)
        self.player = player

    def deactivate(self, player):
        player.game.current_player.unbind("spell_cast", self._reveal)
        self.player = None


class Vaporize(SecretCard):
    def __init__(self):
        super().__init__("Vaporize", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def _reveal(self, attacker, target):
        if target is self.player.hero and type(attacker) is Minion and not attacker.removed:
            attacker.die(self)
            attacker.game.check_delayed()
            super().reveal()

    def activate(self, player):
        player.opponent.bind("attack", self._reveal)

    def deactivate(self, player):
        player.opponent.unbind("attack", self._reveal)


class IceBlock(SecretCard):
    def __init__(self):
        super().__init__("Ice Block", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC)
        self.player = None

    def _reveal(self, character, attacker, amount):
        if isinstance(character, Hero):
            if character.health - amount <= 0:
                character.add_buff(BuffUntil(Immune(), TurnEnded(player=CurrentPlayer())))
                # TODO Check if this spell will also prevent damage to armor.
                super().reveal()

    def activate(self, player):
        player.bind("pre_damage", self._reveal)

    def deactivate(self, player):
        player.unbind("pre_damage", self._reveal)


class ConeOfCold(Card):
    def __init__(self):
        super().__init__("Cone of Cold", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.freeze()
        index = self.target.index

        if self.target.index < len(self.target.player.minions) - 1:
            minion = self.target.player.minions[index + 1]
            minion.damage(player.effective_spell_damage(1), self)
            minion.freeze()

        self.target.damage(player.effective_spell_damage(1), self)

        if self.target.index > 0:
            minion = self.target.player.minions[index - 1]
            minion.damage(player.effective_spell_damage(1), self)
            minion.freeze()


class Fireball(Card):
    def __init__(self):
        super().__init__("Fireball", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(6), self)


class Polymorph(Card):
    def __init__(self):
        super().__init__("Polymorph", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        class Sheep(MinionCard):
            def __init__(self):
                super().__init__("Sheep", 0, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

            def create_minion(self, p):
                return Minion(1, 1)

        sheep = Sheep()
        minion = sheep.create_minion(None)
        minion.card = sheep
        self.target.replace(minion)


class Blizzard(Card):
    def __init__(self):
        super().__init__("Blizzard", 6, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(2), self)
            minion.freeze()


class Flamestrike(Card):
    def __init__(self):
        super().__init__("Flamestrike", 7, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(4), self)


class Pyroblast(Card):
    def __init__(self):
        super().__init__("Pyroblast", 10, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC,
                         hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(10), self)


class Duplicate(SecretCard):
    def __init__(self):
        super().__init__("Duplicate", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)
        self.player = None

    def activate(self, player):
        player.bind("minion_died", self._reveal)
        self.player = player

    def deactivate(self, player):
        player.unbind("minion_died", self._reveal)
        self.player = None

    def _reveal(self, minion, by):
        for c in range(0, 2):
            if len(self.player.hand) < 10:
                self.player.hand.append(type(minion.card)())
        super().reveal()
