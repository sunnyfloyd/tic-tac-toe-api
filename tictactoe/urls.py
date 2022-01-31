from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from tictactoe.users.views import UserViewSet, UserCreateViewSet, HighscoreViewSet
from tictactoe.games.views import GameViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"users", UserCreateViewSet)
router.register(r"games", GameViewSet)

highscore_list = HighscoreViewSet.as_view({"get": "list"})
highscore_detail = HighscoreViewSet.as_view({"get": "retrieve"})
# from pprint import pprint
# pprint(router.urls)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path("api/v1/highscores/<uuid:pk>/", highscore_detail, name="highscore-detail"),
    path("api/v1/highscores/", highscore_list, name="highscore-list"),
    path("api-token-auth/", views.obtain_auth_token),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
