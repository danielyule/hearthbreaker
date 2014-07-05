import random
import unittest

from hsgame.agents.basic_agents import PredictableBot
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Game
from tests.testing_agents import *
from tests.testing_utils import generate_game_for, StackedDeck
from hsgame.cards import *


class TestWarlock(unittest.TestCase):
	def setUp(self):
		random.seed(1857)

	def test_MortalCoil(self):
		game = generate_game_for(BloodfenRaptor, MortalCoil, DoNothingBot, OneSpellTestingAgent)
		
		raptor = BloodfenRaptor()
		raptor.summon(game.players[0], game, 0)
			#player 0 plays raptor
		self.assertEqual(1, len(game.players[0].minions))
		self.assertEqual(2, game.players[0].minions[0].health)
		self.assertEqual(4, len(game.players[1].hand))

		game.play_single_turn()
		game.play_single_turn()
			#mortal coils the 2hp raptor
		self.assertEqual(4, len(game.players[1].hand))
		self.assertEqual(1, len(game.players[0].minions))
		self.assertEqual(1, game.players[0].minions[0].health)
		
		game.play_single_turn()		
		game.play_single_turn()
			#mortal coils the 1hp raptor and draws
		self.assertEqual(0, len(game.players[0].minions))
		self.assertEqual(5, len(game.players[1].hand))
		
	def test_FlameImp(self):
		game = generate_game_for(FlameImp, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

		game.play_single_turn()
		#play Flame Imp, 3 damage to own hero
		self.assertEqual(1, len(game.players[0].minions))
		self.assertEqual(27, game.players[0].hero.health)
		
	def test_PitLord(self):
		game = generate_game_for(PitLord, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
		for turn in range (0, 7):
			game.play_single_turn()
		#play Pit Lord, 5 damage to own hero
		self.assertEqual(1, len(game.players[0].minions))
		self.assertEqual(25, game.players[0].hero.health)
		
	def test_DreadInfernal(self):
		game = generate_game_for(DreadInfernal, StonetuskBoar, MinionPlayingAgent, MinionPlayingAgent)
		for turn in range (0, 10):
			game.play_single_turn()
		self.assertEqual(0, len(game.players[0].minions))
		self.assertEqual(30, game.players[0].hero.health)
		self.assertEqual(5, len(game.players[1].minions))
		self.assertEqual(30, game.players[1].hero.health)
		
		game.play_single_turn()
		#Plays Dread Infernal, 1 damage to all
		self.assertEqual(1, len(game.players[0].minions))
		self.assertEqual(6, game.players[0].minions[0].health)
		self.assertEqual(29, game.players[0].hero.health)
		self.assertEqual(0, len(game.players[1].minions))
		self.assertEqual(29, game.players[1].hero.health)
		
	def test_Felguard(self):
		game = generate_game_for(Felguard, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
		for turn in range (0, 4):
			game.play_single_turn()
			
		self.assertEqual(0, len(game.players[0].minions))
		self.assertEqual(2, game.players[0].max_mana)

		game.play_single_turn()
		#Plays Felguard, destroys mana crystal
		self.assertEqual(1, len(game.players[0].minions))
		self.assertEqual(2, game.players[0].max_mana)		
		
	def test_Succubus(self):
		game = generate_game_for(Succubus, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
		for turn in range (0, 2):
			game.play_single_turn()	
			
		self.assertEqual(0, len(game.players[0].minions))
		self.assertEqual(4, len(game.players[0].hand))

		game.play_single_turn()
		#Plays Succubus, discards
		self.assertEqual(1, len(game.players[0].minions))
		self.assertEqual(3, len(game.players[0].hand))
		
	def test_Doomguard(self):
		game = generate_game_for(Doomguard, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
		for turn in range (0, 8):
			game.play_single_turn()	
			
		self.assertEqual(0, len(game.players[0].minions))
		self.assertEqual(7, len(game.players[0].hand))

		game.play_single_turn()
		#Plays Doomguard, discards twice
		self.assertEqual(1, len(game.players[0].minions))
		self.assertEqual(5, len(game.players[0].hand))