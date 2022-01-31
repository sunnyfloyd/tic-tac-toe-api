from rest_framework.test import APITestCase
from tictactoe.games.models import Game, Move
from django.contrib.auth import get_user_model


User = get_user_model()


class TestGameModel(APITestCase):
    def setUp(self) -> None:
        self.player_1 = User.objects.create(
            username="player_3", email="p1@example.com", password="D*3nd*&*3jnDI"
        )
        self.player_2 = User.objects.create(
            username="player_4", email="p2@example.com", password="D*3nd*&*3jnDI"
        )
        self.game = Game.objects.create()

    def test_is_user_in_game(self):
        self.assertFalse(self.game.is_user_in_game(self.player_1))
        self.assertFalse(self.game.is_user_in_game(self.player_2))

        self.game.player_1 = self.player_1
        self.game.player_2 = self.player_2
        self.game.save()

        self.assertTrue(self.game.is_user_in_game(self.player_1))
        self.assertTrue(self.game.is_user_in_game(self.player_2))

    def test_is_game_full(self):
        self.assertFalse(self.game.is_full)

        self.game.player_1 = self.player_1
        self.game.save()

        self.assertFalse(self.game.is_full)

        self.game.player_2 = self.player_2
        self.game.save()

        self.assertTrue(self.game.is_full)

    def test_get_next_player_and_mark(self):
        self.assertRaises(ValueError, self.game.get_next_player_and_mark)

        self.game.player_1 = self.player_1
        self.game.player_2 = self.player_2
        self.game.save()

        self.assertEqual(self.game.get_next_player_and_mark(), (self.player_1, "o"))

        self.game.next_turn = self.player_2
        self.game.save()

        self.assertEqual(self.game.get_next_player_and_mark(), (self.player_2, "x"))

    def test_is_move_valid(self):
        self.assertTrue(self.game.is_move_valid(0, 0))

        Move.objects.create(
            game=self.game,
            player=self.player_1,
            row=0,
            column=0,
            mark="o",
        )

        self.assertFalse(self.game.is_move_valid(0, 0))
