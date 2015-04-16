import copy
from hearthbreaker.cards.base import SpellCard
from hearthbreaker.tags.action import Summon
from hearthbreaker.tags.base import Deathrattle, Buff
from hearthbreaker.tags.selector import PlayerSelector
from hearthbreaker.tags.status import Windfury as _Windfury, Frozen, ManaChange
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE


class AncestralHealing(SpellCard):
    def __init__(self):
        super().__init__("Ancestral Healing", 0, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        # Uses the max health of the minion, so as to combo with Auchenai Soulpriest
        self.target.heal(player.effective_heal_power(self.target.calculate_max_health()), self)
        self.target.taunt = True


class AncestralSpirit(SpellCard):
    def __init__(self):
        super().__init__("Ancestral Spirit", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.deathrattle.append(Deathrattle(Summon(self.target.card), PlayerSelector()))


class Bloodlust(SpellCard):
    def __init__(self):
        super().__init__("Bloodlust", 5, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for minion in player.minions:
            minion.change_temp_attack(3)


class EarthShock(SpellCard):
    def __init__(self):
        super().__init__("Earth Shock", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.silence()
        self.target.damage(player.effective_spell_damage(1), self)


class FarSight(SpellCard):
    def __init__(self):
        super().__init__("Far Sight", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.EPIC)

    def use(self, player, game):
        def reduce_cost(card):
            card.add_buff(Buff(ManaChange(-3)))

        super().use(player, game)
        player.bind_once("card_drawn", reduce_cost)
        player.draw()


class FeralSpirit(SpellCard):
    def __init__(self):
        super().__init__("Feral Spirit", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE, overload=2)

    def use(self, player, game):
        super().use(player, game)

        for i in range(0, 2):
            spirit_wolf = hearthbreaker.cards.minions.shaman.SpiritWolf()
            spirit_wolf.summon(player, game, len(player.minions))

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


class ForkedLightning(SpellCard):
    def __init__(self):
        super().__init__("Forked Lightning", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON, overload=2)

    def use(self, player, game):
        super().use(player, game)

        minions = copy.copy(game.other_player.minions)
        for i in range(0, 2):
            minion = game.random_choice(minions)
            minions.remove(minion)
            minion.damage(player.effective_spell_damage(3), self)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 2


class FrostShock(SpellCard):
    def __init__(self):
        super().__init__("Frost Shock", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_enemy_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(1), self)
        self.target.add_buff(Buff(Frozen()))


class Hex(SpellCard):
    def __init__(self):
        super().__init__("Hex", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        frog = hearthbreaker.cards.minions.neutral.Frog()
        minion = frog.create_minion(None)
        minion.card = frog
        self.target.replace(minion)


class LavaBurst(SpellCard):
    def __init__(self):
        super().__init__("Lava Burst", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_spell_target, overload=2)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(5), self)


class LightningBolt(SpellCard):
    def __init__(self):
        super().__init__("Lightning Bolt", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target, overload=1)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(3), self)


class LightningStorm(SpellCard):
    def __init__(self):
        super().__init__("Lightning Storm", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE, overload=2)

    def use(self, player, game):
        super().use(player, game)

        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(game.random_amount(2, 3)), self)


class RockbiterWeapon(SpellCard):
    def __init__(self):
        super().__init__("Rockbiter Weapon", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_friendly_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.change_temp_attack(3)


class TotemicMight(SpellCard):
    def __init__(self):
        super().__init__("Totemic Might", 0, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for minion in player.minions:
            if minion.card.minion_type == MINION_TYPE.TOTEM:
                minion.increase_health(2)


class Windfury(SpellCard):
    def __init__(self):
        super().__init__("Windfury", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.add_buff(Buff(_Windfury()))


class Reincarnate(SpellCard):

    def __init__(self):
        super().__init__("Reincarnate", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.die(self)
        game.check_delayed()
        self.target.card.summon(self.target.player, game, len(self.target.player.minions))


class Crackle(SpellCard):
    def __init__(self):
        super().__init__("Crackle", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         target_func=hearthbreaker.targeting.find_spell_target, overload=1)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(game.random_amount(3, 6)), self)


class AncestorsCall(SpellCard):
    def __init__(self):
        super().__init__("Ancestor's Call", 4, CHARACTER_CLASS.SHAMAN, CARD_RARITY.EPIC)

    def can_use(self, player, game):
        return super().can_use(player, game) and (len(player.minions) < 7 or len(player.opponent.minions) < 7)

    def use(self, player, game):
        super().use(player, game)
        for player in game.players:
            minions = [card for card in player.hand if card.is_minion()]
            if len(minions) and len(player.minions) < 7:
                minion_card = game.random_choice(minions)
                minion_card.unattach()
                player.hand.remove(minion_card)
                minion_card.summon(player, game, len(player.minions))


class LavaShock(SpellCard):
    def __init__(self):
        super().__init__("Lava Shock", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE,
                         target_func=hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.damage(2, self)
        player.upcoming_overload = 0
        player.mana += player.current_overload
        player.current_overload = 0
