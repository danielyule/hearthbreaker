import curses
import curses.textpad
import sys

from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Game
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
            text = self.text_box.edit()
            return text.strip().lower()

        def do_turn(self, player):
            renderer.draw_game()
            index = 0
            action = self.prompt("What now? (attack, play, power, quit, end)")
            while not (action == "quit" or action == "end"):
                if action == "play":
                    card = self.choose_card()
                    if card is not None:
                        self.game.play_card(card)
                elif action == "attack":
                    attacker = self.choose_attacker()
                    if attacker is not None:
                        attacker.attack()
                elif action == "power":
                    if player.hero.power.can_use():
                        player.hero.power.use()
                index += 1
                renderer.draw_game()
                action = self.prompt("What now? (attack, play, power, quit, end)")
            if action == "quit":
                sys.exit(0)

        def choose_card(self):
            filtered_cards = [card for card in filter(lambda card: card.can_use(self.game.current_player, self.game),
                                                      self.game.current_player.hand)]
            if len(filtered_cards) is 0:
                return None
            renderer.targets = filtered_cards
            renderer.selected_target = renderer.targets[0]
            renderer.draw_game()
            self.window.addstr(0, 0, "Choose Card")
            self.window.refresh()
            ch = 0
            index = 0
            while ch != 10 and ch != 27:
                ch = self.window.getch()

                if ch == curses.KEY_LEFT:
                    index -= 1
                    if index < 0:
                        index = len(renderer.targets) - 1
                if ch == curses.KEY_RIGHT:
                    index += 1
                    if index == len(renderer.targets):
                        index = 0
                renderer.selected_target = renderer.targets[index]
                renderer.draw_game()
                self.window.addstr(0, 0, "Choose Card")
                self.window.refresh()
            renderer.targets = None
            if ch == 27:
                return None

            return renderer.selected_target

        def choose_attacker(self):
            filtered_attackers = [minion for minion in filter(lambda minion: minion.can_attack(),
                                                              self.game.current_player.minions)]
            if self.game.current_player.hero.can_attack():
                filtered_attackers.append(self.game.current_player.hero)
            if len(filtered_attackers) is 0:
                return None
            renderer.targets = filtered_attackers
            renderer.selected_target = renderer.targets[0]
            renderer.draw_game()
            self.window.addstr(0, 0, "Choose attacker")
            self.window.refresh()
            ch = 0
            index = 0
            while ch != 10 and ch != 27:
                ch = self.window.getch()
                self.window.addstr(0, 0, "{0}".format(ch))
                self.window.refresh()
                if ch == curses.KEY_LEFT:
                    index -= 1
                    if index < 0:
                        index = len(renderer.targets) - 1
                if ch == curses.KEY_RIGHT:
                    index += 1
                    if index == len(renderer.targets):
                        index = 0
                renderer.selected_target = renderer.targets[index]
                renderer.draw_game()
                self.window.refresh()
            renderer.targets = None
            if ch == 27:
                return None

            return renderer.selected_target

        def do_card_check(self, cards):
            return [True, True, True, True]

        def set_game(self, game):
            self.game = game

        def choose_target(self, targets):

            if len(targets) is 0:
                return None
            renderer.targets = targets
            renderer.selected_target = renderer.targets[0]
            renderer.draw_game()
            self.window.addstr(0, 0, "Choose target")
            self.window.refresh()
            ch = 0
            index = 0
            while ch != 10 and ch != 27:
                ch = self.window.getch()
                if ch == curses.KEY_LEFT:
                    index -= 1
                    if index < 0:
                        index = len(renderer.targets) - 1
                if ch == curses.KEY_RIGHT:
                    index += 1
                    if index == len(renderer.targets):
                        index = 0
                renderer.selected_target = renderer.targets[index]
                renderer.draw_game()
                self.window.refresh()
            renderer.targets = None
            if ch == 27:
                return None

            return renderer.selected_target

        def choose_index(self, card):
            renderer.selection_index = 0
            renderer.draw_game()
            self.window.addstr(0, 0, "Choose placement location")
            self.window.refresh()
            ch = 0
            while ch != 10 and ch != 27:
                ch = self.window.getch()
                if ch == curses.KEY_LEFT:
                    renderer.selection_index -= 1
                    if renderer.selection_index < 0:
                        renderer.selection_index = len(self.game.current_player.minions)
                if ch == curses.KEY_RIGHT:
                    renderer.selection_index += 1
                    if renderer.selection_index > len(self.game.current_player.minions):
                        renderer.selection_index = 0
                renderer.draw_game()
                self.window.refresh()
            index = renderer.selection_index
            renderer.selection_index = -1
            if ch == 27:
                return -1

            return index

        def choose_option(self, *options):
            self.window.addstr(0, 0, "Choose option")
            index = 0
            selected = 0
            for option in options:
                if index == selected:
                    color = curses.color_pair(4)
                else:
                    color = curses.color_pair(3)

                self.text_window.addstr(0, index * 20, option.name[:19], color)
                index += 1
            self.window.refresh()
            self.text_window.refresh()
            ch = 0
            while ch != 10 and ch != 27:
                ch = self.window.getch()
                if ch == curses.KEY_LEFT:
                    selected -= 1
                    if selected < 0:
                        selected = len(options) - 1
                if ch == curses.KEY_RIGHT:
                    selected += 1
                    if selected == len(options):
                        selected = 0
                index = 0
                for option in options:
                    if index == selected:
                        color = curses.color_pair(4)
                    else:
                        color = curses.color_pair(3)

                    self.text_window.addstr(0, index * 20, option.name[:19], color)
                    index += 1
                self.window.refresh()
                self.text_window.refresh()
            if ch == 27:
                return None

            return options[selected]

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
    prompt_window = stdscr.derwin(1, 80, 23, 0)
    text_window = stdscr.derwin(1, 80, 24, 0)

    deck1 = StackedDeck([StonetuskBoar(), BluegillWarrior(), Wolfrider(), KeeperOfTheGrove()], CHARACTER_CLASS.DRUID)
    deck2 = StackedDeck([FrostwolfGrunt(), GoldshireFootman(), IronfurGrizzly()], CHARACTER_CLASS.MAGE)
    game = Game([deck1, deck2], [TextAgent(stdscr, prompt_window, text_window), SpellTestingAgent()])
    if isinstance(game.players[0].agent, TextAgent):
        renderer = GameRender(stdscr, game, game.players[0])
    else:
        renderer = GameRender(stdscr, game, game.players[1])
    game.start()


if __name__ == "__main__":
    curses.wrapper(render_game)