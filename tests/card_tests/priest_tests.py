import random
import unittest

from hearthbreaker.agents.basic_agents import PredictableAgent, DoNothingAgent
from hearthbreaker.engine import Game
from tests.agents.testing_agents import OneCardPlayingAgent, CardTestingAgent, PlayAndAttackAgent, SelfSpellTestingAgent
from hearthbreaker.constants import CHARACTER_CLASS
from tests.testing_utils import generate_game_for, StackedDeck
from hearthbreaker.replay import playback, Replay
from hearthbreaker.cards import *


class TestPriest(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_CircleOfHealing(self):
        deck1 = StackedDeck(
            [CircleOfHealing(), MogushanWarden(), CircleOfHealing(), CircleOfHealing(), CircleOfHealing(),
             CircleOfHealing(), CircleOfHealing()], CHARACTER_CLASS.PRIEST)
        deck2 = StackedDeck([MogushanWarden()], CHARACTER_CLASS.PALADIN)
        game = Game([deck1, deck2], [CardTestingAgent(), OneCardPlayingAgent()])
        game.pre_game()
        game.current_player = 1

        for turn in range(0, 8):
            game.play_single_turn()

        game.players[0].minions[0].health = 4
        game.players[1].minions[0].health = 4
        game.play_single_turn()  # Circle of Healing should be played
        self.assertEqual(game.players[0].minions[0].calculate_max_health(), game.players[0].minions[0].health)
        self.assertEqual(game.players[1].minions[0].calculate_max_health(), game.players[1].minions[0].health)

    def test_DivineSpirit(self):
        game = generate_game_for(DivineSpirit, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(7, game.players[1].minions[0].health)
        self.assertEqual(7, game.players[1].minions[0].calculate_max_health())
        game.play_single_turn()  # Two Divine Spirits should be played
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(28, game.players[1].minions[0].health)
        self.assertEqual(28, game.players[1].minions[0].calculate_max_health())
        # Test that this spell is being silenced properly as well
        game.players[1].minions[0].silence()
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(7, game.players[1].minions[0].health)
        self.assertEqual(7, game.players[1].minions[0].calculate_max_health())
        game.play_single_turn()
        # Let's say the minion got damaged
        game.players[1].minions[0].health = 4
        game.play_single_turn()  # Three Divine Spirits should be played
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(32, game.players[1].minions[0].health)
        self.assertEqual(35, game.players[1].minions[0].calculate_max_health())
        # Test that this spell is being silenced properly as well
        game.players[1].minions[0].silence()
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(7, game.players[1].minions[0].health)
        self.assertEqual(7, game.players[1].minions[0].calculate_max_health())

    def test_HolyFire(self):
        game = generate_game_for(HolyFire, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        game.players[0].hero.health = 20
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(7, game.players[1].minions[0].health)
        self.assertEqual(7, game.players[1].minions[0].calculate_max_health())
        game.play_single_turn()  # Holy Fire should be played
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(2, game.players[1].minions[0].health)
        self.assertEqual(7, game.players[1].minions[0].calculate_max_health())
        self.assertEqual(25, game.players[0].hero.health)

    def test_HolyNova(self):
        deck1 = StackedDeck([MogushanWarden(), HolyNova()], CHARACTER_CLASS.PRIEST)
        deck2 = StackedDeck([MogushanWarden()], CHARACTER_CLASS.PALADIN)
        game = Game([deck1, deck2], [CardTestingAgent(), OneCardPlayingAgent()])
        game.pre_game()
        game.current_player = 1

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        game.players[0].minions[0].health = 4  # Fake damage
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(7, game.players[1].minions[0].health)
        game.play_single_turn()  # Holy Nova should be played
        self.assertEqual(6, game.players[0].minions[0].health)
        self.assertEqual(5, game.players[1].minions[0].health)

    def test_HolySmite(self):
        game = generate_game_for(HolySmite, MogushanWarden, CardTestingAgent, DoNothingAgent)

        self.assertEqual(30, game.players[1].hero.health)
        game.play_single_turn()  # Holy Smite should be played
        self.assertEqual(28, game.players[1].hero.health)

    def test_InnerFire(self):
        game = generate_game_for(InnerFire, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(7, game.players[1].minions[0].health)
        game.play_single_turn()  # Inner Fire should be played
        self.assertEqual(7, game.players[1].minions[0].calculate_attack())
        self.assertEqual(7, game.players[1].minions[0].health)
        # Test that this spell is being silenced properly as well
        game.players[1].minions[0].silence()
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(7, game.players[1].minions[0].health)

    def test_MassDispel(self):
        game = generate_game_for(MassDispel, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertTrue(game.players[1].minions[0].taunt)
        self.assertEqual(7, len(game.players[0].hand))
        game.play_single_turn()  # Mass Dispel should be played
        self.assertEqual(1, len(game.players[1].minions))
        self.assertFalse(game.players[1].minions[0].taunt)
        self.assertEqual(8, len(game.players[0].hand))

    def test_MindBlast(self):
        game = generate_game_for(MindBlast, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)
        game.play_single_turn()  # Mind Blast should be played
        self.assertEqual(25, game.players[1].hero.health)

    def test_MindControl(self):
        game = generate_game_for(MindControl, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 18):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[1].minions))
        game.play_single_turn()  # Mind Control should be played
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[1].minions))

    def test_MindVision(self):
        game = generate_game_for(MindVision, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)

        self.assertEqual(3, len(game.players[0].hand))
        self.assertEqual(5, len(game.players[1].hand))
        game.play_single_turn()  # Mind Vision should be played
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual("Mogu'shan Warden", game.players[0].hand[-1].name)
        self.assertEqual(5, len(game.players[1].hand))

    def test_MindVision_no_cards(self):
        game = generate_game_for(Wisp, MindVision, CardTestingAgent, OneCardPlayingAgent)

        game.play_single_turn()  # All cards should be played
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(5, len(game.players[1].hand))

        game.play_single_turn()  # Mind Vision should be played, nothing is being copied
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(5, len(game.players[1].hand))

    def test_Mindgames(self):
        game = generate_game_for(Mindgames, MogushanWarden, CardTestingAgent, DoNothingAgent)

        # Mindgames should be played, Mogu'shan Warden will be found and put into the battlefield
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Mogu'shan Warden", game.players[0].minions[0].card.name)

        # Cheat
        for index in range(0, 30):
            game.players[1].deck.cards[index].drawn = True
        game.players[1].deck.left = 0

        game.play_single_turn()
        game.play_single_turn()
        # Mindgames should be played, opponent have no cards left in deck so Shadow of Nothing should be summoned
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Shadow of Nothing", game.players[0].minions[0].card.name)

    def test_PowerWordShield(self):
        game = generate_game_for(StonetuskBoar, PowerWordShield, OneCardPlayingAgent, CardTestingAgent)

        # Power Word: Shield should be played, and target the enemy Stonetusk Boar. And a card should be drawn.
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[0].calculate_max_health())
        self.assertEqual(6, len(game.players[1].hand))

    def test_ShadowMadness(self):
        game = generate_game_for([MagmaRager, MogushanWarden, WarGolem],
                                 [ShadowMadness, ShadowMadness, Silence], OneCardPlayingAgent,
                                 PlayAndAttackAgent)

        # Magma Rager should be played
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Magma Rager", game.players[0].minions[0].card.name)
        self.assertEqual(7, len(game.players[1].hand))

        # Shadow Madness shouldn't be played, since Magma Rager has attack > 3
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(8, len(game.players[1].hand))

        # Mogu'shan Warden should be played
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Mogu'shan Warden", game.players[0].minions[0].card.name)

        # Shadow Madness should be played, targeting the Mogu'shan that will attack the Magma.
        # Results in killing the Magma, and Mogu'shan takes 5 damage before being returned to the owner.
        game.play_single_turn()
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Mogu'shan Warden", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].minions[0].health)

        # Nothing should happen, no mana for War Golem
        game.play_single_turn()

        # Shadow Madness should be played again targeting the damaged Mogu'shan. Silence should follow after, that
        # target the "mind controlled" Mogu'shan, immediately causing it to switch to our side, before it can attack.
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual("Mogu'shan Warden", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(30, game.players[0].hero.health)

    def test_ShadowMadness_and_Corruption(self):
        game = generate_game_for([ShadowMadness, PowerOverwhelming], [OasisSnapjaw, WarGolem],
                                 CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        # Both Shadow Madness and Power Overlwhelming should be played on the Snapjaw.  At the end of the turn, the
        # Snapjaw should revert back to the owning player, and not die, but still have its effect.

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(6, game.other_player.minions[0].calculate_attack())
        self.assertEqual(11, game.other_player.minions[0].health)

        game.play_single_turn()

        # Now the Snapjaw should be dead
        self.assertEqual(0, len(game.current_player.minions))

    def test_ShadowMadness_and_death(self):
        game = generate_game_for([MagmaRager, SludgeBelcher], ShadowMadness, OneCardPlayingAgent, PlayAndAttackAgent)

        for turn in range(9):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual("Slime", game.current_player.minions[0].card.name)

    def test_ShadowWordDeath(self):
        game = generate_game_for([IronfurGrizzly, MagmaRager], ShadowWordDeath, OneCardPlayingAgent, CardTestingAgent)

        # Ironfur Grizzly should be played
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Ironfur Grizzly", game.players[0].minions[0].card.name)

        # Nothing should happen, since the attack of Grizzly is 3
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))

        # Magma Rager should be played
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Magma Rager", game.players[0].minions[0].card.name)

        # Shadow Word: Death should be played, targeting the Magma Rager
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Ironfur Grizzly", game.players[0].minions[0].card.name)

    def test_ShadowWordPain(self):
        game = generate_game_for([MagmaRager, IronfurGrizzly], ShadowWordPain, OneCardPlayingAgent, CardTestingAgent)

        # Magma Rager should be played
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Magma Rager", game.players[0].minions[0].card.name)

        # Nothing should happen, since the attack of Magma Rager is 5
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))

        # Ironfur Grizzly should be played
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Ironfur Grizzly", game.players[0].minions[0].card.name)

        # Shadow Word: Pain should be played, targeting the Grizzly
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Magma Rager", game.players[0].minions[0].card.name)

    def test_Shadowform(self):
        game = generate_game_for(IronfurGrizzly, Shadowform, OneCardPlayingAgent, PredictableAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual("Lesser Heal", game.players[1].hero.power.__str__())

        # Shadowform should be played
        game.play_single_turn()
        self.assertEqual("Mind Spike", game.players[1].hero.power.__str__())

        # Nothing special
        game.play_single_turn()

        # Mind Spike should be used, and Shadowform should be played
        game.play_single_turn()
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual("Mind Shatter", game.players[1].hero.power.__str__())

        # Nothing special
        game.play_single_turn()
        self.assertEqual(5, len(game.players[0].minions))

        # Mind Shatter should be used, and Shadowform should be played
        # (but nothing will happen, we are already at Mind Shatter)
        game.play_single_turn()
        self.assertEqual("Mind Shatter", game.players[1].hero.power.__str__())
        self.assertEqual(4, len(game.players[0].minions))

        # Test using the hero power, then cast Shadowform and use the new power (this is possible)
        game = playback(Replay("tests/replays/card_tests/Shadowform.hsreplay"))
        game.start()
        self.assertEqual(10, game.players[0].max_mana)
        self.assertEqual(3, game.players[0].mana)
        self.assertEqual(28, game.players[1].hero.health)

    def test_Silence(self):
        game = generate_game_for(IronfurGrizzly, Silence, OneCardPlayingAgent, CardTestingAgent)

        # Ironfur Grizzly should be played
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Ironfur Grizzly", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].taunt)

        # Silence should be played, targeting the grizzly
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Ironfur Grizzly", game.players[0].minions[0].card.name)
        self.assertFalse(game.players[0].minions[0].taunt)

    def test_Thoughtsteal(self):
        game = generate_game_for(Thoughtsteal, IronfurGrizzly, CardTestingAgent, DoNothingAgent)

        # Thoughtsteal should be played, copying two grizzly
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual("Ironfur Grizzly", game.players[0].hand[-1].name)
        self.assertEqual("Ironfur Grizzly", game.players[0].hand[-2].name)

    def test_CabalShadowPriest(self):
        game = generate_game_for(CabalShadowPriest, StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(5, len(game.players[1].minions))

        # Cabal Shadow Priest should be played, targeting one boar
        game.play_single_turn()
        self.assertEqual(4, len(game.players[1].minions))
        self.assertEqual(2, len(game.players[0].minions))

    def test_Lightspawn(self):
        game = generate_game_for(Lightspawn, StonetuskBoar, OneCardPlayingAgent, PredictableAgent)

        # Lightspawn should be played
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(5, game.players[0].minions[0].health)

        # Lightspawn should have taken some hits
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)

        game.players[0].minions[0].heal(2, None)
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

        game.players[0].minions[0].increase_health(4)
        self.assertEqual(7, game.players[0].minions[0].calculate_attack())
        self.assertEqual(7, game.players[0].minions[0].health)

        game.players[0].minions[0].decrease_health(2)  # max_health goes from 9 to 7
        self.assertEqual(7, game.players[0].minions[0].calculate_attack())
        self.assertEqual(7, game.players[0].minions[0].health)

    def test_Lightwell(self):
        game = generate_game_for(Lightwell, StonetuskBoar, OneCardPlayingAgent, PredictableAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(28, game.players[0].hero.health)
        self.assertEqual(2, game.players[0].minions[0].health)

        # Lightwell is out, it should heal at the beginning of this turn
        game.play_single_turn()
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertEqual(30, game.players[0].hero.health)

    def test_Lightwell2(self):
        game = generate_game_for([Lightwell, Deathwing], Whirlwind, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(4, game.players[0].minions[0].health)

        game.play_single_turn()

        self.assertEqual(5, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, game.players[0].minions[0].health)

    def test_NorthshireCleric(self):
        game = generate_game_for(NorthshireCleric, StonetuskBoar, PredictableAgent, PredictableAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(26, game.players[0].deck.left)

        # Northshire is damaged, should get a heal and a card should be drawn
        game.play_single_turn()
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(24, game.players[0].deck.left)

        game.players[0].hero.health = 28
        game.players[0].hero.heal(2, None)
        self.assertEqual(24, game.players[0].deck.left)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        # Silence one Northshire, the other one should still work
        game.players[0].minions[0].silence()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(22, game.players[0].deck.left)
        game.play_single_turn()
        self.assertEqual(20, game.players[0].deck.left)

    def test_AuchenaiSoulpriest(self):
        game = generate_game_for([AuchenaiSoulpriest, EarthenRingFarseer], StonetuskBoar,
                                 OneCardPlayingAgent, DoNothingAgent)

        # Auchenai Soulpriest should be played
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Auchenai Soulpriest", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].heal_does_damage)

        # ERF will damage the Soulpriest with its battlecry

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Earthen Ring Farseer", game.players[0].minions[0].card.name)
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].health)

        game.play_single_turn()
        game.play_single_turn()

        game.players[0].minions[2].silence()
        self.assertTrue(game.players[0].heal_does_damage)
        soulpriest = game.players[0].minions[0]
        soulpriest.die(None)
        game.check_delayed()
        self.assertFalse(game.players[0].heal_does_damage)

        game.play_single_turn()
        # ERF should heal again
        game.play_single_turn()

        # This minion should not have taken damage and received heal instead
        self.assertEqual(3, game.players[0].minions[1].health)

    def test_AuchenaiSoulpriest_with_hero_power(self):
        game = generate_game_for(AuchenaiSoulpriest, StonetuskBoar, PredictableAgent, DoNothingAgent)

        # Auchenai Soulpriest should be played
        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Auchenai Soulpriest", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].heal_does_damage)

        game.play_single_turn()
        # Hero power will be used on own minion, which should now cause 2 damage instead of 2 heal.
        game.play_single_turn()

        self.assertEqual(3, game.players[0].minions[1].health)

    def test_ProphetVelen(self):
        game = generate_game_for([ProphetVelen, ProphetVelen, MindBlast], StonetuskBoar, OneCardPlayingAgent,
                                 DoNothingAgent)

        # Prophet Velen should be played
        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Prophet Velen", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].spell_multiplier)
        self.assertEqual(2, game.players[0].heal_multiplier)

        game.play_single_turn()
        # Another Prophet Velen should be played
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].spell_multiplier)
        self.assertEqual(4, game.players[0].heal_multiplier)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        # Mind Blast should be played, dealing 5 * 4 = 20 damage
        game.play_single_turn()

        self.assertEqual(10, game.players[1].hero.health)
        velen = game.players[0].minions[0]
        velen.die(None)
        velen.activate_delayed()
        self.assertEqual(2, game.players[0].spell_multiplier)
        self.assertEqual(2, game.players[0].heal_multiplier)
        game.players[0].minions[0].silence()
        self.assertEqual(1, game.players[0].spell_multiplier)
        self.assertEqual(1, game.players[0].heal_multiplier)

    def test_TempleEnforcer(self):
        game = generate_game_for([StonetuskBoar, TempleEnforcer], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[0].card.name)
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[0].calculate_max_health())

        # Temple Enforcer should be played, targeting the Stonetusk Boar
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[1].card.name)
        self.assertEqual(4, game.players[0].minions[1].health)
        self.assertEqual(4, game.players[0].minions[1].calculate_max_health())

    def test_DarkCultist(self):
        game = generate_game_for([StonetuskBoar, DarkCultist], StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual("Dark Cultist", game.current_player.minions[0].card.name)
        self.assertEqual("Stonetusk Boar", game.current_player.minions[1].card.name)
        self.assertEqual(1, game.current_player.minions[1].health)
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(4, game.current_player.minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual("Dark Cultist", game.current_player.minions[0].card.name)
        self.assertEqual("Stonetusk Boar", game.current_player.minions[1].card.name)
        self.assertEqual("Stonetusk Boar", game.current_player.minions[2].card.name)
        self.assertEqual(1, game.current_player.minions[1].health)
        self.assertEqual(4, game.current_player.minions[2].health)
        game.current_player.minions[0].silence()
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(1, game.current_player.minions[0].health)
        self.assertEqual(4, game.current_player.minions[1].health)

    def test_Shrinkmeister(self):
        game = generate_game_for([StonetuskBoar, Shrinkmeister], StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[0].card.name)
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())

        # Play a turn, but don't end it
        game._start_turn()
        game.current_player.agent.do_turn(game.current_player)

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[1].card.name)
        self.assertEqual(0, game.players[0].minions[1].calculate_attack())

    def test_UpgradedRepairBot(self):
        game = generate_game_for(UpgradedRepairBot, MechanicalYeti, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(5, game.other_player.minions[0].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(30, game.other_player.hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(9, game.current_player.minions[1].health)
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(5, game.other_player.minions[0].health)
        self.assertEqual(5, game.other_player.minions[1].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(30, game.other_player.hero.health)

    def test_Shadowbomber(self):
        game = generate_game_for(Shadowbomber, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        game.play_single_turn()
        # Play Shadowbomber, 3 damage to both heroes
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(27, game.players[0].hero.health)
        self.assertEqual(27, game.players[1].hero.health)

    def test_VelensChosen(self):
        game = generate_game_for([AcidicSwampOoze, MindBlast, VelensChosen, MindBlast, MindBlast],
                                 [SoulOfTheForest, MassDispel], OneCardPlayingAgent, OneCardPlayingAgent)

        # Plays Ooze, then Mind Blasts for 5
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(25, game.players[1].hero.health)

        # Velen's on Ooze
        game.play_single_turn()

        self.assertEqual(1, game.players[0].spell_damage)
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

        # Mind Blasts for 6
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(19, game.players[1].hero.health)

        # Mass Dispel, then 5 damage Mind Blast
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, game.players[0].spell_damage)
        self.assertEqual(14, game.players[1].hero.health)

    def test_VelensChosenWithExistingSpellDamage(self):
        game = generate_game_for([KoboldGeomancer, MindBlast, VelensChosen, MindBlast, MindBlast],
                                 [SoulOfTheForest, MassDispel], OneCardPlayingAgent, OneCardPlayingAgent)

        # Plays Kobold, then Mind Blasts for 6
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(24, game.players[1].hero.health)

        # Velen's on Kobold
        game.play_single_turn()

        self.assertEqual(2, game.players[0].spell_damage)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

        # Mind Blasts for 7
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(17, game.players[1].hero.health)

        # Mass Dispel, then 5 damage Mind Blast
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, game.players[0].spell_damage)
        self.assertEqual(12, game.players[1].hero.health)

    def test_Shadowboxer(self):
        game = generate_game_for([Shadowboxer, CircleOfHealing], Whirlwind, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(29, game.players[1].hero.health)

    def test_Lightbomb(self):
        game = generate_game_for([ChillwindYeti, Lightbomb], [ArgentSquire, FaerieDragon, SpiderTank, Deathwing],
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(4, game.players[1].minions[0].health)
        self.assertEqual(2, game.players[1].minions[1].health)
        self.assertEqual(1, game.players[1].minions[2].health)
        self.assertTrue(game.players[1].minions[2].divine_shield)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[1].minions[0].health)
        self.assertEqual(1, game.players[1].minions[1].health)
        self.assertFalse(game.players[1].minions[1].divine_shield)

    def test_LightOfTheNaaru(self):
        game = generate_game_for(MindBlast, LightOfTheNaaru, OneCardPlayingAgent, SelfSpellTestingAgent)
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.players[1].minions))

        # Mind Blast
        game.play_single_turn()

        self.assertEqual(25, game.players[1].hero.health)

        # Double Light of the Naaru but only 1 Lightwarden summoned, 1st Lightwarden buffed by 2nd Light of the Naaru
        game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(3, game.players[1].minions[0].calculate_attack())

    def test_Voljin(self):
        game = generate_game_for(Voljin, ChillwindYeti, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(5, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(2, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(2, game.other_player.minions[0].health)

    def test_Resurrect(self):
        game = generate_game_for([StonetuskBoar, VitalityTotem, Resurrect, BoulderfistOgre], ArcaneShot,
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))

        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[1].card.name)

    def test_Resurrect_WildPyro(self):
        game = generate_game_for([WildPyromancer, StonetuskBoar, Resurrect], Darkbomb,
                                 CardTestingAgent, OneCardPlayingAgent)

        for turn in range(5):
            game.play_single_turn()

        # The wild pyro will be resurrected and then it should go off, killing the boar
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Wild Pyromancer", game.current_player.minions[0].card.name)
        self.assertEqual(1, game.current_player.minions[0].health)

    def test_TwilightWhelp(self):
        game = generate_game_for(TwilightWhelp, Wisp, CardTestingAgent, DoNothingAgent)

        for turn in range(5):
            game.play_single_turn()

        self.assertEqual(6, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(1, game.players[0].minions[0].calculate_max_health())
        self.assertEqual(3, game.players[0].minions[5].calculate_max_health())
