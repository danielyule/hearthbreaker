import curses
import curses.textpad
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Deck, Game
from hsgame.cards import *
from hsgame.ui.game_printer import GameRender
from tests.testing_agents import SpellTestingAgent
from tests.testing_utils import StackedDeck



def render_game(stdscr):
    class TextAgent:

        def __init__(self, game_window, prompt_window, text_window):
            self.window = prompt_window
            self.game_window = game_window
            self.text_window = text_window
            self.text_box = curses.textpad.Textbox(text_window)
            self.game = None

        def prompt(self, message):
            self.window.addstr(0, 0, message)
            self.window.refresh()
            self.text_window.clear()
            self.text_window.refresh()
            return self.text_box.edit()


        def do_turn(self, player):
            renderer.draw_game()
            self.prompt("What now?")

        def do_card_check(self, cards):
            return [True, True, True, True]

        def set_game(self, game):
            self.game = game

        def choose_target(self, targets):
            return targets[0]

        def choose_index(self, card):
            return 0

        def choose_option(self, *options):
            return options[0]

    # Clear screen
    stdscr.clear()
    #
    # # This raises ZeroDivisionError when i == 10.
    # for i in range(0, 10):
    #     v = i-10
    #     stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, 10/v))
    #
    # stdscr.refresh()
    # stdscr.getkey()
    prompt_window = stdscr.derwin(1, 80, 25, 0)
    text_window = stdscr.derwin(1, 80, 26, 0)

    deck1 = StackedDeck([StonetuskBoar(), BluegillWarrior(), Wolfrider()], CHARACTER_CLASS.DRUID)
    deck2 = StackedDeck([FrostwolfGrunt(), GoldshireFootman(), IronfurGrizzly()], CHARACTER_CLASS.MAGE)
    game = Game([deck1, deck2], [TextAgent(stdscr, prompt_window, text_window), SpellTestingAgent()])
    game.players[0].agent.set_game(game)
    game.players[1].agent.set_game(game)
    renderer = GameRender(stdscr, game, game.players[0])
    game.start()

if __name__ == "__main__":
    curses.wrapper(render_game)