from typing import Union
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tictactoe.games.models import Game
from tictactoe.games.serializers import GameSerializer, MoveSerializer
from tictactoe.games.services import GameService


class GameViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer: GameSerializer) -> None:
        game = serializer.save()
        GameService.set_up_player(game=game, user=self.request.user)

    @action(detail=True, methods=["post"])
    def join_game(self, request, pk: Union[int, None] = None) -> Response:
        game = self.get_object()
        result = GameService.join_game(game=game, user=request.user)

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(game).data)

    @action(detail=True, methods=["post"], serializer_class=MoveSerializer)
    def move(self, request, pk: Union[int, None] = None) -> Response:
        game = self.get_object()
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = GameService.move(
            game=game, data=serializer.validated_data, user=request.user
        )

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.serializer_class(result["move"]).data)

    @action(detail=True, methods=["get"], serializer_class=MoveSerializer)
    def moves(self, request, pk: Union[int, None] = None) -> Response:
        queryset = self.get_object().moves.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
