import copy
from hearthbreaker.cards.base import SecretCard, SpellCard
from hearthbreaker.cards.minions.mage import SpellbenderMinion, MirrorImageMinion
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY
from hearthbreaker.tags.base import BuffUntil, Buff
from hearthbreaker.tags.card_source import CollectionSource
from hearthbreaker.tags.condition import IsMinion
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.selector import CurrentPlayer, Count, DeadMinionSelector, BothPlayer
from hearthbreaker.tags.status import Immune, Frozen, ManaChange
import hearthbreaker.targeting


class ArcaneMissiles(SpellCard):
    def __init__(self):
        super().__init__("Arcane Missiles", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, player.effective_spell_damage(3)):
            targets = copy.copy(game.other_player.minions)
            targets.append(game.other_player.hero)
            target = game.random_choice(targets)
            target.damage(1, self)


class IceLance(SpellCard):
    def __init__(self):
        super().__init__("Ice Lance", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if self.target.frozen:
            self.target.damage(4, self)
        else:
            self.target.add_buff(Buff(Frozen()))


class MirrorImage(SpellCard):
    def __init__(self):
        super().__init__("Mirror Image", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, 2):
            MirrorImageMinion().summon(player, game, len(player.minions))

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


class ArcaneExplosion(SpellCard):
    def __init__(self):
        super().__init__("Arcane Explosion", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(1), self)


class Frostbolt(SpellCard):
    def __init__(self):
        super().__init__("Frostbolt", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(3), self)
        self.target.add_buff(Buff(Frozen()))


class ArcaneIntellect(SpellCard):
    def __init__(self):
        super().__init__("Arcane Intellect", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        for c in range(0, 2):
            player.draw()


class FrostNova(SpellCard):
    def __init__(self):
        super().__init__("Frost Nova", 3, CHARACTER_CLASS.MAGE,
                         CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for minion in game.other_player.minions:
            minion.add_buff(Buff(Frozen()))


class Counterspell(SecretCard):
    def __init__(self):
        super().__init__("Counterspell", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)

    def _reveal(self, card, index):
        if card.is_spell():
            card.cancel = True
            super().reveal()

    def activate(self, player):
        player.game.current_player.bind("card_played", self._reveal)

    def deactivate(self, player):
        player.game.current_player.unbind("card_played", self._reveal)


class IceBarrier(SecretCard):
    def __init__(self):
        super().__init__("Ice Barrier", 3, CHARACTER_CLASS.MAGE,
                         CARD_RARITY.COMMON)

    def _reveal(self, attacker, target):
        if target is self.player.hero and not attacker.removed:
            attacker.player.game.other_player.hero.armor += 8
            super().reveal()

    def activate(self, player):
        player.opponent.bind("character_attack", self._reveal)

    def deactivate(self, player):
        player.opponent.unbind("character_attack", self._reveal)


class MirrorEntity(SecretCard):
    def __init__(self):
        super().__init__("Mirror Entity", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)
        self.player = None

    def _reveal(self, minion):
        if len(self.player.minions) < 7:
            mirror = minion.copy(self.player)
            mirror.add_to_board(len(self.player.minions))
            minion.player.trigger("minion_summoned", mirror)
            minion.player.trigger("after_added", mirror)
            super().reveal()

    def activate(self, player):
        player.game.current_player.bind("minion_played", self._reveal)
        self.player = player

    def deactivate(self, player):
        player.game.current_player.unbind("minion_played", self._reveal)
        self.player = None


class Spellbender(SecretCard):
    def __init__(self):
        super().__init__("Spellbender", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC)
        self.player = None

    def _reveal(self, card, index):
        # According to http://us.battle.net/hearthstone/en/forum/topic/10070927066, Spellbender
        # will not activate if there are too many minions
        if card.is_spell() and len(self.player.minions) < 7 and card.target and card.target.is_minion():
            SpellbenderMinion().summon(self.player, self.player.game, len(self.player.minions))
            card.target = self.player.minions[-1]
            super().reveal()

    def activate(self, player):
        player.game.current_player.bind("card_played", self._reveal)
        self.player = player

    def deactivate(self, player):
        player.game.current_player.unbind("card_played", self._reveal)
        self.player = None


class Vaporize(SecretCard):
    def __init__(self):
        super().__init__("Vaporize", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def _reveal(self, attacker, target):
        if target is self.player.hero and attacker.is_minion() and not attacker.removed:
            attacker.die(self)
            attacker.game.check_delayed()
            super().reveal()

    def activate(self, player):
        player.opponent.bind("character_attack", self._reveal)

    def deactivate(self, player):
        player.opponent.unbind("character_attack", self._reveal)


class IceBlock(SecretCard):
    def __init__(self):
        super().__init__("Ice Block", 3, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC)
        self.player = None

    def _reveal(self, character, attacker, amount):
        if character.is_hero():
            if character.health - amount <= 0:
                character.add_buff(BuffUntil(Immune(), TurnEnded(player=CurrentPlayer())))
                # TODO Check if this spell will also prevent damage to armor.
                super().reveal()

    def activate(self, player):
        player.bind("pre_damage", self._reveal)

    def deactivate(self, player):
        player.unbind("pre_damage", self._reveal)


class ConeOfCold(SpellCard):
    def __init__(self):
        super().__init__("Cone of Cold", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.add_buff(Buff(Frozen()))
        index = self.target.index

        if self.target.index < len(self.target.player.minions) - 1:
            minion = self.target.player.minions[index + 1]
            minion.damage(player.effective_spell_damage(1), self)
            minion.add_buff(Buff(Frozen()))

        self.target.damage(player.effective_spell_damage(1), self)

        if self.target.index > 0:
            minion = self.target.player.minions[index - 1]
            minion.damage(player.effective_spell_damage(1), self)
            minion.add_buff(Buff(Frozen()))


class Fireball(SpellCard):
    def __init__(self):
        super().__init__("Fireball", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(6), self)


class Polymorph(SpellCard):
    def __init__(self):
        super().__init__("Polymorph", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        from hearthbreaker.cards.minions.mage import Sheep
        sheep = Sheep()
        minion = sheep.create_minion(None)
        minion.card = sheep
        self.target.replace(minion)


class Blizzard(SpellCard):
    def __init__(self):
        super().__init__("Blizzard", 6, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(2), self)
        for minion in game.other_player.minions:
            minion.add_buff(Buff(Frozen()))


class Flamestrike(SpellCard):
    def __init__(self):
        super().__init__("Flamestrike", 7, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(4), self)


class Pyroblast(SpellCard):
    def __init__(self):
        super().__init__("Pyroblast", 10, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC,
                         target_func=hearthbreaker.targeting.find_spell_target)

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
                new_card = type(minion.card)()
                self.player.hand.append(new_card)
                new_card.attach(new_card, self.player)
        super().reveal()


class Flamecannon(SpellCard):
    def __init__(self):
        super().__init__("Flamecannon", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        targets = hearthbreaker.targeting.find_enemy_minion_battlecry_target(player.game, lambda x: True)
        target = game.random_choice(targets)
        target.damage(player.effective_spell_damage(4), self)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 1


class EchoOfMedivh(SpellCard):
    def __init__(self):
        super().__init__("Echo of Medivh", 4, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)
        for minion in sorted(copy.copy(player.minions), key=lambda minion: minion.born):
            if len(player.hand) < 10:
                player.hand.append(minion.card)


class UnstablePortal(SpellCard):
    def __init__(self):
        super().__init__("Unstable Portal", 2, CHARACTER_CLASS.MAGE, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        query = CollectionSource([IsMinion()])
        new_minon = query.get_card(player, player, self)
        new_minon.add_buff(Buff(ManaChange(-3)))
        player.hand.append(new_minon)
        new_minon.attach(new_minon, player)


class DragonsBreath(SpellCard):
    def __init__(self):
        super().__init__("Dragon's Breath", 5, CHARACTER_CLASS.MAGE, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target,
                         buffs=[Buff(ManaChange(Count(DeadMinionSelector(players=BothPlayer())), -1))])

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(4), self)


class ArcaneBlast(SpellCard):
    def __init__(self):
        super().__init__("Arcane Blast", 1, CHARACTER_CLASS.MAGE, CARD_RARITY.EPIC,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(2 + player.spell_damage), self)
