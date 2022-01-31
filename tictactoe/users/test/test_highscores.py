from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from tictactoe.games.models import Game
from tictactoe.games.services import GameService
from tictactoe.users.test.factories import UserFactory


User = get_user_model()


class TestHighscoreView(APITestCase):
    def setUp(self) -> None:
        self.player_1 = User.objects.create(
            username="player_1", email="p1@example.com", password="D*3nd*&*3jnDI"
        )
        self.player_2 = User.objects.create(
            username="player_2", email="p2@example.com", password="D*3nd*&*3jnDI"
        )
        self.player_3 = UserFactory()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.player_1.auth_token}")

        for _ in range(6):
            Game.objects.create(
                player_1=self.player_1, status="finished", winner=self.player_1
            )

        for _ in range(11):
            Game.objects.create(
                player_1=self.player_2, status="finished", winner=self.player_2
            )

    def test_highscore_list(self):
        url = reverse("highscore-list")
        response = self.client.get(url, {})
        results = {
            score["id"]: score["wins_count"]
            for score in response.data.get("results")
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results[str(self.player_1.id)], 6)
        self.assertEqual(results[str(self.player_2.id)], 11)
        self.assertEqual(results[str(self.player_3.id)], 0)

    def test_highscore_detail(self):
        url = reverse("highscore-detail", kwargs={"pk": self.player_1.id})
        response = self.client.get(url, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("wins_count"), 6)
