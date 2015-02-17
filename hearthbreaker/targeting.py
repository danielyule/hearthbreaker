import copy


def find_spell_target(game, filter_function):
    targets = copy.copy(game.other_player.minions)
    targets.extend(game.current_player.minions)
    targets.append(game.other_player.hero)
    targets.append(game.current_player.hero)

    targets = [target for target in targets if filter_function(target)]
    return targets


def find_enemy_spell_target(game, filter_function):
    targets = copy.copy(game.other_player.minions)
    targets.append(game.other_player.hero)

    targets = [target for target in targets if filter_function(target)]
    return targets


def find_friendly_spell_target(game, filter_function):
    targets = copy.copy(game.current_player.minions)
    targets.append(game.current_player.hero)

    targets = [target for target in targets if filter_function(target)]
    return targets


def find_minion_spell_target(game, filter_function):
    targets = copy.copy(game.other_player.minions)
    targets.extend(game.current_player.minions)

    targets = [target for target in targets if filter_function(target)]
    return targets


def find_enemy_minion_spell_target(game, filter_function):
    targets = copy.copy(game.other_player.minions)

    targets = [target for target in targets if filter_function(target)]
    return targets


def find_friendly_minion_spell_target(game, filter_function):
    targets = copy.copy(game.current_player.minions)

    targets = [target for target in targets if filter_function(target)]
    return targets


def find_enemy_minion_battlecry_target(game, filter_function):
    targets = copy.copy(game.other_player.minions)

    targets = [target for target in targets if filter_function(target)]
    if len(targets) is 0:
        return None
    return targets


def find_friendly_minion_battlecry_target(game, filter_function):
    targets = copy.copy(game.current_player.minions)

    targets = [target for target in targets if filter_function(target)]
    if len(targets) is 0:
        return None
    return targets
