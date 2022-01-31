from typing import Tuple
import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

MARKS = {"player_1": "o", "player_2": "x"}


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player_1 = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="games_as_p1"
    )
    player_2 = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="games_as_p2"
    )
    STATUS_CHOICES = (
        ("not_started", "Not started"),
        ("in_progress", "In progress"),
        ("finished", "Finished"),
    )
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=15, default="not_started"
    )
    winner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="games_won"
    )
    next_turn = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="games_pending_move"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def is_user_in_game(self, user: User) -> bool:
        """Checks if user is part of a game.

        Args:
            user (User): user to check

        Returns:
            bool: True if user is part of a game
        """
        return user in (self.player_1, self.player_2)

    @property
    def is_full(self) -> bool:
        """Game property indicating if game is full.

        Returns:
            bool: True if game is full
        """
        return None not in (self.player_1, self.player_2)

    def get_next_player_and_mark(self) -> Tuple[User, str]:
        """Returns tuple of current player's turn and their in-game mark.

        Method sets up `next_turn` value to `player_1` before players' first move.

        Returns:
            Tuple[User, str]: user with their tic-tac-toe mark
        """
        if self.player_1 is None:
            raise ValueError("Game must be started before getting next player")
        
        if self.next_turn is None:
            self.next_turn = self.player_1
            self.save()
        mark = (
            MARKS["player_1"] if self.next_turn == self.player_1 else MARKS["player_2"]
        )

        return (self.next_turn, mark)

    def is_move_valid(self, row: int, column: int) -> bool:
        """Verified if given move is valid for current game.

        Args:
            row (int): row in which mark should be placed
            column (int): col in which mark should be placed

        Returns:
            bool: True if given move has not been made before
        """
        return not self.moves.filter(row=row, column=column).exists()

    def __str__(self) -> str:
        return f"Game {self.id} - status {self.status}"


class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    player = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name="moves"
    )
    MOVE_CHOICES = (
        (0, 0),
        (1, 1),
        (2, 2),
    )
    row = models.IntegerField(choices=MOVE_CHOICES)
    column = models.IntegerField(choices=MOVE_CHOICES)
    MARK_CHOICES = (
        (MARKS["player_1"], "Nought"),
        (MARKS["player_2"], "Cross"),
    )
    mark = models.CharField(choices=MARK_CHOICES, max_length=1)
