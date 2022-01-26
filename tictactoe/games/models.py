import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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
    status = models.CharField(choices=STATUS_CHOICES, max_length=15)
    winner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="games_won"
    )
    next_turn = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="games_pending_move"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]


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
        ("o", "Nought"),
        ("x", "Cross"),
    )
    mark = models.CharField(choices=MARK_CHOICES, max_length=1)
