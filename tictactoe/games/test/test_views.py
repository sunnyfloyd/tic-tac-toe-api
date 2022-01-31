from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from tictactoe.users.test.factories import UserFactory
from tictactoe.games.models import Game
from tictactoe.games.services import GameService


User = get_user_model()


class TestGameView(APITestCase):
    def setUp(self) -> None:
        self.player_1 = User.objects.create(
            username="player_1", email="p1@example.com", password="D*3nd*&*3jnDI"
        )
        self.player_2 = User.objects.create(
            username="player_2", email="p2@example.com", password="D*3nd*&*3jnDI"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.player_1.auth_token}")
        self.game = Game.objects.create()

    def test_game_creation(self):
        url = reverse("game-list")
        response = self.client.post(url, {})
        game_id = str(response.data.get("id"))
        player_data = response.data.get("player_1") or response.data.get("player_2")

        self.assertTrue(Game.objects.get(pk=game_id).is_user_in_game(self.player_1))
        self.assertEqual(self.player_1.id, player_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_join_game(self):
        GameService.set_up_player(self.game, self.player_2)
        url = reverse("game-join-game", kwargs={"pk": self.game.id})
        response = self.client.post(url, {})
        self.game.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            self.game.is_user_in_game(self.player_1)
        )
        self.assertTrue(
            self.game.is_user_in_game(self.player_2)
        )

    def test_join_game_by_the_game_creator(self):
        GameService.set_up_player(self.game, self.player_1)
        url = reverse("game-join-game", kwargs={"pk": self.game.id})
        response = self.client.post(url, {})
        self.game.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "You already joined this game")
        self.assertFalse(
            self.game.is_user_in_game(self.player_2)
        )
        self.assertTrue(
            self.game.is_user_in_game(self.player_1)
        )

    def test_join_full_game(self):
        self.game.player_1 = UserFactory()
        self.game.player_2 = UserFactory()
        self.game.save()
        url = reverse("game-join-game", kwargs={"pk": self.game.id})
        response = self.client.post(url, {})
        self.game.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "This game is already full")
        self.assertFalse(
            self.game.is_user_in_game(self.player_1)
        )

    def test_join_game_by_the_same_player_twice(self):
        self.game.player_1 = self.player_1
        self.game.save()
        url = reverse("game-join-game", kwargs={"pk": self.game.id})
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "You already joined this game")

    def _set_up_game(self):
        self.game.player_1 = self.player_1
        self.game.player_2 = self.player_2
        self.game.status = "in_progress"
        self.game.save()

    def test_move(self):
        self._set_up_game()
        url = reverse("game-move", kwargs={"pk": self.game.id})
        response = self.client.post(url, {"row": 0, "column": 0})
        self.game.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.game.moves.filter(row=0, column=0).exists())
        self.assertEqual(self.game.next_turn, self.player_2)

    def test_move_with_logic_error(self):
        self._set_up_game()
        self.game.status = "finished"
        self.game.save()
        url = reverse("game-move", kwargs={"pk": self.game.id})
        response = self.client.post(url, {"row": 0, "column": 0})
        self.game.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "This game has already finished")
        self.assertFalse(self.game.moves.filter(row=0, column=0).exists())

    def test_move_with_request_data_error(self):
        self._set_up_game()
        url = reverse("game-move", kwargs={"pk": self.game.id})
        response = self.client.post(url, {"row": -1, "column": 5})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.game.moves.filter(row=-1, column=5).exists())

    def _set_up_moves(self, player_1_moves, player_2_moves):
        url = reverse("game-move", kwargs={"pk": self.game.id})

        for p1, p2 in zip(player_1_moves, player_2_moves):
            self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.player_1.auth_token}")
            yield self.client.post(url, {"row": p1[0], "column": p1[1]})
            self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.player_2.auth_token}")
            yield self.client.post(url, {"row": p2[0], "column": p2[1]})
            
    def test_moves(self):
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
        moves = player_1_moves + player_2_moves
        self._set_up_game()
        
        for response in self._set_up_moves(player_1_moves, player_2_moves):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(
            set(moves),
            set(self.game.moves.all().values_list("row", "column"))
        )

