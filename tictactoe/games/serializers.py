from rest_framework import serializers
from tictactoe.games.models import Game, Move


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = (
            "player_1",
            "player_2",
            "status",
            "winner",
            "next_turn",
        )


class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = "__all__"
        read_only_fields = (
            "game",
            "player",
            "mark",
        )
