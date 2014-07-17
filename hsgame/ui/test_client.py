import curses

from hsgame.cards import StonetuskBoar, RagingWorgen
from tests.testing_agents import MinionPlayingAgent
from tests.testing_utils import generate_game_for
from hsgame.ui.game_printer import GameRender


def render_game(stdscr):
    # Clear screen
    stdscr.clear()
    #
    # # This raises ZeroDivisionError when i == 10.
    # for i in range(0, 10):
    # v = i-10
    #     stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, 10/v))
    #
    # stdscr.refresh()
    # stdscr.getkey()
    game = generate_game_for(StonetuskBoar, RagingWorgen, MinionPlayingAgent, MinionPlayingAgent)
    for turn in range(0, 6):
        game.play_single_turn()

    game._start_turn()
    renderer = GameRender(stdscr, game, game.current_player)
    renderer.draw_game()
    stdscr.refresh()
    stdscr.getkey()


if __name__ == "__main__":
    curses.wrapper(render_game)