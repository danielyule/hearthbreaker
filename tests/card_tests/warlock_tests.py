import random
import unittest

from hearthbreaker.agents.basic_agents import PredictableAgent, DoNothingAgent
from tests.agents.testing_agents import OneCardPlayingAgent, EnemySpellTestingAgent, \
    CardTestingAgent, EnemyMinionSpellTestingAgent, PlayAndAttackAgent, HeroPowerAndCardPlayingAgent
from hearthbreaker.constants import MINION_TYPE
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *


class TestWarlock(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_MortalCoil(self):
        game = generate_game_for(BloodfenRaptor, MortalCoil, DoNothingAgent, OneCardPlayingAgent)

        raptor = BloodfenRaptor()
        raptor.summon(game.players[0], game, 0)
        # player 0 plays raptor
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(5, len(game.players[1].hand))

        game.play_single_turn()
        game.play_single_turn()
        # mortal coils the 2hp raptor
        self.assertEqual(5, len(game.players[1].hand))
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()
        # mortal coils the 1hp raptor and draws
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[1].hand))

    def test_MortalCoilDivineShield(self):
        game = generate_game_for(StonetuskBoar, MortalCoil, DoNothingAgent, OneCardPlayingAgent)

        scarlet = ScarletCrusader()
        scarlet.summon(game.players[0], game, 0)
        # player 0 plays Scarlet Crusader
        self.assertTrue(game.players[0].minions[0].divine_shield)
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(5, len(game.players[1].hand))

        game.play_single_turn()
        game.play_single_turn()
        # mortal coils the divine shield, no draw
        self.assertFalse(game.players[0].minions[0].divine_shield)
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(5, len(game.players[1].hand))

        game.play_single_turn()
        game.play_single_turn()
        # mortal coils the 1hp scarlet crusader and draws
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[1].hand))

    def test_FlameImp(self):
        game = generate_game_for(FlameImp, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        game.play_single_turn()
        # play Flame Imp, 3 damage to own hero
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(27, game.players[0].hero.health)

    def test_PitLord(self):
        game = generate_game_for(PitLord, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 7):
            game.play_single_turn()
            # play Pit Lord, 5 damage to own hero
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(25, game.players[0].hero.health)

    def test_DreadInfernal(self):
        game = generate_game_for(DreadInfernal, StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 10):
            game.play_single_turn()
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(5, len(game.players[1].minions))
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        # Plays Dread Infernal, 1 damage to all
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, game.players[0].minions[0].health)
        self.assertEqual(29, game.players[0].hero.health)
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(29, game.players[1].hero.health)

    def test_Felguard(self):
        game = generate_game_for(Felguard, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].max_mana)

        game.play_single_turn()
        # Plays Felguard, destroys mana crystal
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].max_mana)

    def test_Succubus(self):
        game = generate_game_for(Succubus, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[0].hand))

        game.play_single_turn()
        # Plays Succubus, discards
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[0].hand))

    def test_Doomguard(self):
        game = generate_game_for(Doomguard, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(7, len(game.players[0].hand))

        game.play_single_turn()
        # Plays Doomguard, discards twice
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[0].hand))

    def test_Hellfire(self):
        game = generate_game_for(Hellfire, SilverbackPatriarch, CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 6):
            game.play_single_turn()
            # plays 1 Silverback Patriarch
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(4, game.players[1].minions[0].health)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        # Plays Hellfire, 3 damage to all
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].health)
        self.assertEqual(27, game.players[0].hero.health)
        self.assertEqual(27, game.players[1].hero.health)

    def test_ShadowBolt(self):
        game = generate_game_for(ShadowBolt, SilverbackPatriarch, CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 6):
            game.play_single_turn()
            # Plays Silverback Patriarch
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(4, game.players[1].minions[0].health)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        # Uses Shadow Bolt
        self.assertEqual(0, len(game.players[1].minions))

    def test_DrainLife(self):
        game = generate_game_for(DrainLife, MindBlast, EnemySpellTestingAgent, CardTestingAgent)
        for turn in range(0, 4):
            game.play_single_turn()
            # Uses Mind Blast
        self.assertEqual(25, game.players[0].hero.health)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        # Uses Drain Life
        self.assertEqual(27, game.players[0].hero.health)
        self.assertEqual(28, game.players[1].hero.health)

    def test_Soulfire(self):
        game = generate_game_for(Soulfire, StonetuskBoar, EnemySpellTestingAgent, DoNothingAgent)

        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].hand))
        self.assertEqual(26, game.players[1].hero.health)
        game.play_single_turn()
        game.play_single_turn()
        # It should play 2 copies of Soulfire at the enemy hero and discard the remaining copy
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(18, game.players[1].hero.health)
        self.assertEqual(30, game.players[0].hero.health)

    def test_TwistingNether(self):
        game = generate_game_for(TwistingNether, SilverbackPatriarch, CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 14):
            game.play_single_turn()
            # Plays Silverback Patriarch each turn
        self.assertEqual(5, len(game.players[1].minions))

        game.play_single_turn()
        # Plays Twisting Nether
        self.assertEqual(0, len(game.players[1].minions))

    def test_DemonfireEnemy(self):
        game = generate_game_for(Demonfire, FlameImp, EnemyMinionSpellTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 2):
            game.play_single_turn()
            # play Flame Imp, 3 damage to own hero
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(27, game.players[1].hero.health)

        game.play_single_turn()
        # Demonfire to kill enemy Flame Imp
        self.assertEqual(0, len(game.players[1].minions))

    def test_DemonfireAlly(self):
        game = generate_game_for(Demonfire, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        imp = FlameImp()
        imp.summon(game.players[0], game, 0)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(30, game.players[0].hero.health)  # summon doesnt trigger battlecry

        game.play_single_turn()
        # Demonfire to buff own Flame Imp
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())

    def test_DemonfireAllyNonDemon(self):
        game = generate_game_for(Demonfire, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        raptor = BloodfenRaptor()
        raptor.summon(game.players[0], game, 0)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(30, game.players[0].hero.health)

        game.play_single_turn()
        # Demonfire to kill own Raptor
        self.assertEqual(0, len(game.players[0].minions))

    def test_SacrificialPact(self):
        game = generate_game_for(MindBlast, SacrificialPact, CardTestingAgent, CardTestingAgent)
        for turn in range(0, 3):
            game.play_single_turn()
            # Uses 1 Mindblast
        self.assertEqual(25, game.players[1].hero.health)
        imp = FlameImp()
        imp.summon(game.players[0], game, 0)

        game.play_single_turn()
        # Pact the Imp
        self.assertEqual(30, game.players[1].hero.health)

    def test_SiphonSoul(self):
        game = generate_game_for(MindBlast, SiphonSoul, OneCardPlayingAgent, CardTestingAgent)
        for turn in range(0, 11):
            game.play_single_turn()
            # Uses Mindblast for 5 turns
        self.assertEqual(5, game.players[1].hero.health)
        boar = StonetuskBoar()
        boar.summon(game.players[0], game, 0)

        game.play_single_turn()
        # Siphon Soul on the Boar
        self.assertEqual(8, game.players[1].hero.health)

    def test_SenseDemons(self):
        game = generate_game_for([SenseDemons, Doomguard], StonetuskBoar, CardTestingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()
        self.assertEqual(5, len(game.players[0].hand))

        game.play_single_turn()
        # plays Sense Demons and draws 2 Doomguards
        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual('Doomguard', game.players[0].hand[5].name)
        self.assertEqual('Doomguard', game.players[0].hand[6].name)

        for turn in range(0, 4):
            game.play_single_turn()

    def test_SenseDemonsNoDemons(self):
        game = generate_game_for(SenseDemons, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()
        self.assertEqual(5, len(game.players[0].hand))

        game.play_single_turn()
        # plays Sense Demons and draws 2 Worthless Imps
        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual('Worthless Imp', game.players[0].hand[5].name)
        self.assertEqual('Worthless Imp', game.players[0].hand[6].name)

        game.play_single_turn()
        game.play_single_turn()
        # Sense Demons again
        self.assertEqual(9, len(game.players[0].hand))

        game.play_single_turn()
        game.play_single_turn()
        # Sense Demons again
        self.assertEqual(10, len(game.players[0].hand))
        self.assertEqual(0, len(game.players[0].minions))

        for turn in range(0, 4):
            game.play_single_turn()
        # Play 3 copies of Sense Demons and then 2 copies of Worthless Imp
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Worthless Imp", game.players[0].minions[0].card.name)
        self.assertEqual("Worthless Imp", game.players[0].minions[1].card.name)

    def test_SenseDemonsOverflow(self):
        game = generate_game_for([SenseDemons, SenseDemons, SenseDemons, FlameImp, FlameImp], Wisp,
                                 OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()
        self.assertEqual(5, len(game.players[0].hand))

        # Sense Demons to draw 2 Flame Imps
        game.play_single_turn()

        self.assertEqual(7, len(game.players[0].hand))

        # Sense Demons to draw 2 more Flame Imps
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(9, len(game.players[0].hand))

        # Sense Demons to draw 2 more Flame Imps, but 1 gets destroyed
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(10, len(game.players[0].hand))

    def test_BaneOfDoom(self):
        game = generate_game_for(BaneOfDoom, StonetuskBoar, EnemyMinionSpellTestingAgent, DoNothingAgent)
        imp = FlameImp()
        imp.summon(game.players[1], game, 0)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))

        game.play_single_turn()
        # Kills enemy Imp with Bane of Doom and summons random demon
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(MINION_TYPE.DEMON, game.players[0].minions[0].card.minion_type)

        # Banes the Mogushan but does not kill it
        mogu = MogushanWarden()
        mogu.summon(game.players[1], game, 0)
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(5, game.players[1].minions[0].health)

    def test_Corruption(self):
        game = generate_game_for(Corruption, StonetuskBoar, EnemyMinionSpellTestingAgent, DoNothingAgent)
        imp = FlameImp()
        imp.summon(game.players[1], game, 0)
        self.assertEqual(1, len(game.players[1].minions))

        game.play_single_turn()
        # Casts Corruption on enemy Imp
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(3, len(game.players[0].hand))

        game.play_single_turn()
        # Enemy minion still alive until start of my turn
        self.assertEqual(1, len(game.players[1].minions))

        game.play_single_turn()
        # Corruption resolves at start of my turn, no targets to use remaining cards on
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))

    def test_PowerOverwhelming(self):
        game = generate_game_for(PowerOverwhelming, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        imp = FlameImp()
        imp.summon(game.players[0], game, 0)
        self.assertEqual(1, len(game.players[0].minions))

        def verify_poweroverwhelming():
            self.assertEqual(7, game.players[0].minions[0].calculate_attack())
            self.assertEqual(6, game.players[0].minions[0].health)

        game.players[0].minions[0].bind("health_changed", verify_poweroverwhelming)
        game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[0].hand))

    def test_Shadowflame(self):
        game = generate_game_for(Shadowflame, Shieldbearer, CardTestingAgent, OneCardPlayingAgent)
        imp = FlameImp()
        imp.summon(game.players[0], game, 0)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual(4, game.players[1].minions[0].health)
        self.assertEqual(4, game.players[1].minions[1].health)
        self.assertEqual(4, game.players[1].minions[2].health)
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        # Uses Shadowflame on own Flame Imp
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].health)
        self.assertEqual(1, game.players[1].minions[1].health)
        self.assertEqual(1, game.players[1].minions[2].health)
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(30, game.players[1].hero.health)

    def test_SummoningPortal(self):
        game = generate_game_for([SummoningPortal, Wisp], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual('Wisp', game.players[0].hand[0].name)
        self.assertEqual(0, game.players[0].hand[0].mana_cost())

    def test_SummoningPortal_Mechwarper(self):
        game = generate_game_for([SummoningPortal, Mechwarper, SpiderTank], StonetuskBoar,
                                 OneCardPlayingAgent, DoNothingAgent)
        for turn in range(9):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(0, game.current_player.hand[0].mana_cost())

    def test_BloodImp(self):
        game = generate_game_for(BloodImp, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertTrue(game.players[0].minions[0].stealth)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertTrue(game.players[0].minions[0].stealth)
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertTrue(game.players[0].minions[1].stealth)

    def test_Jaraxxus(self):
        game = generate_game_for(LordJaraxxus, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)
        for turn in range(0, 17):
            game.play_single_turn()

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(15, game.current_player.hero.health)
        self.assertEqual(15, game.current_player.hero.calculate_max_health())
        self.assertEqual(27, game.other_player.hero.health)

        game.current_player.agent = PredictableAgent()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(6, game.current_player.minions[0].calculate_attack())
        self.assertEqual(6, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(8, game.current_player.mana)
        self.assertEqual(24, game.other_player.hero.health)

    def test_Jaraxxus_with_secrets(self):
        class SecretTester(DoNothingAgent):
            def __init__(self):
                super().__init__()
                self.turn = 0

            def do_turn(self, player):
                self.turn += 1
                if self.turn >= 8:
                    player.game.play_card(player.hand[0])

        game = generate_game_for(LordJaraxxus, [Repentance, Snipe, MirrorEntity], CardTestingAgent, SecretTester)

        for turn in range(0, 17):
            game.play_single_turn()

        # Jaraxxus should be played, Repentance should activate, leaving
        # the hero with one health and one max health
        # See http://www.reddit.com/r/hearthstone/comments/218vsu/jaraxxus_and_sword_of_justice_rule_inconsistency_o/

        self.assertEqual(1, game.current_player.hero.health)
        self.assertEqual(1, game.current_player.hero.calculate_max_health())

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(11, game.current_player.hero.health)
        self.assertEqual(15, game.current_player.hero.calculate_max_health())

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(15, game.current_player.hero.health)
        self.assertEqual(15, game.current_player.hero.calculate_max_health())
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Lord Jaraxxus", game.other_player.minions[0].card.name)

    def test_Jaraxxus_Repentance_Snipe(self):
        game = generate_game_for(LordJaraxxus, [Repentance, Snipe], OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(17):
            game.play_single_turn()

        # Based on https://www.youtube.com/watch?v=n8u2Senk_XU
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(0, game.current_player.hero.health)
        self.assertTrue(game.current_player.hero.dead)
        self.assertTrue(game.game_ended)

    def test_Jaraxxus_with_SacrificialPact(self):
        game = generate_game_for(LordJaraxxus, SacrificialPact, CardTestingAgent, CardTestingAgent)

        for turn in range(0, 18):
            game.play_single_turn()

        # Sacrificial pact will target Jaraxxus, killing him instantly
        # See http://www.hearthhead.com/card=163/sacrificial-pact#comments:id=1889015
        self.assertTrue(game.other_player.hero.dead)
        self.assertTrue(game.game_ended)

    def test_VoidTerror(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, VoidTerror], StonetuskBoar,
                                 OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        def _choose_index(card, player):
            return 1
        game.players[0].agent.choose_index = _choose_index

        self.assertEqual(2, len(game.players[0].minions))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(5, game.players[0].minions[0].health)

    def test_Voidcaller(self):
        game = generate_game_for(Assassinate, [Voidcaller, FlameImp, ArgentSquire, BoulderfistOgre, StonetuskBoar],
                                 CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Voidcaller", game.current_player.minions[0].card.name)

        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Flame Imp", game.other_player.minions[0].card.name)

    def testAnimaGolem(self):
        game = generate_game_for([Loatheb, AnimaGolem, TwistingNether, AnimaGolem], StonetuskBoar,
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        # Loatheb should be played
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Loatheb", game.other_player.minions[0].card.name)
        self.assertEqual(5, len(game.current_player.minions))

        # The golem should be played, and live past the end of its turn, because of Loatheb
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual("Anima Golem", game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        # Twisting Nether is played, removing everything from the board
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))

        # The golem is played alone, which results in its death at the end of the turn
        game.play_single_turn()
        self.assertEqual(0, len(game.current_player.minions))

    def test_Darkbomb(self):
        game = generate_game_for(Darkbomb, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(27, game.players[1].hero.health)

    def test_DemonheartEnemy(self):
        game = generate_game_for(Demonheart, FlameImp, EnemyMinionSpellTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(4, len(game.players[1].minions))

        game.play_single_turn()
        # Demonheart to kill enemy Flame Imp
        self.assertEqual(3, len(game.players[1].minions))

    def test_DemonheartAlly(self):
        game = generate_game_for(Demonheart, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        imp = FlameImp()
        imp.summon(game.players[0], game, 0)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))

        game.play_single_turn()
        # Demonheart to buff own Flame Imp
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(8, game.players[0].minions[0].calculate_attack())
        self.assertEqual(7, game.players[0].minions[0].health)

    def test_DemonheartAllyNonDemon(self):
        game = generate_game_for(Demonheart, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        raptor = BloodfenRaptor()
        raptor.summon(game.players[0], game, 0)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))

        game.play_single_turn()
        # Demonheart to kill own Raptor
        self.assertEqual(0, len(game.players[0].minions))

    def test_FelCannon(self):
        game = generate_game_for([FelCannon, BoulderfistOgre], [BloodfenRaptor, HarvestGolem, Deathwing],
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(6):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))

        # Fel Cannon should target the Bloodfen Raptor
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Harvest Golem", game.other_player.minions[0].card.name)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        # Fel Cannon should target nothing
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Harvest Golem", game.other_player.minions[0].card.name)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        # Fel Cannon should target ogre

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Harvest Golem", game.other_player.minions[0].card.name)
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(5, game.current_player.minions[1].health)

    def test_ImpLosion(self):
        game = generate_game_for([Implosion, OgreMagi], [SpiderTank, Whirlwind],
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 7):
            game.play_single_turn()

        # Rolls 4, killing Spider
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

        # Whirlwind clears, Ogre, Spider, Implosion
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        # Rolls 3 + 1 spell damage, killing Spider
        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

        # Whirlwind clears except Ogre, Ogre, Spider, Implosion
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        # Rolls 2 + 2 spell damage, rip Spider
        self.assertEqual(6, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

    def test_MalGanis(self):
        game = generate_game_for([FlameImp, MalGanis], FlameImp, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(17):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertTrue(game.current_player.hero.immune)
        self.assertFalse(game.other_player.hero.immune)
        self.assertEqual(5, game.current_player.minions[1].calculate_attack())
        self.assertEqual(4, game.current_player.minions[1].calculate_max_health())
        self.assertEqual(9, game.current_player.minions[0].calculate_attack())
        self.assertEqual(7, game.current_player.minions[0].calculate_max_health())

        for minion in game.other_player.minions:
            self.assertEqual(3, minion.calculate_attack())
            self.assertEqual(2, minion.calculate_max_health())

    def test_FloatingWatcher(self):
        game = generate_game_for(FloatingWatcher, Hellfire, HeroPowerAndCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(13):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(9, game.current_player.hero.health)
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())

        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(6, game.other_player.hero.health)
        self.assertEqual(4, game.other_player.minions[0].calculate_attack())
        self.assertEqual(4, game.other_player.minions[0].calculate_max_health())

        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.hero.health)
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(6, game.current_player.minions[1].calculate_attack())
        self.assertEqual(6, game.current_player.minions[1].calculate_max_health())

    def test_MistressOfPain(self):
        game = generate_game_for([MistressOfPain, AbusiveSergeant], SinisterStrike,
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(5):
            game.play_single_turn()

        self.assertEqual(27, game.current_player.hero.health)

    def test_MistressOfPain_Auchenai(self):
        game = generate_game_for([MistressOfPain, AuchenaiSoulpriest], SinisterStrike,
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(7):
            game.play_single_turn()

        self.assertEqual(0, game.current_player.hero.health)
        self.assertTrue(game.current_player.hero.dead)

    def test_MistressOfPain_DivineShield(self):
        game = generate_game_for(MistressOfPain, [SinisterStrike, ArgentSquire],
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(5):
            game.play_single_turn()

        # The mistress of pain does no damage, so the hero isn't healed
        # See https://www.youtube.com/watch?v=wakqQSBjDdE
        self.assertEqual(27, game.current_player.hero.health)

    def test_MistressOfPain_saves_hero(self):
        # based on http://youtu.be/_Z2ZU-cIoG8?t=1m3s
        game = generate_game_for([MistressOfPain, Demonfire], Misdirection, PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(4):
            game.play_single_turn()

        game.players[0].hero.health = 2

        game.play_single_turn()

        self.assertFalse(game.game_ended)

    def test_ImpGangBoss(self):
        game = generate_game_for(ImpGangBoss, [MortalCoil, ShadowWordPain], OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))

        game.play_single_turn()  # Mortal Coils the gang boss

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Imp", game.players[0].minions[1].card.name)

        game.play_single_turn()  # Plays 2nd Gang Boss
        game.play_single_turn()  # Pains 1 Boss, no damage

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Imp Gang Boss", game.players[0].minions[0].card.name)
        self.assertEqual("Imp", game.players[0].minions[1].card.name)

    def test_Demonwrath(self):
        game = generate_game_for(Demonwrath, [Voidwalker, RiverCrocolisk], OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(5):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].health)  # Beast damaged
        self.assertEqual(3, game.players[1].minions[1].health)  # Voidwalker undamaged
