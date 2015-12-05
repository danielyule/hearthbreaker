import copy
from hearthbreaker.cards.base import SpellCard
from hearthbreaker.game_objects import Minion
from hearthbreaker.tags.action import Kill, Damage
from hearthbreaker.tags.base import Effect, ActionTag
from hearthbreaker.tags.card_source import CollectionSource
from hearthbreaker.tags.condition import IsType, MinionIsTarget
from hearthbreaker.tags.event import TurnStarted, TurnEnded, CardDiscarded
from hearthbreaker.tags.selector import SelfSelector, EnemyPlayer, CharacterSelector, RandomPicker
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.cards.minions.warlock import Imp


class MortalCoil(SpellCard):
    def __init__(self):
        super().__init__("Mortal Coil", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if self.target.health <= player.effective_spell_damage(1) and not self.target.divine_shield:
            self.target.damage(player.effective_spell_damage(1), self)
            player.draw()
        else:
            self.target.damage(player.effective_spell_damage(1), self)
            # not sure how necessary this is, making sure damage before
            # draw but need to compare health before dealing damage


class Hellfire(SpellCard):
    def __init__(self):
        super().__init__("Hellfire", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)
        targets = copy.copy(game.other_player.minions)
        targets.extend(game.current_player.minions)
        targets.append(game.other_player.hero)
        targets.append(game.current_player.hero)
        for minion in targets:
            minion.damage(player.effective_spell_damage(3), self)


class ShadowBolt(SpellCard):
    def __init__(self):
        super().__init__("Shadow Bolt", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(4), self)


class DrainLife(SpellCard):
    def __init__(self):
        super().__init__("Drain Life", 3, CHARACTER_CLASS.WARLOCK,
                         CARD_RARITY.FREE, target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(2), self)
        player.hero.heal(player.effective_heal_power(2), self)


class Soulfire(SpellCard):
    def __init__(self):
        super().__init__("Soulfire", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(4), self)
        player.discard()


class TwistingNether(SpellCard):
    def __init__(self):
        super().__init__("Twisting Nether", 8, CHARACTER_CLASS.WARLOCK, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)
        targets = copy.copy(game.other_player.minions)
        targets.extend(game.current_player.minions)
        for minion in targets:
            minion.die(self)


class Demonfire(SpellCard):
    def __init__(self):
        super().__init__("Demonfire", 2, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        targets = copy.copy(player.game.current_player.minions)
        if self.target.card.minion_type is MINION_TYPE.DEMON and self.target in targets:
            self.target.change_attack(2)
            self.target.increase_health(2)
        else:
            self.target.damage(player.effective_spell_damage(2), self)


class SacrificialPact(SpellCard):
    def __init__(self):
        super().__init__("Sacrificial Pact", 0, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target,
                         filter_func=lambda character: character.card.minion_type == MINION_TYPE.DEMON)

    def use(self, player, game):
        super().use(player, game)
        self.target.die(self)
        player.hero.heal(player.effective_heal_power(5), self)


class SiphonSoul(SpellCard):
    def __init__(self):
        super().__init__("Siphon Soul", 6, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.die(self)
        player.hero.heal(player.effective_heal_power(3), self)


class SenseDemons(SpellCard):
    def __init__(self):
        super().__init__("Sense Demons", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for i in range(0, 2):
            demon_card = game.random_draw(game.current_player.deck.cards,
                                          lambda c: not c.drawn and
                                          c.is_minion() and
                                          c.minion_type == MINION_TYPE.DEMON)
            if demon_card:
                demon_card.drawn = True
                player.deck.left -= 1
                if len(player.hand) < 10:
                    player.hand.append(demon_card)
                    demon_card.player = player
                    self.trigger("card_drawn", demon_card)
                else:
                    player.trigger("card_destroyed", demon_card)
            else:
                if len(player.hand) < 10:
                    player.hand.append(hearthbreaker.cards.minions.warlock.WorthlessImp())
                    player.hand[-1].player = player
                    self.trigger("card_drawn", hearthbreaker.cards.minions.warlock.WorthlessImp())


class BaneOfDoom(SpellCard):
    def __init__(self):
        super().__init__("Bane of Doom", 5, CHARACTER_CLASS.WARLOCK, CARD_RARITY.EPIC,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        if self.target.health <= player.effective_spell_damage(2) and \
                (isinstance(self.target, Minion) and not self.target.divine_shield):
            self.target.damage(player.effective_spell_damage(2), self)
            demons = CollectionSource([IsType(MINION_TYPE.DEMON)])
            demons.get_card(player, player, self).summon(player, game, len(player.minions))
        else:
            self.target.damage(player.effective_spell_damage(2), self)


class Shadowflame(SpellCard):
    def __init__(self):
        super().__init__("Shadowflame", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        shadowflame_damage = self.target.calculate_attack()
        self.target.die(self)
        for minion in game.other_player.minions:
            minion.damage(player.effective_spell_damage(shadowflame_damage),
                          self)


class Corruption(SpellCard):
    def __init__(self):
        super().__init__("Corruption", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.add_effect(Effect(TurnStarted(player=EnemyPlayer()), ActionTag(Kill(), SelfSelector())))


class PowerOverwhelming(SpellCard):
    def __init__(self):
        super().__init__("Power Overwhelming", 1, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_friendly_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.add_effect(Effect(TurnEnded(), ActionTag(Kill(), SelfSelector())))
        self.target.change_attack(4)
        self.target.increase_health(4)


class Darkbomb(SpellCard):
    def __init__(self):
        super().__init__("Darkbomb", 2, CHARACTER_CLASS.WARLOCK, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(player.effective_spell_damage(3), self)


class Demonheart(SpellCard):
    def __init__(self):
        super().__init__("Demonheart", 5, CHARACTER_CLASS.WARLOCK, CARD_RARITY.EPIC,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        targets = copy.copy(player.game.current_player.minions)
        if self.target.card.minion_type is MINION_TYPE.DEMON and self.target in targets:
            self.target.change_attack(5)
            self.target.increase_health(5)
        else:
            self.target.damage(player.effective_spell_damage(5), self)


class Implosion(SpellCard):
    def __init__(self):
        super().__init__("Imp-losion", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        # This is to get around the case where you kill your own spell damage minion
        amount = player.effective_spell_damage(game.random_amount(2, 4))
        had_shield = self.target.divine_shield

        self.target.damage(amount, self)

        if not had_shield:
            for i in range(0, amount):
                imp = Imp()
                imp.summon(player, game, len(player.minions))


class Demonwrath(SpellCard):
    def __init__(self):
        super().__init__("Demonwrath", 3, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)
        targets = copy.copy(game.other_player.minions)
        targets.extend(game.current_player.minions)
        for minion in targets:
            if minion.card.minion_type is not MINION_TYPE.DEMON:
                minion.damage(player.effective_spell_damage(2), self)


class FistOfJaraxxus(SpellCard):
    def __init__(self):
        super().__init__("Fist of Jaraxxus", 4, CHARACTER_CLASS.WARLOCK, CARD_RARITY.RARE,
                         effects=[Effect(CardDiscarded(MinionIsTarget()), ActionTag(Damage(4),
                                                                                    CharacterSelector(None,
                                                                                                      EnemyPlayer(),
                                                                                                      RandomPicker())))
                                  ])

    def use(self, player, game):
        super().use(player, game)

        targets = copy.copy(game.other_player.minions)

        targets.append(game.other_player.hero)
        target = game.random_choice(targets)
        target.damage(player.effective_spell_damage(4), self)
