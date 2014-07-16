from unittest.mock import Mock
from hsgame.game_objects import Player

__author__ = 'Daniel'

import unittest
from hsgame.cards import StonetuskBoar
from hsgame.ui.game_printer import minion_to_string

class TestPrinting(unittest.TestCase):

    def test_Minions(self):
        dummy_player = Mock(Player)
        dummy_player.auras = []
        minion = StonetuskBoar().create_minion(dummy_player)
        minion.player = dummy_player
        minion.card = StonetuskBoar()
        self.assertEqual(" StntskBr \n 1 - 1/1  \n    c     ", minion_to_string(minion))
