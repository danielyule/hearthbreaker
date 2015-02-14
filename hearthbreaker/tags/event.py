from hearthbreaker.tags.base import MinionEvent, PlayerEvent
from hearthbreaker.tags.condition import MinionIsNotTarget, CardIsNotTarget
from hearthbreaker.tags.selector import FriendlyPlayer


class SpellCast(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("spell_cast", condition, player)

    def bind(self, target, func):
        for player in self.player.get_players(target.player):
            self.__target__ = target
            self.__func__ = func
            player.bind("card_played", self.__action__)

    def unbind(self, target, func):
        for player in self.player.get_players(target.player):
            player.unbind("card_played", self.__action__)

    def __action__(self, card, index):
        if card.is_spell():
            if self.condition:
                super().__action__(card, index)
            else:
                self.__func__(card, index)


class CardPlayed(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("card_played", condition, player)


class CardUsed(PlayerEvent):
    def __init__(self, condition=CardIsNotTarget(), player=FriendlyPlayer()):
        super().__init__("card_used", condition, player)


class AfterAdded(PlayerEvent):
    def __init__(self, condition=MinionIsNotTarget(), player=FriendlyPlayer()):
        super().__init__("after_added", condition, player)


class TurnEnded(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("turn_ended", condition, player)


class TurnStarted(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("turn_started", condition, player)


class MinionDied(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("minion_died", condition, player)


class MinionPlaced(PlayerEvent):
    def __init__(self, condition=MinionIsNotTarget(), player=FriendlyPlayer()):
        super().__init__("minion_placed", condition, player)


class MinionSummoned(PlayerEvent):
    def __init__(self, condition=MinionIsNotTarget(), player=FriendlyPlayer()):
        super().__init__("minion_summoned", condition, player)


class CharacterDamaged(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("character_damaged", condition, player)


class CharacterHealed(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("character_healed", condition, player)


class SecretRevealed(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("secret_revealed", condition, player)


class CharacterAttack(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("character_attack", condition, player)


class ArmorIncreased(PlayerEvent):
    def __init__(self, condition=None, player=FriendlyPlayer()):
        super().__init__("armor_increased", condition, player)


class Attack(MinionEvent):
    def __init__(self, condition=None):
        super().__init__("attack", condition)


class AttackCompleted(MinionEvent):
    def __init__(self):
        super().__init__("attack_completed")


class DidDamage(MinionEvent):
    def __init__(self):
        super().__init__("did_damage")


class WeaponDestroyed(MinionEvent):
    def __init__(self):
        super().__init__("weapon_destroyed")


class Damaged(MinionEvent):
    def __init__(self):
        super().__init__("damaged")


class Drawn(MinionEvent):
    def __init__(self):
        super().__init__("drawn")
