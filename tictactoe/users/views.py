from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from .models import User
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, UserHighscoreSerializer



class UserViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """
    Updates and retrieves user accounts
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


class UserCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Creates user accounts
    """

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class HighscoreViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = (
        get_user_model()
        .objects.annotate(wins_count=Count("games_won"))
        .order_by("-wins_count")
    )
    serializer_class = UserHighscoreSerializer
    permission_classes = (AllowAny,)
