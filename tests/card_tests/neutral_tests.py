import random
import unittest

from hsgame.agents.basic_agents import DoNothingBot, PredictableBot
from tests.testing_agents import *
from tests.testing_utils import generate_game_for
from hsgame.cards import *


class TestCommon(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_NoviceEngineer(self):
        game = generate_game_for(NoviceEngineer, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].health)
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual("Novice Engineer", game.current_player.minions[0].card.name)

        # Three cards to start, two for the two turns and one from the battlecry
        self.assertEqual(24, game.current_player.deck.left)

    def test_KoboldGeomancer(self):
        game = generate_game_for(KoboldGeomancer, IronbeakOwl, MinionPlayingAgent, MinionPlayingAgent)

        for i in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].spell_damage)
        self.assertEqual(1, game.current_player.spell_damage)

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].health)
        self.assertEqual(2, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(2, game.other_player.minions[0].calculate_attack())
        self.assertEqual(0, game.other_player.minions[0].spell_damage)
        self.assertEqual(0, game.other_player.spell_damage)

    def test_ElvenArcher(self):
        game = generate_game_for(StonetuskBoar, ElvenArcher, MinionPlayingAgent, MinionPlayingAgent)

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].health)
        self.assertEqual(1, game.current_player.minions[0].calculate_max_health())
        self.assertEqual("Elven Archer", game.current_player.minions[0].card.name)

    def test_ArgentSquire(self):
        game = generate_game_for(ArgentSquire, ElvenArcher, MinionPlayingAgent, MinionPlayingAgent)
        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].divine_shield)

        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertFalse(game.other_player.minions[0].divine_shield)

    def test_SilvermoonGuardian(self):
        game = generate_game_for(SilvermoonGuardian, ElvenArcher, MinionPlayingAgent, MinionPlayingAgent)

        for i in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].divine_shield)

        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertFalse(game.other_player.minions[0].divine_shield)

    def test_TwilightDrake(self):
        game = generate_game_for(TwilightDrake, ElvenArcher, MinionPlayingAgent, DoNothingBot)

        for i in range(0, 7):
            game.play_single_turn()

        # 7 cards in hand, Twilight Drake should be played, making it
        # 6 cards left in hand, giving the drake +6 health (a total of 7)
        self.assertEqual(6, len(game.current_player.hand))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(7, game.current_player.minions[0].health)

    def test_DireWolfAlpha(self):
        game = generate_game_for(StonetuskBoar, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        # There should be three Stonetusk Boars on the board
        self.assertEqual(3, len(game.current_player.minions))

        # add a new Dire wolf at index 1
        wolf = DireWolfAlpha()
        wolf.summon(game.current_player, game, 1)

        # The minions to either side should have their attack increased
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(1, game.current_player.minions[3].calculate_attack())

        # When removing the minion at index 0, we should not get an error
        game.current_player.minions[0].die(None)
        game.current_player.minions[0].activate_delayed()
        self.assertEqual(3, len(game.current_player.minions))

        # When removing the minion at index 1, we should have a new minion at index 1,
        # and its attack should be increased
        game.current_player.minions[1].die(None)
        game.current_player.minions[1].activate_delayed()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())

        # Silencing this minion should have no effect on its attack
        game.current_player.minions[1].silence()
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())

        # We should be able to add a boar on either side of the wolf, and their attack should be increased
        # The attack of the boar which used to be next to the wolf should decrease
        boar = StonetuskBoar()
        boar.summon(game.current_player, game, 0)
        boar.summon(game.current_player, game, 2)
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(1, game.current_player.minions[3].calculate_attack())

        # Add a new boar on the left of the wolf since we haven't tested that yet
        boar.summon(game.current_player, game, 1)
        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())

        game.current_player.minions[1].die(None)
        game.current_player.minions[1].activate_delayed()
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())

        # If the wolf is silenced, then the boars to either side should no longer have increased attack
        game.current_player.minions[1].silence()
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[2].calculate_attack())
        self.assertEqual(1, game.current_player.minions[3].calculate_attack())

    def test_DireWolfAlphaWithLightspawn(self):
        game = generate_game_for([DireWolfAlpha, Lightspawn], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())
        self.assertEqual(5, game.current_player.minions[0].health)

        game.current_player.minions[0].silence()

        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(5, game.current_player.minions[0].health)

        game.current_player.minions[1].silence()

        self.assertEqual(0, game.current_player.minions[0].calculate_attack())
        self.assertEqual(5, game.current_player.minions[0].health)

    def test_WorgenInfiltrator(self):
        game = generate_game_for([WorgenInfiltrator, ElvenArcher], [ArcaneShot], MinionPlayingAgent, SpellTestingAgent)
        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].stealth)

        def _choose_target(targets):
            self.assertEqual(2, len(targets))
            return targets[0]

        game.players[0].agent.choose_target = _choose_target
        game.players[1].agent.choose_target = _choose_target
        game.play_single_turn()
        game.play_single_turn()

    def test_OgreMagi(self):
        game = generate_game_for(OgreMagi, IronbeakOwl, MinionPlayingAgent, MinionPlayingAgent)

        for i in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].health)
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].spell_damage)
        self.assertEqual(1, game.current_player.spell_damage)

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].health)
        self.assertEqual(4, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(4, game.other_player.minions[0].calculate_attack())
        self.assertEqual(0, game.other_player.minions[0].spell_damage)
        self.assertEqual(0, game.other_player.spell_damage)

    def test_Archmage(self):
        game = generate_game_for(Archmage, IronbeakOwl, MinionPlayingAgent, MinionPlayingAgent)

        for i in range(0, 11):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, game.current_player.minions[0].health)
        self.assertEqual(7, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].spell_damage)
        self.assertEqual(1, game.current_player.spell_damage)

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(7, game.other_player.minions[0].health)
        self.assertEqual(7, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(4, game.other_player.minions[0].calculate_attack())
        self.assertEqual(0, game.other_player.minions[0].spell_damage)
        self.assertEqual(0, game.other_player.spell_damage)

    def test_DalaranMage(self):
        game = generate_game_for(DalaranMage, IronbeakOwl, MinionPlayingAgent, MinionPlayingAgent)

        for i in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].health)
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].spell_damage)
        self.assertEqual(1, game.current_player.spell_damage)

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].health)
        self.assertEqual(4, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(1, game.other_player.minions[0].calculate_attack())
        self.assertEqual(0, game.other_player.minions[0].spell_damage)
        self.assertEqual(0, game.other_player.spell_damage)

    def test_AzureDrake(self):
        game = generate_game_for(AzureDrake, IronbeakOwl, MinionPlayingAgent, MinionPlayingAgent)

        for i in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].health)
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].spell_damage)
        self.assertEqual(1, game.current_player.spell_damage)
        self.assertEqual(8, len(game.current_player.hand))
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].health)
        self.assertEqual(4, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(4, game.other_player.minions[0].calculate_attack())
        self.assertEqual(0, game.other_player.minions[0].spell_damage)
        self.assertEqual(0, game.other_player.spell_damage)

    def test_Malygos(self):
        game = generate_game_for([Malygos, MindBlast], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for i in range(0, 17):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].spell_damage)
        self.assertEqual(5, game.current_player.spell_damage)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(20, game.other_player.hero.health)

    def test_Abomination(self):
        game = generate_game_for([Abomination, Abomination, Abomination, Abomination, Abomination, SoulOfTheForest],
                                 Fireball, SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Abomination", game.current_player.minions[0].card.name)

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(28, game.current_player.hero.health)
        self.assertEqual(22, game.other_player.hero.health)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Abomination", game.current_player.minions[0].card.name)
        self.assertEqual(10, game.current_player.hero.health)

        # The fireball should hit the abomination, which will cause it to go off
        # The soul of the forest will then activate, which will create a Treant.
        # The Second fireball will then hit the treant, so the enemy hero will only
        # be damaged by the Abomination deathrattle
        game.play_single_turn()
        self.assertEqual(8, game.other_player.hero.health)

    def test_SpellBreaker(self):
        game = generate_game_for(Spellbreaker, LeperGnome, SpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertTrue(game.other_player.minions[0].silenced)
        game.other_player.minions[0].die(None)
        game.other_player.minions[0].activate_delayed()

        self.assertEqual(30, game.current_player.hero.health)

    def test_BloodmageThalnos(self):
        game = generate_game_for(BloodmageThalnos, StonetuskBoar, MinionPlayingAgent, PredictableBot)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].spell_damage)
        self.assertEqual(1, game.current_player.spell_damage)

        # The other player will now use their hero power to kill Thalnos, drawing a card
        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(5, len(game.other_player.hand))

    def test_AmaniBerserker(self):
        game = generate_game_for([AmaniBerserker, AbusiveSergeant, AmaniBerserker, EarthenRingFarseer], ExplosiveTrap,
                                 PredictableAgentWithoutHeroPower, SpellTestingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())
        self.assertEqual(5, game.current_player.minions[1].calculate_attack())
        self.assertEqual(23, game.other_player.hero.health)

        game.current_player.minions[0].heal(2, None)
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        game.current_player.minions[0].damage(2, None)
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())

        game.current_player.minions[1].silence()
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        game.current_player.minions[1].heal(2, None)
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        game.current_player.minions[1].damage(2, None)
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())

    def test_AmaniBerserkerWithDireWolf(self):
        game = generate_game_for([DireWolfAlpha, AmaniBerserker], StonetuskBoar, MinionPlayingAgent,
                                 DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        game.current_player.minions[0].damage(2, None)
        self.assertEqual(6, game.current_player.minions[0].calculate_attack())
        game.current_player.minions[1].silence()
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(6, game.current_player.minions[1].calculate_attack())
        game.current_player.minions[1].heal(2, None)
        self.assertEqual(3, game.current_player.minions[1].calculate_attack())

    def test_SilverHandKnight(self):
        game = generate_game_for([OasisSnapjaw, SilverHandKnight, SilverHandKnight], StonetuskBoar, MinionPlayingAgent,
                                 DoNothingBot)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual("Silver Hand Knight", game.current_player.minions[0].card.name)
        self.assertEqual("Squire", game.current_player.minions[1].card.name)

        def choose_1(max):
            return 1

        game.players[0].agent.choose_index = choose_1
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual("Silver Hand Knight", game.current_player.minions[0].card.name)
        self.assertEqual("Silver Hand Knight", game.current_player.minions[1].card.name)
        self.assertEqual("Squire", game.current_player.minions[2].card.name)
        self.assertEqual("Squire", game.current_player.minions[3].card.name)

    def test_StormwindChampion(self):
        game = generate_game_for([SilverHandKnight, StormwindChampion], [BoulderfistOgre, Equality],
                                 MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        game.current_player.minions[0].damage(3, None)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(6, game.current_player.minions[0].health)
        self.assertEqual(6, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].health)
        self.assertEqual(5, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[2].health)
        self.assertEqual(3, game.current_player.minions[2].calculate_attack())

        game.play_single_turn()

        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(2, game.other_player.minions[1].health)
        self.assertEqual(2, game.other_player.minions[1].calculate_max_health())
        self.assertEqual(2, game.other_player.minions[2].health)
        self.assertEqual(2, game.other_player.minions[2].calculate_max_health())

        game.other_player.minions[0].silence()

        self.assertEqual(6, game.other_player.minions[0].health)
        self.assertEqual(6, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(1, game.other_player.minions[1].health)
        self.assertEqual(1, game.other_player.minions[1].calculate_max_health())
        self.assertEqual(1, game.other_player.minions[2].health)
        self.assertEqual(1, game.other_player.minions[2].calculate_max_health())

    def test_VoodooDoctor(self):
        game = generate_game_for(VoodooDoctor, StonetuskBoar, SelfSpellTestingAgent, DoNothingBot)

        game.players[0].hero.health = 20

        game.play_single_turn()
        # Heal self
        self.assertEqual(22, game.players[0].hero.health)
        self.assertEqual(1, len(game.players[0].minions))

    def test_EarthenRingFarseer(self):
        game = generate_game_for(EarthenRingFarseer, StonetuskBoar, SelfSpellTestingAgent, DoNothingBot)
        game.players[0].hero.health = 20
        for turn in range(0, 5):
            game.play_single_turn()
        # Heal self
        self.assertEqual(23, game.players[0].hero.health)
        self.assertEqual(1, len(game.players[0].minions))

    def test_Nightblade(self):
        game = generate_game_for(Nightblade, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 9):
            game.play_single_turn()
        self.assertEqual(27, game.players[1].hero.health)
        self.assertEqual(1, len(game.players[0].minions))

    def test_PriestessOfElune(self):
        game = generate_game_for(PriestessOfElune, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        game.players[0].hero.health = 20
        for turn in range(0, 11):
            game.play_single_turn()
        self.assertEqual(24, game.players[0].hero.health)
        self.assertEqual(1, len(game.players[0].minions))

    def test_ArcaneGolem(self):
        game = generate_game_for(ArcaneGolem, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(2, game.players[1].max_mana)
        self.assertEqual(0, len(game.players[0].minions))

        game.play_single_turn()

        self.assertEqual(3, game.players[1].max_mana)
        self.assertEqual(1, len(game.players[0].minions))

    def test_DarkscaleHealer(self):
        game = generate_game_for(DarkscaleHealer, Flamestrike, MinionPlayingAgent, OneSpellTestingAgent)
        game.players[0].hero.health = 20
        for turn in range(0, 8):
            game.play_single_turn()
        self.assertEqual(20, game.players[0].hero.health)

        game.play_single_turn()
        # 1st darkscale healer
        self.assertEqual(22, game.players[0].hero.health)
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()
        # 2nd darkscale healer
        self.assertEqual(24, game.players[0].hero.health)
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()
        # 3rd darkscale healer
        self.assertEqual(26, game.players[0].hero.health)
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(5, game.players[0].minions[1].health)

        game.play_single_turn()
        # Flamestrike
        self.assertEqual(26, game.players[0].hero.health)
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].health)
        self.assertEqual(1, game.players[0].minions[2].health)

        game.play_single_turn()
        # 4th darkscale healer
        self.assertEqual(28, game.players[0].hero.health)
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[1].health)
        self.assertEqual(3, game.players[0].minions[2].health)
        self.assertEqual(3, game.players[0].minions[3].health)

    def test_ShatteredSunCleric(self):
        game = generate_game_for(ShatteredSunCleric, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()
        # 1st ssc
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()
        # 2nd ssc
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(4, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)

    def test_TheBlackKnight(self):
        game = generate_game_for(TheBlackKnight, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 10):
            game.play_single_turn()

        tasdingo = SenjinShieldmasta()
        tasdingo.summon(game.players[0], game, 0)
        tasdingo.summon(game.players[1], game, 0)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

        yeti = ChillwindYeti()
        yeti.summon(game.players[1], game, 0)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual("The Black Knight", game.players[0].minions[0].card.name)
        self.assertEqual("The Black Knight", game.players[0].minions[1].card.name)
        self.assertEqual("Sen'jin Shieldmasta", game.players[0].minions[2].card.name)

    def test_Deathwing(self):
        game = generate_game_for(Deathwing, LordOfTheArena, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 18):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[1].minions))
        self.assertEqual(10, len(game.players[0].hand))
        self.assertEqual(9, len(game.players[1].hand))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(9, len(game.players[1].hand))

    def test_Alexstrasza(self):
        game = generate_game_for(Alexstrasza, StonetuskBoar, SelfSpellTestingAgent, DoNothingBot)
        for turn in range(0, 17):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(15, game.players[0].hero.health)
        self.assertEqual(30, game.players[1].hero.health)

    def test_EmperorCobra(self):
        game = generate_game_for(EmperorCobra, [EmperorCobra, MagmaRager, ChillwindYeti],
                                 PredictableAgentWithoutHeroPower, PredictableAgentWithoutHeroPower)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(2, len(game.current_player.minions))

    def test_CrazedAlchemist(self):
        game = generate_game_for([FlametongueTotem, StormwindChampion, MagmaRager],
                                 [CrazedAlchemist, CrazedAlchemist, BoulderfistOgre],
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].health)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].damage(2, None)

        game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].calculate_attack())
        self.assertEqual(6, game.other_player.minions[0].health)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(3, game.other_player.minions[0].calculate_attack())
        self.assertEqual(7, game.other_player.minions[0].health)

        game.other_player.minions[0].silence()
        self.assertEqual(6, game.other_player.minions[0].calculate_attack())
        self.assertEqual(2, game.other_player.minions[0].health)

    def test_BaronGeddon(self):
        game = generate_game_for(BaronGeddon, MassDispel, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(28, game.players[0].hero.health)
        self.assertEqual(28, game.players[1].hero.health)
        self.assertEqual(5, game.players[0].minions[0].health)

        game.play_single_turn()  # Silences the Baron Geddon on the field
        game.play_single_turn()  # Only the new Baron Geddon triggers

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(26, game.players[0].hero.health)
        self.assertEqual(26, game.players[1].hero.health)
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[1].health)

    def test_AncientBrewmaster(self):
        game = generate_game_for(AncientBrewmaster, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 8):
            game.play_single_turn()
        # Summon first panda, nothing to return
        self.assertEqual(1, len(game.players[0].minions))

        game.play_single_turn()
        # Return 1st panda with 2nd panda
        self.assertEqual(1, len(game.players[0].minions))

    def test_AngryChicken(self):
        game = generate_game_for([AngryChicken, PowerWordShield], [ArcaneExplosion, MassDispel],
                                 OneSpellTestingAgent, SpellTestingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

        game.play_single_turn()
        # Uses Arcane Explosion, enraging the chicken
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)

    def test_AngryChickenHeal(self):
        game = generate_game_for([AngryChicken, PowerWordShield], [ArcaneExplosion, CircleOfHealing],
                                 OneSpellTestingAgent, OneSpellTestingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

        game.play_single_turn()
        # Uses Arcane Explosion, enraging the chicken
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

        game.play_single_turn()  # 2nd chicken
        game.play_single_turn()  # Circle of healing

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)

    def test_SpitefulSmith(self):
        game = generate_game_for(LightsJustice, [MortalCoil, AcidicSwampOoze, CircleOfHealing],
                                 PredictableAgentWithoutHeroPower, OneSpellTestingAgent)
        smith = SpitefulSmith()
        smith.summon(game.players[0], game, 0)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(29, game.players[1].hero.health)  # No enrage, only LJ

        game.play_single_turn()

        self.assertEqual(22, game.players[1].hero.health)  # Enrage LJ for 3 + Smith for 4

        game.play_single_turn()  # Ooze

        self.assertEqual(1, len(game.players[1].minions))

        game.play_single_turn()  # New weapon

        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(27, game.players[0].hero.health)  # Enrage LJ for 3 to kill Ooze
        self.assertEqual(18, game.players[1].hero.health)  # Smith to face for 4

        game.play_single_turn()  # Circle of Healing
        game.play_single_turn()  # Unenraged LJ for 1 + Smith for 4

        self.assertEqual(13, game.players[1].hero.health)

    def test_BloodKnight(self):
        game = generate_game_for(BloodKnight, ArgentSquire, MinionPlayingAgent, MinionPlayingAgent)
        squire = ArgentSquire()
        squire.summon(game.players[0], game, 0)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(12, game.players[0].minions[0].calculate_attack())
        self.assertEqual(12, game.players[0].minions[0].health)
        self.assertFalse(game.players[0].minions[1].divine_shield)
        self.assertFalse(game.players[1].minions[0].divine_shield)
        self.assertFalse(game.players[1].minions[1].divine_shield)

    def test_FrostwolfWarlord(self):
        game = generate_game_for(FrostwolfWarlord, ArgentSquire, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 9):
            game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(4, game.players[0].minions[1].calculate_attack())
        self.assertEqual(4, game.players[0].minions[1].health)

    def test_SummonBattlecries(self):
        game = generate_game_for([MurlocTidehunter, RazorfenHunter, DragonlingMechanic], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 7):
            game.play_single_turn()
        self.assertEqual(6, len(game.players[0].minions))

    def test_AcidicSwampOoze(self):
        game = generate_game_for(AcidicSwampOoze, LightsJustice, SpellTestingAgent, SpellTestingAgent)
        game.play_single_turn()
        game.play_single_turn()

        self.assertTrue(game.current_player.hero.weapon is not None)

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.hero.weapon is None)

    def test_AcidicSwampOozeWithNoWeapon(self):
        game = generate_game_for(AcidicSwampOoze, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        game.play_single_turn()
        game.play_single_turn()

        self.assertTrue(game.current_player.hero.weapon is None)

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.hero.weapon is None)

    def test_KnifeJuggler(self):
        game = generate_game_for([KnifeJuggler, KnifeJuggler, MasterOfDisguise], [StonetuskBoar, GoldshireFootman],
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        # The knife will be thrown into the enemy hero
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(29, game.other_player.hero.health)
        self.assertEqual(2, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[1].health)

        game.play_single_turn()
        game.play_single_turn()

        # One knife to the older Boar, one knife to the footman
        self.assertFalse(game.current_player.minions[1].stealth)
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[1].health)

    def test_CairneBloodhoof(self):
        game = generate_game_for(CairneBloodhoof, SiphonSoul, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual("Baine Bloodhoof", game.players[0].minions[0].card.name)

    def test_TheBeast(self):
        game = generate_game_for(TheBeast, SiphonSoul, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual("Finkle Einhorn", game.players[1].minions[0].card.name)

    def test_HarvestGolem(self):
        game = generate_game_for(HarvestGolem, ShadowBolt, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual("Damaged Golem", game.players[0].minions[0].card.name)

    def test_SylvanasWindrunner(self):
        game = generate_game_for(SylvanasWindrunner, SiphonSoul, MinionPlayingAgent, SpellTestingAgent)
        imp = FlameImp()
        imp.summon(game.players[1], game, 0)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual("Flame Imp", game.players[0].minions[0].card.name)

    def test_StampedingKodo(self):
        game = generate_game_for(StampedingKodo, ArgentSquire, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[1].minions))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))

    def test_FrostElemental(self):
        game = generate_game_for(FrostElemental, ArgentSquire, SelfSpellTestingAgent, DoNothingBot)
        for turn in range(0, 11):
            game.play_single_turn()

        self.assertTrue(game.players[0].hero.frozen)

    def test_LeperGnome(self):
        game = generate_game_for(LeperGnome, MortalCoil, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(28, game.players[1].hero.health)

    def test_ManaAddict(self):
        game = generate_game_for([ManaAddict, ArcaneIntellect], StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 4):
            game.play_single_turn()

        def check_attack(m):
            self.assertEqual(2, game.players[0].minions[0].temp_attack)

        game.players[0].bind("spell_cast", check_attack)
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(0, game.players[0].minions[0].temp_attack)
        self.assertEqual(6, len(game.players[0].hand))

    def test_RagingWorgen(self):
        game = generate_game_for(RagingWorgen, [ArcaneExplosion, ArcaneExplosion, CircleOfHealing],
                                 OneSpellTestingAgent, OneSpellTestingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

        game.play_single_turn()
        # Uses Arcane Explosion, enraging the worgen
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertTrue(game.players[0].minions[0].windfury)

        game.play_single_turn()  # 2nd Raging Worgen
        game.play_single_turn()  # Circle of Healing

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)
        self.assertTrue(not game.players[0].minions[0].windfury)
        self.assertTrue(not game.players[0].minions[1].windfury)

    def test_TaurenWarrior(self):
        game = generate_game_for(TaurenWarrior, [ArcaneExplosion, ArcaneExplosion, CircleOfHealing],
                                 OneSpellTestingAgent, OneSpellTestingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

        game.play_single_turn()
        # Uses Arcane Explosion, enraging the Tauren Warrior
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

        game.play_single_turn()  # 2nd Tauren Warrior
        game.play_single_turn()  # Circle of Healing

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)

    def test_RaidLeader(self):
        game = generate_game_for([Wisp, RaidLeader], [ShadowBolt, MortalCoil, MassDispel],
                                 MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()  # Coils extra wisp
        game.play_single_turn()
        game.play_single_turn()  # Mass Dispel

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)

    def test_KnifeJugglerEdgeCase(self):
        game = generate_game_for(TheBeast, [KnifeJuggler, SiphonSoul],
                                 MinionPlayingAgent, EnemyMinionSpellTestingAgent)
        for turn in range(0, 12):
            game.play_single_turn()
        # Beast dies to Siphon Soul and summons us a Finkle Einhorn, so Juggler knifes enemy hero
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(29, game.players[0].hero.health)

    def test_VentureCoMercenary(self):
        game = generate_game_for([VentureCoMercenary, Silence], StonetuskBoar, OneSpellTestingAgent, DoNothingBot)
        for turn in range(0, 10):
            game.play_single_turn()

        self.assertFalse(game.players[0].minions[0].silenced)
        self.assertEqual(0, game.players[0].hand[0].mana_cost(game.players[0]))
        self.assertEqual(8, game.players[0].hand[1].mana_cost(game.players[0]))
