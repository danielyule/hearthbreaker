import hsgame.targeting
from hsgame.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hsgame.game_objects import Card


class Effect:
    def __init__(self, name, target):
        self.name = name
        self.target = target

    def apply(self):
        pass

    def unapply(self):
        pass


class ImmuneThisTurn(Effect):
    def __init__(self, target):
        super().__init__("Immune This Turn", target)

    def apply(self):
        self.target.immune = True
        self.target.player.bind("turn_ended", self.remove_immunity)

    def unapply(self):
        self.target.player.unbind("turn_ended", self.remove_immunity)

    def remove_immunity(self):
        self.target.immune = False


class BestialWrath(Card):
    def __init__(self):
        super().__init__("Bestial Wrath", 1, CHARACTER_CLASS.HUNTER,
                         CARD_RARITY.EPIC,
                         hsgame.targeting.find_minion_spell_target,
                         lambda minion: minion.minion_type is MINION_TYPE.BEAST and minion.spell_targetable())

    def use(self, player, game):
        super().use(player, game)

        self.target.apply_effect(ImmuneThisTurn)
        self.target.change_temp_attack(2)