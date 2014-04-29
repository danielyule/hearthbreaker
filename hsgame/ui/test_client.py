from hsgame.replay import SavedGame

__author__ = 'Daniel'
import curses
from hsgame.ui.game_printer import draw_game

def render_game(stdscr):
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
    game = SavedGame("tests/replays/stonetusk_innervate.rep")
    game.start()
    draw_game(game, stdscr)
    stdscr.refresh()
    stdscr.getkey()

if __name__ == "__main__":
    curses.wrapper(render_game)