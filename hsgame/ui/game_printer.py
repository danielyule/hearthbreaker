from hsgame.cards import StonetuskBoar, RagingWorgen
from tests.testing_agents import MinionPlayingAgent
from tests.testing_utils import generate_game_for

__author__ = 'Daniel'
import curses

card_abbreviations = {
    'Mark of the Wild': 'Mark Wild',
    'Power of the Wild': 'Pow. Wild',
    'Wild Growth': 'W. Growth',
    'Healing Touch': 'Heal Touch',
    'Mark of Nature': 'Mark Nat.',
    'Savage Roar': 'Sav. Roar',
    'Soul of the Forest': 'Soul Forest',
    'Force of Nature': 'Force of Nat.',
    'Keeper of the Grove': 'Keep. Grove',
    'Druid of the Claw': 'Druid Claw',
    'Stonetusk Boar': 'StntskBr',
}


def abbreviate (card_name):
    return card_abbreviations.get(card_name, card_name)

def minion_to_string(minion):
    status_array = []
    if minion.can_attack():
        status_array.append("*")
    if "attack" in minion.events:
        status_array.append("a")
    if "turn_start" in minion.events:
        status_array.append("b")
    if minion.charge:
        status_array.append("c")
    if minion.deathrattle is not None:
        status_array.append("d")
    if 'turn_end' in minion.events:
        status_array.append("e")
    if minion.frozen:
        status_array.append("f")
    if minion.stealth:
        status_array.append("s")
    if minion.taunt:
        status_array.append("t")

    status = ''.join(status_array)
    power_line = "{0} - {1}/{2}".format(minion.calculate_attack(), minion.health, minion.calculate_max_health())
    return "{0:^10}\n{1:^10}\n{2:^10}".format(abbreviate(minion.card.name)[:8], power_line, status)


def game_to_string(game):
    pass

def draw_game(window, game):
    def create_minion_strings(minions):
        top_string = ""
        middle_string = ""
        bottom_string = ""

        for minion in minions:
            min_split = minion_to_string(minion).split("\n")
            top_string += min_split[0]
            middle_string += min_split[1]
            bottom_string += min_split[2]
        return "\n".join([top_string, middle_string, bottom_string])

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    minion_window = window.derwin(7, 70, 0, 10)
    minion_window.addstr(0, 0, create_minion_strings(game.players[0].minions), curses.color_pair(1))
    minion_window.addstr(4, 0, create_minion_strings(game.players[1].minions), curses.color_pair(1))
