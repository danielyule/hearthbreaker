import random
import unittest

from hearthbreaker.agents.basic_agents import PredictableBot, DoNothingBot
from tests.agents.testing_agents import MinionPlayingAgent, SpellTestingAgent, SelfSpellTestingAgent, \
    PredictableAgentWithoutHeroPower, OneSpellTestingAgent, EnemyMinionSpellTestingAgent
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *


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
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(1, game.current_player.minions[3].calculate_attack())

        # Add a new boar on the left of the wolf since we haven't tested that yet
        boar.summon(game.current_player, game, 1)
        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[3].calculate_attack())
        self.assertEqual(1, game.current_player.minions[4].calculate_attack())

        game.current_player.minions[1].die(None)
        game.current_player.minions[1].activate_delayed()
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(1, game.current_player.minions[3].calculate_attack())

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
        self.assertEqual(4, game.current_player.hero.health)

        # The fireball should hit the abomination, which will cause it to go off
        # The soul of the forest will then activate, which will create a Treant.
        # The Second fireball will then hit the treant, so the enemy hero will only
        # be damaged by the Abomination deathrattle
        game.play_single_turn()
        self.assertEqual(2, game.other_player.hero.health)

    def test_SpellBreaker(self):
        game = generate_game_for(Spellbreaker, LeperGnome, SpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions[0].effects))
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

        def choose_1(max, player):
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

    def test_ExtraSpitefulSmith(self):
        game = generate_game_for([LightsJustice, CircleOfHealing], MortalCoil, MinionPlayingAgent, OneSpellTestingAgent)
        smith = SpitefulSmith()
        smith.summon(game.players[0], game, 0)
        for turn in range(0, 3):
            game.play_single_turn()  # Circle to heal spiteful

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

        # One knife to each of the boars
        self.assertFalse(game.current_player.minions[1].stealth)
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].health)

    def test_KnifeJugglerWithOwl(self):
        game = generate_game_for([KnifeJuggler, IronbeakOwl], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        # The owl should silence the knife juggler, and no knives should be thrown
        self.assertEqual(30, game.other_player.hero.health)
        self.assertEqual(0, len(game.current_player.minions[1].effects))

    def test_KnifeJugglerandMCT(self):
        game = generate_game_for(KnifeJuggler, [ChillwindYeti, MindControlTech],
                                 MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        # The MCT should take a knife juggler.  This knife jugger's knife should go off as a consequence of the
        # MCT being added to the board.  See http://www.hearthhead.com/card=734/mind-control-tech#comments:id=1925580
        self.assertEqual(29, game.other_player.hero.health)

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
        game = generate_game_for(LeperGnome, [MortalCoil, LeperGnome],
                                 SpellTestingAgent, PredictableAgentWithoutHeroPower)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(28, game.players[1].hero.health)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(20, game.players[1].hero.health)
        self.assertEqual(28, game.players[0].hero.health)

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))

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
        game = generate_game_for([TheBeast, PowerOverwhelming], [KnifeJuggler, MindControl],
                                 OneSpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 13):
            game.play_single_turn()
        # Beast dies to Siphon Soul and summons us a Finkle Einhorn, so Juggler knifes enemy hero
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(29, game.players[0].hero.health)

    def test_VentureCoMercenary(self):
        game = generate_game_for([VentureCoMercenary, Silence], StonetuskBoar, OneSpellTestingAgent, DoNothingBot)
        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(0, game.players[0].hand[0].mana_cost(game.players[0]))
        self.assertEqual(8, game.players[0].hand[1].mana_cost(game.players[0]))

        game.play_single_turn()

        self.assertEqual(5, game.players[0].hand[0].mana_cost(game.players[0]))
        self.assertEqual(0, game.players[0].hand[1].mana_cost(game.players[0]))

    def test_Demolisher(self):
        game = generate_game_for(Demolisher, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(4, game.players[0].minions[1].health)
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(28, game.players[1].hero.health)

    def test_Doomsayer(self):
        game = generate_game_for(Doomsayer, StonetuskBoar, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

    def test_MasterSwordsmith(self):
        game = generate_game_for(MasterSwordsmith, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())

    def test_InjuredBlademaster(self):
        game = generate_game_for([InjuredBlademaster, CircleOfHealing], StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].health)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(7, game.players[0].minions[0].health)

    def test_Gruul(self):
        game = generate_game_for(Gruul, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 16):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(9, game.players[0].minions[0].calculate_attack())
        self.assertEqual(9, game.players[0].minions[0].health)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(8, game.players[0].minions[0].calculate_attack())
        self.assertEqual(8, game.players[0].minions[0].health)
        self.assertEqual(10, game.players[0].minions[1].calculate_attack())
        self.assertEqual(10, game.players[0].minions[1].health)

    def test_Hogger(self):
        game = generate_game_for(Hogger, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].health)

    def test_ImpMaster(self):
        game = generate_game_for([ImpMaster, MindControl], StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual("Imp", game.players[0].minions[0].card.name)

    def test_NatPagle(self):
        game = generate_game_for([NatPagle, MindControl], StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(4, len(game.players[0].hand))

        game.play_single_turn()
        game.play_single_turn()
        # Draw failed
        self.assertEqual(5, len(game.players[0].hand))

        game.play_single_turn()
        game.play_single_turn()
        # Draw successful
        self.assertEqual(7, len(game.players[0].hand))

    def test_RagnarosTheFirelord(self):
        game = generate_game_for(RagnarosTheFirelord, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)
        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(22, game.players[1].hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(6, game.players[1].hero.health)
        # 3 rag balls to the face, but no attacks

    def test_AncientWatcher(self):
        game = generate_game_for(AncientWatcher, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(30, game.players[1].hero.health)

    def test_ColdlightOracle(self):
        game = generate_game_for(ColdlightOracle, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(9, len(game.players[1].hand))

    def test_ColdlightSeer(self):
        game = generate_game_for(ColdlightSeer, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(5, game.players[0].minions[1].health)

    def test_GrimscaleOracle(self):
        game = generate_game_for(GrimscaleOracle, [MurlocRaider, ArcaneExplosion],
                                 MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(4, game.players[1].minions[0].calculate_attack())
        self.assertEqual(1, game.players[1].minions[0].health)

        game.play_single_turn()  # Arcane explosion to check aura removal

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[1].minions[0].calculate_attack())
        self.assertEqual(1, game.players[1].minions[0].health)

    def test_MurlocWarleader(self):
        game = generate_game_for(MurlocWarleader, [MurlocRaider, StonetuskBoar], MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(5, game.players[0].minions[1].calculate_attack())
        self.assertEqual(4, game.players[0].minions[1].health)
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual(6, game.players[1].minions[0].calculate_attack())
        self.assertEqual(3, game.players[1].minions[0].health)
        self.assertEqual(1, game.players[1].minions[1].calculate_attack())
        self.assertEqual(1, game.players[1].minions[1].health)
        self.assertEqual(6, game.players[1].minions[2].calculate_attack())
        self.assertEqual(3, game.players[1].minions[2].health)

    def test_BigGameHunter(self):
        game = generate_game_for(BigGameHunter, [StonetuskBoar, EarthElemental], MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))

        game.play_single_turn()

        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))

    def test_BloodsailCorsair(self):
        game = generate_game_for(BloodsailCorsair, [LightsJustice, FieryWarAxe], SpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, game.players[1].hero.weapon.durability)

        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(2, game.players[1].hero.weapon.durability)

        game.play_single_turn()

        self.assertEqual(2, game.players[1].hero.weapon.durability)

        game.play_single_turn()

        self.assertEqual(6, len(game.players[0].minions))
        self.assertIsNone(game.players[1].hero.weapon)

    def test_BloodsailRaider(self):
        game = generate_game_for([BloodsailRaider, LightsJustice], StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)

    def test_CaptainGreenskin(self):
        game = generate_game_for([CaptainGreenskin, LightsJustice], StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].hero.weapon.base_attack)
        self.assertEqual(4, game.players[0].hero.weapon.durability)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].hero.weapon.base_attack)
        self.assertEqual(5, game.players[0].hero.weapon.durability)

    def test_HungryCrab(self):
        game = generate_game_for(HungryCrab, MurlocRaider, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

    def test_ManaWraith(self):
        game = generate_game_for([ManaWraith, Silence], StonetuskBoar, OneSpellTestingAgent, DoNothingBot)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, game.players[0].hand[0].mana_cost(game.players[0]))
        self.assertEqual(3, game.players[0].hand[1].mana_cost(game.players[0]))
        self.assertEqual(2, game.players[1].hand[0].mana_cost(game.players[0]))

        game.play_single_turn()

        self.assertEqual(2, game.players[0].hand[0].mana_cost(game.players[0]))
        self.assertEqual(0, game.players[0].hand[1].mana_cost(game.players[0]))
        self.assertEqual(1, game.players[1].hand[0].mana_cost(game.players[0]))

    def test_MindControlTech(self):
        game = generate_game_for(MindControlTech, StonetuskBoar, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[1].minions))

        game.play_single_turn()

        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))

    def test_MurlocTidecaller(self):
        game = generate_game_for(MurlocTidecaller, MurlocRaider, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[1].minions[0].calculate_attack())
        self.assertEqual(1, game.players[1].minions[0].health)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[1].minions[0].calculate_attack())
        self.assertEqual(1, game.players[1].minions[0].health)

    def test_Onyxia(self):
        game = generate_game_for(Onyxia, MurlocRaider, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 17):
            game.play_single_turn()

        self.assertEqual(7, len(game.players[0].minions))
        self.assertEqual(8, game.players[0].minions[0].calculate_attack())
        self.assertEqual(8, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)

    def test_SouthseaCaptain(self):
        game = generate_game_for(SouthseaCaptain, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(4, game.players[0].minions[1].calculate_attack())
        self.assertEqual(4, game.players[0].minions[1].health)

    def test_SouthseaDeckhand(self):
        game = generate_game_for([SouthseaDeckhand, LightsJustice], StonetuskBoar,
                                 PredictableAgentWithoutHeroPower, DoNothingBot)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(1, len(game.players[0].minions))

        game.play_single_turn()
        # Old minion attacks, equip weapon and attack, new minion gets charge and attacks
        self.assertEqual(25, game.players[1].hero.health)
        self.assertEqual(2, len(game.players[0].minions))

    def test_YoungPriestess(self):
        game = generate_game_for(YoungPriestess, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].health)

    def test_AcolyteOfPain(self):
        game = generate_game_for(AcolyteOfPain, [MortalCoil, ShadowWordPain], MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[0].hand))

        game.play_single_turn()  # Mortal Coils the Acolyte

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[0].hand))

        game.play_single_turn()  # Plays 2nd Acolyte
        game.play_single_turn()  # Pains 1 Acolyte, no draw

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[0].hand))

    def test_CultMaster(self):
        game = generate_game_for([CultMaster, CultMaster, HolyNova], [StonetuskBoar, Assassinate],
                                 MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(6, len(game.players[0].hand))
        self.assertEqual(8, len(game.players[1].hand))

        game.play_single_turn()  # Assassinates 1 Cult Master, other Cult Master draws

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(8, len(game.players[1].hand))

    def test_Secretkeeper(self):
        game = generate_game_for([Secretkeeper, ExplosiveTrap], ExplosiveTrap,
                                 MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

        game.play_single_turn()  # I play a secret

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

        game.play_single_turn()  # He plays a secret

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)

    def test_VioletTeacher(self):
        game = generate_game_for([VioletTeacher, CircleOfHealing], CircleOfHealing,
                                 MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

    def test_GadgetzanAuctioneer(self):
        game = generate_game_for([GadgetzanAuctioneer, CircleOfHealing], CircleOfHealing,
                                 MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(7, len(game.players[0].hand))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(8, len(game.players[0].hand))

    def test_IllidanStormrage(self):
        game = generate_game_for([IllidanStormrage, CircleOfHealing], CircleOfHealing,
                                 MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

    def test_Lightwarden(self):
        game = generate_game_for([Lightwarden, MindControl],
                                 [StonetuskBoar, BoulderfistOgre, BoulderfistOgre, BoulderfistOgre, BoulderfistOgre],
                                 PredictableBot, PredictableBot)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)

        game.play_single_turn()  # Heal Lightwarden

        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

    def test_FlesheatingGhoul(self):
        game = generate_game_for(CircleOfHealing, StonetuskBoar, OneSpellTestingAgent, PredictableAgentWithoutHeroPower)
        ghoul = FlesheatingGhoul()
        ghoul.summon(game.players[0], game, 0)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

        game.play_single_turn()  # Circle
        game.play_single_turn()  # Two Boars into Ghoul

        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(30, game.players[0].hero.health)

    def test_QuestingAdventurer(self):
        game = generate_game_for(QuestingAdventurer, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)
        game.players[0].minions[0].silence()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertEqual(4, game.players[0].minions[2].calculate_attack())
        self.assertEqual(4, game.players[0].minions[2].health)

    def test_GurubashiBerserker(self):
        game = generate_game_for(GurubashiBerserker, MortalCoil, MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

    def test_MadBomber(self):
        game = generate_game_for(MadBomber, StonetuskBoar, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[1].minions))  # 1 hits boar
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(29, game.players[0].hero.health)  # 1 hits us
        self.assertEqual(29, game.players[1].hero.health)  # 1 hits him

    def test_AncientMage(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, AncientMage], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 6):
            game.play_single_turn()

        def _choose_index(card, player):
            return 1
        game.players[0].agent.choose_index = _choose_index

        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[1].health)
        self.assertEqual(1, game.players[0].minions[0].spell_damage)
        self.assertEqual(1, game.players[0].minions[2].spell_damage)
        self.assertEqual(2, game.players[0].spell_damage)

    def test_DefenderOfArgus(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, DefenderOfArgus], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 6):
            game.play_single_turn()

        def _choose_index(card, player):
            return 1
        game.players[0].agent.choose_index = _choose_index

        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertTrue(game.players[0].minions[0].taunt)
        self.assertTrue(game.players[0].minions[2].taunt)
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)
        self.assertEqual(2, game.players[0].minions[2].calculate_attack())
        self.assertEqual(2, game.players[0].minions[2].health)

    def test_SunfuryProtector(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, SunfuryProtector], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 4):
            game.play_single_turn()

        def _choose_index(card, player):
            return 1
        game.players[0].agent.choose_index = _choose_index

        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertTrue(game.players[0].minions[0].taunt)
        self.assertTrue(game.players[0].minions[2].taunt)

    def test_HarrisonJones(self):
        game = generate_game_for(HarrisonJones, LightsJustice, MinionPlayingAgent, SpellTestingAgent)
        game.players[0].max_mana = 3  # Cheat so player 1 has room to draw 4
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[0].hand))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(8, len(game.players[0].hand))

    def test_KingMukla(self):
        game = generate_game_for([KingMukla, MindControl], LightsJustice, MinionPlayingAgent, OneSpellTestingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[1].hand))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(7, len(game.players[1].hand))
        self.assertEqual("Bananas", game.players[1].hand[5].name)
        self.assertEqual("Bananas", game.players[1].hand[6].name)

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(6, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

    def test_LeeroyJenkins(self):
        game = generate_game_for(LeeroyJenkins, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))

    def test_MountainGiant(self):
        game = generate_game_for(MountainGiant, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        game.play_single_turn()

        self.assertEqual(8, game.current_player.hand[0].mana_cost(game.current_player))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(7, game.current_player.hand[0].mana_cost(game.current_player))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(6, game.current_player.hand[0].mana_cost(game.current_player))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(5, game.current_player.hand[0].mana_cost(game.current_player))

        # Play the mountain giant (it costs 4 mana, then the subsequent ones cost 5)
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(5, game.current_player.hand[0].mana_cost(game.current_player))
        self.assertEqual(1, len(game.current_player.minions))

    def test_MoltenGiant(self):
        game = generate_game_for(MoltenGiant, StonetuskBoar, DoNothingBot, DoNothingBot)

        game.play_single_turn()
        self.assertEqual(20, game.current_player.hand[0].mana_cost(game.current_player))

        game.current_player.hero.damage(10, None)
        self.assertEqual(10, game.current_player.hand[0].mana_cost(game.current_player))

        game.current_player.hero.damage(15, None)
        self.assertEqual(0, game.current_player.hand[0].mana_cost(game.current_player))

    def test_SeaGiant(self):
        game = generate_game_for([SeaGiant, SummoningPortal], StonetuskBoar, MinionPlayingAgent, SpellTestingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(9, game.current_player.hand[0].mana_cost(game.current_player))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(7, game.current_player.hand[0].mana_cost(game.current_player))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(4, game.current_player.hand[0].mana_cost(game.current_player))
        self.assertEqual(2, game.current_player.hand[1].mana_cost(game.current_player))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(0, game.current_player.hand[0].mana_cost(game.current_player))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, game.current_player.hand[0].mana_cost(game.current_player))
        self.assertEqual(0, game.current_player.hand[1].mana_cost(game.current_player))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(0, game.current_player.hand[0].mana_cost(game.current_player))

    def test_DreadCorsair(self):
        game = generate_game_for([DreadCorsair, LightsJustice, GladiatorsLongbow],
                                 StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 8):
            game.play_single_turn()  # Play 4 mana dread corsair

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].hand[2].mana_cost(game.players[0]))

        game.play_single_turn()  # Equip LJ and check

        self.assertEqual(1, game.players[0].hero.weapon.base_attack)
        self.assertEqual(3, game.players[0].hand[1].mana_cost(game.players[0]))

        for turn in range(0, 4):
            game.play_single_turn()  # Equip longbow and check

        self.assertEqual(0, game.players[0].hand[0].mana_cost(game.players[0]))

    def test_CaptainsParrot(self):
        game = generate_game_for([CaptainsParrot, DreadCorsair, StonetuskBoar], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[0].hand))
        self.assertEqual(24, game.players[0].deck.left)
        self.assertEqual("Dread Corsair", game.players[0].hand[4].name)

    def test_TinkmasterOverspark(self):
        game = generate_game_for(TinkmasterOverspark, StonetuskBoar, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual("Devilsaur", game.players[1].minions[2].card.name)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual("Devilsaur", game.players[1].minions[2].card.name)
        self.assertEqual("Devilsaur", game.players[1].minions[1].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[1].minions))
        self.assertEqual("Devilsaur", game.players[1].minions[2].card.name)
        self.assertEqual("Devilsaur", game.players[1].minions[3].card.name)
        self.assertEqual("Squirrel", game.players[0].minions[1].card.name)

    def test_AlarmoBot(self):
        game = generate_game_for([AlarmoBot, Sap, Sap, Sap, Sap, Deathwing, Deathwing], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(5, len(game.players[0].hand))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(12, game.players[0].minions[0].health)
        self.assertEqual(6, len(game.players[0].hand))

    def test_EliteTaurenChieftain(self):
        game = generate_game_for(EliteTaurenChieftain, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        game.players[0].max_mana = 4

        game.play_single_turn()

        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(6, len(game.players[1].hand))

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(10, len(game.players[1].hand))
        self.assertEqual("Rogues Do It...", game.players[0].hand[0].name)
        self.assertEqual("I Am Murloc", game.players[0].hand[2].name)
        self.assertEqual("I Am Murloc", game.players[0].hand[4].name)
        self.assertEqual("Rogues Do It...", game.players[0].hand[6].name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(8, len(game.players[0].hand))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual("I Am Murloc", game.players[0].hand[8].name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(7, len(game.players[0].minions))
        self.assertEqual(9, len(game.players[0].hand))

        for i in range(0, 9):
            game.players[0].discard()
        for minion in game.players[0].minions:
            minion.damage(10, None)
            minion.activate_delayed()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual("I Am Murloc", game.players[0].hand[0].name)
        game.players[0].discard()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual("I Am Murloc", game.players[0].hand[0].name)
        game.players[0].discard()

        game.play_single_turn()
        game.play_single_turn()

        for minion in game.players[0].minions:
            minion.damage(10, None)
            minion.activate_delayed()
        self.assertEqual("Rogues Do It...", game.players[0].hand[0].name)
        game.players[0].discard()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual("I Am Murloc", game.players[0].hand[0].name)
        game.players[0].discard()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual("Power of the Horde", game.players[0].hand[0].name)
        # Finally
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(6, len(game.players[0].minions))
        self.assertEqual("Sen'jin Shieldmasta", game.players[0].minions[5].card.name)
        # Ok, that's all 3 cards covered

    def test_MillhouseManastorm(self):
        game = generate_game_for(MillhouseManastorm, SiphonSoul, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))

    def test_PintSizedSummoner(self):
        game = generate_game_for(PintSizedSummoner, SiphonSoul, SpellTestingAgent, SpellTestingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))

        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))  # 1st costs 1, 2nd costs 2

    def test_OldMurkEye(self):
        game = generate_game_for([OldMurkEye, ArcaneExplosion], BluegillWarrior, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())

    def test_Ysera(self):
        game = generate_game_for(Innervate, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        ysera = Ysera()
        ysera.summon(game.players[0], game, 0)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Nightmare", game.players[0].hand[0].name)

        game.play_single_turn()  # Nightmare my own Ysera
        game.play_single_turn()

        self.assertEqual(9, game.players[0].minions[0].calculate_attack())
        self.assertEqual(17, game.players[0].minions[0].health)
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Playful Sister", game.players[0].hand[0].name)
        ysera.summon(game.players[0], game, 0)  # Backup Ysera strats

        game.play_single_turn()  # 1st Ysera Dies to Nightmare, RIP
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Playful Sister", game.players[0].hand[0].name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Playful Sister", game.players[0].hand[0].name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Dream", game.players[0].hand[0].name)

        game.play_single_turn()  # Bounce and replay Ysera
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Nightmare", game.players[0].hand[0].name)
        game.players[0].discard()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Playful Sister", game.players[0].hand[0].name)
        game.players[0].discard()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Nightmare", game.players[0].hand[0].name)
        game.players[0].discard()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Nightmare", game.players[0].hand[0].name)
        game.players[0].discard()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Ysera Awakens", game.players[0].hand[0].name)  # Finally, just 1 left
        self.assertEqual(4, len(game.players[0].minions))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual("Emerald Drake", game.players[0].hand[0].name)  # Oh baby
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(12, game.players[0].minions[0].health)
        self.assertEqual(25, game.players[0].hero.health)
        self.assertEqual(25, game.players[1].hero.health)

        game.play_single_turn()  # Play Emerald Drake and we are done

    def test_YseraOverload(self):
        game = generate_game_for(MindControl, StonetuskBoar, DoNothingBot, DoNothingBot)
        ysera = Ysera()
        ysera.summon(game.players[0], game, 0)
        ysera.summon(game.players[0], game, 1)
        for turn in range(0, 5):
            game.play_single_turn()

    def test_GelbinMekkaTwerk(self):
        game = generate_game_for([GelbinMekkatorque, TwistingNether], StonetuskBoar, OneSpellTestingAgent, DoNothingBot)
        game.players[0].hero.health = 14
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Poultryizer", game.players[0].minions[1].card.name)  # Poly's at start of next turn

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Chicken", game.players[0].minions[0].card.name)  # Poly'd our Gelbin
        self.assertEqual("Poultryizer", game.players[0].minions[1].card.name)

        for turn in range(0, 5):
            game.play_single_turn()  # Twisting to clear and replay Gelbin

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Homing Chicken", game.players[0].minions[1].card.name)
        for i in range(0, 8):
            game.players[0].discard()
        self.assertEqual("Twisting Nether", game.players[0].hand[0].name)

        game.play_single_turn()  # Homing Chicken explodes and you draw, then nether

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual("Gelbin Mekkatorque", game.players[0].hand[0].name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Repair Bot", game.players[0].minions[1].card.name)
        self.assertEqual(20, game.players[0].hero.health)  # Healed damaged hero

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Poultryizer", game.players[0].minions[1].card.name)  # Try again

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Homing Chicken", game.players[0].minions[1].card.name)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Emboldener 3000", game.players[0].minions[1].card.name)  # Last one
        self.assertEqual(6, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())  # Buffed itself
        self.assertEqual(5, game.players[0].minions[1].health)

    def test_LorewalkerCho(self):
        game = generate_game_for(FreezingTrap, SinisterStrike, OneSpellTestingAgent, OneSpellTestingAgent)
        cho = LorewalkerCho()
        cho.summon(game.players[0], game, 0)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(27, game.players[0].hero.health)
        self.assertEqual(5, len(game.players[0].hand))
        self.assertEqual("Sinister Strike", game.players[0].hand[4].name)

        game.play_single_turn()

        self.assertEqual(5, len(game.players[0].hand))
        self.assertEqual("Freezing Trap", game.players[0].hand[4].name)

    def test_WildPyromancer(self):
        game = generate_game_for([WildPyromancer, MindBlast, PowerWordShield], Shieldbearer,
                                 SpellTestingAgent, DoNothingBot)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].health)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual("Wild Pyromancer", game.players[0].hand[0].name)

        game.play_single_turn()
        game.play_single_turn()

        # The two pyros killed each other with the effect after mind blast
        self.assertEqual(0, len(game.players[0].minions))

    def test_FacelessManipulator(self):
        game = generate_game_for(FacelessManipulator, Abomination, EnemyMinionSpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual("Faceless Manipulator", game.players[0].minions[0].card.name)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual("Abomination", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].taunt)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].calculate_max_health())

    def test_NerubianEgg(self):
        game = generate_game_for(NerubianEgg, ShadowBolt, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual("Nerubian Egg", game.players[0].minions[0].card.name)
        self.assertEqual(0, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].calculate_max_health())

        # Shadow Bolt should be played, killing the egg
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual("Nerubian", game.players[0].minions[0].card.name)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].calculate_max_health())

    def test_Maexxna(self):
        game = generate_game_for(Maexxna, [Maexxna, WarGolem, Gruul],
                                 PredictableAgentWithoutHeroPower, PredictableAgentWithoutHeroPower)

        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(2, len(game.current_player.minions))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(2, len(game.current_player.minions))

    def test_HauntedCreeper(self):
        game = generate_game_for(HauntedCreeper, Frostbolt, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual("Spectral Spider", game.players[0].minions[0].card.name)
        self.assertEqual("Spectral Spider", game.players[0].minions[1].card.name)

    def test_HauntedCreeper_overfill(self):
        game = generate_game_for(Blizzard, HauntedCreeper, SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 11):
            game.play_single_turn()

        # The blizzard should kill 4 haunted creepers, but only 7 spiders should be left
        self.assertEqual(7, len(game.other_player.minions))
        for minion in game.other_player.minions:
            self.assertEqual("Spectral Spider", minion.card.name)

    def test_NerubarWeblord(self):
        game = generate_game_for([NerubarWeblord, EarthenRingFarseer], [NoviceEngineer, IronfurGrizzly],
                                 MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.hand[0].mana_cost(game.current_player))
        self.assertEqual(4, game.other_player.hand[0].mana_cost(game.other_player))
        self.assertEqual(3, game.other_player.hand[1].mana_cost(game.other_player))
        game.current_player.minions[0].silence()
        self.assertEqual(3, game.current_player.hand[0].mana_cost(game.current_player))
        self.assertEqual(2, game.other_player.hand[0].mana_cost(game.other_player))
        self.assertEqual(3, game.other_player.hand[1].mana_cost(game.other_player))

    def test_NerubarWeblord_with_combo_and_choose(self):
        game = generate_game_for(NerubarWeblord,
                                 [KeeperOfTheGrove, AncientOfWar, Kidnapper, DefiasRingleader, SI7Agent],
                                 MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(4, game.other_player.hand[0].mana_cost(game.other_player))
        self.assertEqual(7, game.other_player.hand[1].mana_cost(game.other_player))
        self.assertEqual(6, game.other_player.hand[2].mana_cost(game.other_player))
        self.assertEqual(2, game.other_player.hand[3].mana_cost(game.other_player))
        # Skip the coin
        self.assertEqual(3, game.other_player.hand[5].mana_cost(game.other_player))

    def test_UnstableGhoul(self):
        game = generate_game_for([StonetuskBoar, FaerieDragon, GoldshireFootman, Frostbolt], UnstableGhoul,
                                 SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(1, game.current_player.minions[0].health)
        self.assertEqual(1, game.current_player.minions[1].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(30, game.other_player.hero.health)

    def test_Loatheb(self):
        game = generate_game_for(Loatheb, [Assassinate, BoulderfistOgre], MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(10, game.other_player.hand[0].mana_cost(game.other_player))
        self.assertEqual(6, game.other_player.hand[1].mana_cost(game.other_player))

        game.play_single_turn()

        self.assertEqual(5, game.current_player.hand[0].mana_cost(game.current_player))
        self.assertEqual(6, game.current_player.hand[1].mana_cost(game.current_player))

    def test_StoneskinGargoyle(self):
        game = generate_game_for(ConeOfCold,
                                 [NorthshireCleric, StoneskinGargoyle, StoneskinGargoyle, StoneskinGargoyle],
                                 SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(3, game.other_player.minions[0].health)

        game.play_single_turn()
        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].health)
        self.assertEqual(4, game.current_player.minions[1].health)
        self.assertEqual(7, len(game.current_player.hand))
        game.play_single_turn()

        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual(3, game.other_player.minions[0].health)
        self.assertEqual(3, game.other_player.minions[1].health)

        game.other_player.minions[0].silence()

        game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[1].health)
        self.assertEqual(4, game.current_player.minions[2].health)

    def test_SludgeBelcher(self):
        game = generate_game_for(SludgeBelcher, Fireball, MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual(5, game.current_player.minions[0].health)

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertTrue(game.other_player.minions[0].taunt)
        self.assertEqual(2, game.other_player.minions[0].health)

    def test_FaerieDragon(self):
        game = generate_game_for(FaerieDragon, Frostbolt, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))

        def check_no_dragon(targets):
            self.assertNotIn(game.other_player.minions[0], targets)
            return targets[0]

        def check_dragon(targets):
            self.assertIn(game.other_player.minions[0], targets)
            return targets[0]

        game.other_player.agent.choose_target = check_no_dragon

        game.play_single_turn()
        game.play_single_turn()

        game.other_player.agent.choose_target = check_dragon
        game.current_player.minions[0].silence()
        game.play_single_turn()

    def test_BaronRivendare(self):
        game = generate_game_for([BloodmageThalnos, HarvestGolem, BaronRivendare], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        game.current_player.minions[1].die(None)
        game.check_delayed()
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual("Baron Rivendare", game.current_player.minions[0].card.name)
        self.assertEqual("Damaged Golem", game.current_player.minions[1].card.name)
        self.assertEqual("Damaged Golem", game.current_player.minions[2].card.name)
        self.assertEqual("Bloodmage Thalnos", game.current_player.minions[3].card.name)

        # Check silence on the Baron
        self.assertEqual(4, len(game.current_player.hand))
        game.current_player.minions[0].silence()
        game.current_player.minions[3].die(None)
        game.check_delayed()
        self.assertEqual(5, len(game.current_player.hand))

    def test_BaronRivendareFaceless(self):
        game = generate_game_for([HarvestGolem, BaronRivendare, FacelessManipulator], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        # According to http://youtu.be/Psq83bosG60?t=12m, multiple Rivendares will not stack the effect
        game.current_player.minions[2].die(None)
        game.check_delayed()
        self.assertEqual(4, len(game.current_player.minions))

    def test_DancingSwords(self):
        game = generate_game_for(DancingSwords, ShadowBolt, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, len(game.other_player.hand))
        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(9, len(game.current_player.hand))

    def test_Deathlord(self):
        game = generate_game_for(Deathlord, [HauntedCreeper, OasisSnapjaw, Frostbolt, WaterElemental, Pyroblast],
                                 MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))

        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))

        self.assertEqual("Water Elemental", game.other_player.minions[0].card.name)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))

        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(2, len(game.other_player.minions))

        self.assertEqual("Oasis Snapjaw", game.other_player.minions[1].card.name)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, len(game.other_player.minions))

        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))

        self.assertEqual("Water Elemental", game.other_player.minions[2].card.name)

        used_count = 0

        for u in game.other_player.deck.used:
            if u:
                used_count += 1

        self.assertEqual(11, used_count)

    def test_SpectralKnight(self):
        game = generate_game_for(SpectralKnight, Fireball, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))

        def check_no_knight(targets):
            self.assertNotIn(game.other_player.minions[0], targets)
            return targets[0]

        def check_knight(targets):
            self.assertIn(game.other_player.minions[0], targets)
            return targets[0]

        game.other_player.agent.choose_target = check_no_knight

        game.play_single_turn()
        game.play_single_turn()

        game.other_player.agent.choose_target = check_knight
        game.current_player.minions[0].silence()
        game.play_single_turn()

    def test_Reincarnate(self):
        game = generate_game_for([BoulderfistOgre, Reincarnate], SylvanasWindrunner,
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 13):
            game.play_single_turn()

        # Sylvanas will die to the reincarnate, steal the Ogre, then be reborn.
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual("Boulderfist Ogre", game.other_player.minions[0].card.name)
        self.assertEqual("Sylvanas Windrunner", game.other_player.minions[1].card.name)

    def test_Undertaker(self):
        game = generate_game_for([Undertaker, GoldshireFootman, HarvestGolem, AnubarAmbusher], HauntedCreeper,
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual("Goldshire Footman", game.current_player.minions[0].card.name)
        self.assertEqual("Undertaker", game.current_player.minions[1].card.name)
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())

        game.play_single_turn()

        self.assertEqual(1, game.other_player.minions[1].calculate_attack())
        self.assertEqual(2, game.other_player.minions[1].calculate_max_health())

        game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual("Harvest Golem", game.current_player.minions[0].card.name)
        self.assertEqual("Goldshire Footman", game.current_player.minions[1].card.name)
        self.assertEqual("Undertaker", game.current_player.minions[2].card.name)
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(3, game.current_player.minions[2].calculate_max_health())

        game.current_player.minions[2].silence()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, game.current_player.minions[3].calculate_attack())
        self.assertEqual(2, game.current_player.minions[3].calculate_max_health())

    def test_WailingSoul(self):
        game = generate_game_for([StonetuskBoar, HauntedCreeper, IronfurGrizzly, WailingSoul], ScarletCrusader,
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertFalse(game.current_player.minions[3].charge)
        self.assertIsNone(game.current_player.minions[2].deathrattle)
        self.assertFalse(game.current_player.minions[1].taunt)
        self.assertTrue(game.other_player.minions[0].divine_shield)

    def test_ZombieChow(self):
        game = generate_game_for([ZombieChow, ZombieChow, ZombieChow, AuchenaiSoulpriest], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)

        game.play_single_turn()

        game.other_player.hero.health = 10
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Zombie Chow", game.current_player.minions[0].card.name)
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(15, game.other_player.hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Zombie Chow", game.current_player.minions[0].card.name)
        game.current_player.minions[0].silence()
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(15, game.other_player.hero.health)

        # Auchenai Soulpriest causes the zombie chow to damage the opponent hero

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual("Zombie Chow", game.current_player.minions[1].card.name)
        game.current_player.minions[1].die(None)
        game.check_delayed()
        self.assertEqual(10, game.other_player.hero.health)

    def test_Feugen(self):
        game = generate_game_for([Stalagg, Feugen], Assassinate, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        # Stalagg should have been played and assassinated, leaving no minions behind

        self.assertEqual(0, len(game.other_player.minions))

        game.play_single_turn()
        game.play_single_turn()

        # Feugen is assassinated, which should summon Thaddius
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Thaddius", game.other_player.minions[0].card.name)

    def test_Stalagg(self):
        game = generate_game_for([Feugen, Stalagg], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 9):
            game.play_single_turn()

        # Feugen should have been played we will silence and kill him, which should still summon Thaddius so long as
        # Stalagg isn't also silenced

        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].silence()
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(0, len(game.current_player.minions))

        game.play_single_turn()
        game.play_single_turn()

        # Stalagg is played,  We will kill him, which should summon Thaddius
        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual("Thaddius", game.current_player.minions[0].card.name)

    def test_Stalagg_Feugen_and_simultaneous_death(self):
        game = generate_game_for([Feugen, Stalagg], [WildGrowth, WildGrowth, TwistingNether],
                                 MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))

        # Twisting Nether should kill both, which should summon Thaddius
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Thaddius", game.other_player.minions[0].card.name)

    def test_MadScientist(self):
        game = generate_game_for([MadScientist, EyeForAnEye, Repentance], BluegillWarrior,
                                 SpellTestingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Mad Scientist", game.current_player.minions[0].card.name)

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.secrets))

        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.secrets))

        game.play_single_turn()

        # Bluegill should cause both secrets to go off
        self.assertEqual(0, len(game.other_player.secrets))

        game.play_single_turn()

        # both secrets and the mad scientist should be down
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Mad Scientist", game.current_player.minions[0].card.name)
        self.assertEqual(2, len(game.current_player.secrets))

        # Because both secrets are already up, no new secrets should be added
        game.current_player.minions[0].die(None)
        self.assertEqual(2, len(game.current_player.secrets))

    def test_EchoingOoze(self):
        game = generate_game_for(EchoingOoze, StoneskinGargoyle, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())
        self.assertEqual(1, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_max_health())
        self.assertEqual(1, game.current_player.minions[3].calculate_attack())
        self.assertEqual(2, game.current_player.minions[3].calculate_max_health())

    def test_EchoingOoze_buff(self):
        game = generate_game_for([BloodfenRaptor, EchoingOoze, BlessingOfMight], StonetuskBoar,
                                 SpellTestingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(4, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())

    def testEchoingOoze_silence(self):
        game = generate_game_for([EchoingOoze, Silence], StoneskinGargoyle, SpellTestingAgent, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        # Even if the Ooze is silenced, it should be copied, since the effect is a battlecry
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())

    def test_EchoingOoze_removal(self):
        game = generate_game_for([IronfurGrizzly, EchoingOoze, Frostbolt], StonetuskBoar,
                                 SpellTestingAgent, DoNothingBot)

        for turn in range(0, 7):
            game.play_single_turn()

        # When the Ooze is removed, it should not be duplicated at turn end
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Ironfur Grizzly", game.current_player.minions[0].card.name)

    def test_EchoingOoze_Faceless(self):
        game = generate_game_for([BoulderfistOgre, EchoingOoze, FacelessManipulator], StonetuskBoar,
                                 SpellTestingAgent, DoNothingBot)

        for turn in range(0, 13):
            game.play_single_turn()

        # Faceless Manipulator should not also be copied.
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())
        self.assertEqual(1, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_max_health())

    def test_ShadeOfNaxxramas(self):
        game = generate_game_for(ShadeOfNaxxramas, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(3, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[1].calculate_max_health())

        game.current_player.minions[0].silence()

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())
        self.assertEqual(4, game.current_player.minions[2].calculate_attack())
        self.assertEqual(4, game.current_player.minions[2].calculate_max_health())

    def test_KelThuzad(self):
        game = generate_game_for([StonetuskBoar, IronfurGrizzly, MagmaRager, KelThuzad], [WarGolem, Flamestrike],
                                 MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))

        game.play_single_turn()

        # All but Kel'Thuzad should have died and then come back to life

        self.assertEqual(4, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].health)

    def test_KelThuzad_with_silence(self):
        game = generate_game_for([StonetuskBoar, IronfurGrizzly, MagmaRager, KelThuzad], [WarGolem, Flamestrike],
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        game.current_player.minions[0].silence()

        game.play_single_turn()

        # The minions should not be brought back

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].health)

    def test_KelThuzad_on_friendly_turn(self):
        game = generate_game_for([StonetuskBoar, IronfurGrizzly, MagmaRager, KelThuzad, Hellfire], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 16):
            game.play_single_turn()

        self.assertEqual(4, len(game.other_player.minions))

        game.play_single_turn()

        # All but Kel'Thuzad should have died and then come back to life, but not the Boars

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(0, len(game.other_player.minions))

    def test_KelThuzad_after_friendly_death(self):
        game = generate_game_for([RagnarosTheFirelord, Naturalize, KelThuzad], StonetuskBoar,
                                 SpellTestingAgent, DoNothingBot)
        for turn in range(0, 17):
            game.play_single_turn()

        self.assertEqual(22, game.other_player.hero.health)
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual("Kel'Thuzad", game.current_player.minions[0].card.name)
        self.assertEqual("Ragnaros the Firelord", game.current_player.minions[1].card.name)
