from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from api.viewsets import JogadoresViewSet, RachasViewSet, RankingRachaViewSet, DetailJogadorRachaViewSet, \
    RegistrosPartidasViewSet, CustomAuthToken, JogadoresRachaViewSet, PartidaViewSet, JogadoresPartidaViewSet, \
    AddJogadoresPartidaViewSet, JogadoresNaoRachaViewSet
from cadastros.autocomplete_fields import AutocompleteJogadoresPresentes, AutocompleteAssistente
from cadastros.views import *
# from cadastros.autocomplete_fields import *
from racha import settings

router = routers.DefaultRouter()
router.register('partidas', PartidaViewSet, basename='Partidas')
router.register('jogadores', JogadoresViewSet, basename='Jogadores')
router.register('jogadores_partida', JogadoresPartidaViewSet, basename='Jogadores Partida')
router.register('registro_partidas', RegistrosPartidasViewSet, basename='Registro Partidas')
router.register('rachas', RachasViewSet, basename='Rachas')
router.register('ranking_racha', RankingRachaViewSet, basename='Ranking do Racha')
router.register('jogador_racha_detalhe', DetailJogadorRachaViewSet, basename='Detalhe Jogador Racha')
router.register('jogadores_racha', JogadoresRachaViewSet, basename='Jogadores Racha')
router.register('jogadores_nao_racha', JogadoresNaoRachaViewSet, basename='Jogadores Nao Racha')



urlpatterns = [

    path('admin/', admin.site.urls),
    path('', lista_de_rachas, name="lista_de_rachas"),
    path('login/', autenticar, name='login'),
    path('logout/', sair, name='sair'),
    path('home/<int:pk>', home, name='home'),
    path('criar_partida/<int:pk>', criar_partida, name='criar_partida'),
    path('partida/<int:pk>', partida, name='partida'),

    path('cadastrar_jogadores/', cadastrar_jogador, name="cadastrar_jogador"),
    path('cadastrar_partidas/<int:pk>', cadastrar_partidas, name="cadastrar_partidas"),
    path('cadastrar_jogadores_presentes/<int:pk>', cadastrar_jogadores_presentes, name="cadastrar_jogadores_presentes"),
    path('cadastrar_premios/<int:racha_pk>', cadastrar_premios, name="cadastrar_premios"),
    path('cadastrar_jogadores_racha/<int:racha_pk>', cadastrar_jogadores_racha, name="cadastrar_jogadores_racha"),
    path('cadastrar_candidatos_premio/<int:partida_pk>', cadastrar_candidatos_premio, name="cadastrar_candidatos_premio"),

    path('remover_jogador_partida/<int:pk>', remove_jogador_partida, name="remove_jogador_partida"),
    path('registro_partida/<int:pk>', registro_partida, name="registro_partida"),

    path('anotar_gol/', anotar_gol, name='anotar_gol'),

    path('lista_rachas/', lista_de_rachas, name="lista_de_rachas"),
    path('lista_ranking/<int:pk>', lista_ranking, name="lista_ranking"),
    path('lista_artilharia/<int:pk>', lista_artilharia, name="lista_artilharia"),
    path('lista_assistencias/<int:pk>', lista_assistencia, name="lista_assistencias"),
    path('lista_premios/<int:racha_pk>', lista_premios, name="lista_premios"),

    path('lista_jogadores/', lista_de_jogadores, name="lista_de_jogadores"),
    path('lista_de_jogadores_racha/<int:pk>', lista_de_jogadores_racha, name="lista_de_jogadores_racha"),
    path('lista_partidas/', lista_de_partidas, name="lista_de_partidas"),
    path('lista_partidas_racha/<int:pk>', lista_de_partidas_racha, name="lista_de_partida_racha"),

    path('lista_balanco/<int:racha_pk>', lista_balanco, name="lista_balanco"),

    path('detalhe_jogador_racha/<int:pk>/<int:racha_pk>/', detalhe_jogador_racha, name="detalhe_jogador_racha"),

    url(r'^auto_jogador/$', AutocompleteJogadoresPresentes.as_view(), name='auto_jogador'),
    url(r'^auto_assistente/$', AutocompleteAssistente.as_view(), name='auto_assistente'),

    path('api/', include(router.urls)),
    path('api-token-auth/', CustomAuthToken.as_view()),
    path('api/add_jogadores_partida/', AddJogadoresPartidaViewSet.as_view(), name="adicionar_jogadores_partida"),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
