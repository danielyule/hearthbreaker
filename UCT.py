#!python3
# This is a very simple implementation of the UCT Monte Carlo Tree Search algorithm in Python 2.7.
# The function UCT(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a 
# state.GetRandomMove() or state.DoRandomRollout() function.
# 
# Example GameState classes for Nim, OXO and Othello are included to give some idea of how you
# can write your own GameState use UCT in your 2-player game. Change the game to be played in 
# the UCTPlayGame() function at the bottom of the code.
# 
# Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
# 
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
# 
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai

from math import *
import random
from hsgame.game_objects import *
from hsgame.targeting import *
from tests.testing_utils import generate_game_for
from hsgame.agents.basic_agents import DoNothingBot, RandomBot
from hsgame.constants import CHARACTER_CLASS
from hsgame.cards.spells.mage import Pyroblast
deck1 = Pyroblast  # Breaks if you finish with a spell, returning Game Ended
deck2 = Pyroblast
game = generate_game_for(deck1, deck2, RandomBot, RandomBot)
game.players[0].max_mana = 2  # Starting with 1 mana seems to give it issues with empty movelists
game.players[0].hero.health = 3
game.players[1].hero.health = 3
game._start_turn()

class HearthState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement UCT in any 2-player complete information deterministic 
        zero-sum game, although they can be enhanced and made quicker, for example by using a 
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1 and 2.
    """
    def __init__(self, game):
        self.game = game
        self.playerJustMoved = 1

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = HearthState(self.game)
        st.playerJustMoved = self.playerJustMoved
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        # print(str(self.game.current_player.mana) + "/" + str(self.game.current_player.max_mana))
        if move[0] == "end_turn":
            self.game._end_turn()
            self.game._start_turn()
            self.playerJustMoved = 1 - self.playerJustMoved
            # print("Player " + str(self.playerJustMoved) + " ends turn")
        elif move[1] == "summon_minion":
            self.game.current_player.agent.choose_index = move[2]
            move[1]  # DoNothingBot summons at index 0, that's ok for now, but need to pass index eventually
        elif move[2] is None:
            move[1]
        elif move[0] == "minion_attack" or move[0] == "hero_attack" or move[0] == "mage_power":
            self.game.current_player.agent.choose_target = move[2]
            move[1]
            # print(str(move[0]) + " used with target " + str(move[2]))
        else:
            raise NameError("DoMove ran into unclassified card", move)

    def GetMoves(self):
        """ Get all possible moves from this state.
            Going to return tuples, untargeted_spell, targetted_spell, equip_weapon, play_secret, mininion_attack, hero_attack, hero_power, end_turn
        """
        if self.game.players[1].hero.health <= 0 or self.game.players[0].hero.health <= 0:
            return []
        valid_moves = [["end_turn", self.game._end_turn(), None]]
        found_taunt = False
        targets = []
        for enemy in self.game.other_player.minions:
            if enemy.taunt and enemy.can_be_attacked():
                found_taunt = True
            if enemy.can_be_attacked():
                targets.append(enemy)

        if found_taunt:
            targets = [target for target in targets if target.taunt]
        else:
            targets.append(self.game.other_player.hero)

        for minion in copy.copy(self.game.current_player.minions):
            if minion.can_attack():
                for target in targets:
                    valid_moves.append(["minion_attack", minion.attack(), target])

        if self.game.current_player.hero.can_attack():
            for target in targets:
                valid_moves.append(["hero_attack", self.game.current_player.hero.attack(), target])

        for card in copy.copy(self.game.current_player.hand):
            if card.can_use(self.game.current_player, self.game) and isinstance(card, MinionCard):
                valid_moves.append(["summon_minion", self.game.play_card(card), 0])
            elif card.can_use(self.game.current_player, self.game) and isinstance(card, WeaponCard):
                valid_moves.append(["equip_weapon", self.game.play_card(card), None])
            elif card.can_use(self.game.current_player, self.game) and isinstance(card, SecretCard):
                valid_moves.append(["played_secret", self.game.play_card(card), None])
            elif card.can_use(self.game.current_player, self.game) and not card.targetable:
                valid_moves.append(["untargeted_spell", self.game.play_card(card), None])
            elif card.can_use(self.game.current_player, self.game) and card.targetable:
                for target in card.targets:
                    valid_moves.append(["targeted_spell", self.game.play_card(card), target])

        if self.game.current_player.hero.character_class == CHARACTER_CLASS.MAGE and self.game.current_player.hero.power.can_use():
            for target in hsgame.targeting.find_enemy_spell_target(game, lambda x: True):
                valid_moves.append(["mage_power", self.game.current_player.hero.power.use(), target])
        elif self.game.current_player.hero.character_class == CHARACTER_CLASS.PRIEST and self.game.current_player.hero.power.can_use():
            for target in hsgame.targeting.find_friendly_spell_target(game, lambda x: x.health != x.calculate_max_health()):
                valid_moves.append(["priest_power", self.game.current_player.hero.power.use(), target])
        elif self.game.current_player.hero.power.can_use():
            valid_moves.append(["hero_power", self.game.current_player.hero.power.use(), None])
        print(str(valid_moves))
        return valid_moves

    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """
        assert self.game.current_player.hero.health <= 0 or self.game.other_player.hero.health <= 0
        if self.game.current_player.hero.health <= 0:
            return 0
        if self.game.other_player.hero.health <= 0:
            return 1

    def __repr__(self):
        s = "[" + str(self.game.players[1].hero.health) + " hp:" + str(len(self.game.players[1].hand)) + " in hand:" + str(self.game.players[1].deck.left) + " in deck] "
        for minion in copy.copy(self.game.players[1].minions):
            s += str(minion.calculate_attack()) + "/" + str(minion.health) + ":"
        s += "\n[" + str(self.game.players[0].hero.health) + " hp:" + str(len(self.game.players[0].hand)) + " in hand:" + str(self.game.players[1].deck.left) + " in deck] "
        for minion in copy.copy(self.game.players[0].minions):
            s += str(minion.calculate_attack()) + "/" + str(minion.health) + ":"
        s += "\n" + "Current Player: " + str(1 - self.playerJustMoved)
        return s

class NimState:
    """ A state of the game Nim. In Nim, players alternately take 1,2 or 3 chips with the 
        winner being the player to take the last chip. 
        In Nim any initial state of the form 4n+k for k = 1,2,3 is a win for player 1
        (by choosing k) chips.
        Any initial state of the form 4n is a win for player 2.
    """
    def __init__(self, ch):
        self.playerJustMoved = 1 # At the root pretend the player just moved is p1 - p0 has the first move
        self.chips = ch
        
    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = NimState(self.chips)
        st.playerJustMoved = self.playerJustMoved
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        assert move >= 1 and move <= 3 and move == int(move)
        self.chips -= move
        self.playerJustMoved = 1 - self.playerJustMoved
        
    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        return list(range(1,min([4, self.chips + 1])))
    
    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """
        assert self.chips == 0
        if self.playerJustMoved == playerjm:
            return 1 # playerjm took the last chip and has won
        else:
            return 0 # playerjm's opponent took the last chip and has won

    def __repr__(self):
        s = "Chips:" + str(self.chips) + " JustPlayed:" + str(self.playerJustMoved)
        return s

class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves() # future child nodes
        self.playerJustMoved = state.playerJustMoved # the only part of the state that the Node needs later
        
    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
        return s
    
    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves = [x for x in self.untriedMoves if x != m]
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " P:" + str(int(100 * self.wins / self.visits)) + "% W/V:" + str(int(self.wins)) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s


def UCT(rootstate, itermax, verbose = False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state = rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMove(node.move)

        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves) 
            state.DoMove(m)
            node = node.AddChild(m,state) # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != []: # while state is non-terminal
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(node.playerJustMoved)) # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if (verbose):
        print(rootnode.TreeToString(0))
    else:
        print(rootnode.ChildrenToString())

    return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited
                
def UCTPlayGame():
    """ Play a sample game between two UCT players where each player gets a different number 
        of UCT iterations (= simulations = tree nodes).
    """
    # state = NimState(15) # uncomment to play Nim with the given number of starting chips
    state = HearthState(game)
    while (state.GetMoves() != []):
        print(str(state))
        if state.playerJustMoved == 1:
            m = UCT(rootstate = state, itermax = 10, verbose = False) # play with values for itermax and verbose = True
        else:
            m = UCT(rootstate = state, itermax = 10, verbose = False)
        print("Best Move: " + str(m) + "\n")
        state.DoMove(m)
    if state.GetResult(state.playerJustMoved) == 1:
        print("Player " + str(state.playerJustMoved) + " wins!" + "\n" + str(state))
    elif state.GetResult(state.playerJustMoved) == 0:
        print("Player " + str(1 - state.playerJustMoved) + " wins!" + "\n" + str(state))
    else: print("Nobody wins!")
    #raw_input("[Close]")

if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    UCTPlayGame()