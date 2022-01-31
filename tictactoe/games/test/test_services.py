from unittest import TestCase
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from tictactoe.users.test.factories import UserFactory
from tictactoe.games.models import Game
from tictactoe.games.services import GameService


User = get_user_model()


class TestGameService(TestCase):
    def setUp(self) -> None:
        self.player_1 = UserFactory()
        self.player_2 = UserFactory()
        self.player_3 = UserFactory()
        self.game = Game.objects.create()

    def test_setting_up_player(self):
        GameService.set_up_player(self.game, self.player_1)

        self.assertEqual(
            set([self.player_1, None]), set([self.game.player_1, self.game.player_2])
        )

    def test_join_game(self):
        GameService.set_up_player(self.game, self.player_1)
        results = GameService.join_game(self.game, self.player_2)

        self.assertEqual("Joined a game", results["status"])
        self.assertTrue(
            self.game.is_user_in_game(self.player_1)
        )

    def test_join_game_by_the_game_creator(self):
        GameService.set_up_player(self.game, self.player_1)
        results = GameService.join_game(self.game, self.player_1)

        self.assertEqual("You already joined this game", results["error"])
        self.assertTrue(self.game.is_user_in_game(self.player_1))

    def test_join_game_by_the_same_player_twice(self):
        GameService.set_up_player(self.game, self.player_1)
        GameService.join_game(self.game, self.player_2)
        results = GameService.join_game(self.game, self.player_2)

        self.assertEqual("You already joined this game", results["error"])
        self.assertTrue(self.game.is_user_in_game(self.player_2))

    def test_join_full_game(self):
        GameService.set_up_player(self.game, self.player_1)
        GameService.join_game(self.game, self.player_2)
        results = GameService.join_game(self.game, self.player_3)

        self.assertEqual("This game is already full", results["error"])
        self.assertFalse(self.game.is_user_in_game(self.player_3))
        self.assertTrue(self.game.is_user_in_game(self.player_1))
        self.assertTrue(self.game.is_user_in_game(self.player_2))

    def _prepare_game(self):
        GameService.set_up_player(self.game, self.player_1)
        GameService.join_game(self.game, self.player_2)
        self.player_1 = self.game.player_1
        self.player_2 = self.game.player_2
        self.game.status = "in_progress"

    def _move_and_get_expected_move_results(self, game, player, row, column):
        results = GameService.move(game, {"row": row, "column": column}, player)["move"]

        expected_results = {
            "id": results.id,
            "game": game.id,
            "player": player.id,
            "row": row,
            "column": column,
            "mark": "o" if player == game.player_1 else "x",
        }

        return (model_to_dict(results), expected_results)

    def test_move(self):
        self._prepare_game()
        results, expected_results = self._move_and_get_expected_move_results(
            self.game, self.player_1, 0, 0
        )

        self.assertEqual(expected_results, results)

        results, expected_results = self._move_and_get_expected_move_results(
            self.game, self.player_2, 1, 1
        )

        self.assertEqual(expected_results, results)

    def test_move_when_not_part_of_game(self):
        self._prepare_game()
        results = GameService.move(self.game, {"row": 0, "column": 0}, self.player_3)

        self.assertEqual("You are not part of this game", results["error"])

    def test_move_when_game_is_finished(self):
        self._prepare_game()
        self.game.status = "finished"
        results = GameService.move(self.game, {"row": 0, "column": 0}, self.player_1)

        self.assertEqual("This game has already finished", results["error"])

    def test_move_when_game_not_started(self):
        self._prepare_game()
        self.game.status = "not_started"
        results = GameService.move(self.game, {"row": 0, "column": 0}, self.player_1)

        self.assertEqual("Wait for the other player to join", results["error"])

    def test_move_when_not_players_turn(self):
        self._prepare_game()
        results = GameService.move(self.game, {"row": 0, "column": 0}, self.player_2)

        self.assertEqual("This is not your turn now", results["error"])

    def test_player_row_win(self):
        self._prepare_game()
        self._move_and_get_expected_move_results(self.game, self.player_1, 0, 2)

        for i in range(2):
            self._move_and_get_expected_move_results(self.game, self.player_2, 1, i)
            self._move_and_get_expected_move_results(self.game, self.player_1, 0, i)

        self.assertEqual("finished", self.game.status)
        self.assertEqual(self.player_1, self.game.winner)

    def test_player_col_win(self):
        self._prepare_game()

        for i in range(3):
            if i == 2:
                self._move_and_get_expected_move_results(self.game, self.player_1, i, 1)
            else:
                self._move_and_get_expected_move_results(self.game, self.player_1, i, 0)
            self._move_and_get_expected_move_results(self.game, self.player_2, i, 2)

        self.assertEqual("finished", self.game.status)
        self.assertEqual(self.player_2, self.game.winner)

    def test_player_p_diag_win(self):
        self._prepare_game()

        for i in range(3):
            if i == 2:
                self._move_and_get_expected_move_results(self.game, self.player_1, 2, 0)
            else:
                self._move_and_get_expected_move_results(self.game, self.player_1, i, 2)
            self._move_and_get_expected_move_results(self.game, self.player_2, i, i)

        self.assertEqual("finished", self.game.status)
        self.assertEqual(self.player_2, self.game.winner)

    def test_player_n_diag_win(self):
        self._prepare_game()

        for i in range(3):
            if i == 2:
                self._move_and_get_expected_move_results(self.game, self.player_1, 2, 2)
            else:
                self._move_and_get_expected_move_results(self.game, self.player_1, i, 0)
            self._move_and_get_expected_move_results(self.game, self.player_2, 2-i, i)

        self.assertEqual("finished", self.game.status)
        self.assertEqual(self.player_2, self.game.winner)

    def test_draw(self):
        self._prepare_game()
        player_1_moves = [
            (1, 2),
            (2, 0),
            (0, 1),
            (2, 1),
        ]
        player_2_moves = [
            (0, 2),
            (1, 0),
            (1, 1),
            (2, 2),
        ]

        self._move_and_get_expected_move_results(self.game, self.player_1, 0, 0)
        for p1, p2 in zip(player_1_moves, player_2_moves):
            self._move_and_get_expected_move_results(self.game, self.player_2, *p2)
            self._move_and_get_expected_move_results(self.game, self.player_1, *p1)

        self.assertEqual("finished", self.game.status)
        self.assertEqual(None, self.game.winner)
