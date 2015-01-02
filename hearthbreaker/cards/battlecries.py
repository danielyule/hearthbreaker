import copy


def gain_one_health_for_each_card_in_hand(minion):
    minion.increase_health(len(minion.player.hand))


def deathwing(minion):
    targets = copy.copy(minion.player.game.other_player.minions)
    targets.extend(minion.player.game.current_player.minions)
    for target in targets:
        if target is not minion:
            target.die(None)
    for i in range(len(minion.player.hand)):
        minion.player.game.current_player.discard()
