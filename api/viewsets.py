from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.db import transaction

from api.serializers import JogadoresSerializer, RachasSerializer, RachaRakingSerializer, RegistrosPartidasSerializer, \
    JogadoresRachaSerializer, PartidaSerializer, JogadoresPartidaSerializer
from cadastros.models import Jogadores, Rachas, JogadoresRacha, RegistroPartida, Partida, JogadoresPartida


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        jogador = Jogadores.objects.get(user=user)
        token, created = Token.objects.get_or_create(user=user)
        admin = False
        if user.is_superuser:
            admin = True

        response = Response({
            'id': jogador.id,
            'token': token.key,
            'username': user.username,
            'nome': jogador.nome,
            'foto': jogador.get_foto(),
            'admin': admin
        })

        return response


class JogadoresViewSet(ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = [IsAuthenticated]
    queryset = Jogadores.objects.all()
    serializer_class = JogadoresSerializer

    def list(self, request, *args, **kwargs):
        try:
            jogadores = Jogadores.objects.all()
            serializers = self.serializer_class(jogadores, many=True)
            return Response(data=serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def update(self, request, *args, **kwargs):
    #     jogador = Jogadores.objects.get(id=kwargs['pk'])
    #     serializer = self.serializer_class(jogador, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def retrieve(self, request, *args, **kwargs):
    #     try:
    #         jogador = Jogadores.objects.get(id=kwargs['pk'])
    #         serializers = self.serializer_class(jogador)
    #         return Response(data=serializers.data, status=status.HTTP_200_OK)
    #     except ObjectDoesNotExist:
    #         return Response({'message': 'Registro não existe!'}, status=status.HTTP_404_NOT_FOUND)


class RachasViewSet(ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = [IsAuthenticated]
    queryset = Rachas.objects.all().order_by('-data_inicio')
    serializer_class = RachasSerializer

    def list(self, request, *args, **kwargs):

        try:
            # rachas = Rachas.objects.filter(ativo=True).order_by('-data_inicio')
            if request.user.is_authenticated:
                if request.user.is_superuser:
                    rachas = Rachas.objects.all().order_by('-data_inicio')
                else:
                    jogador = Jogadores.objects.get(user=request.user)
                    rachas = jogador.get_rachas()
                serializers = self.serializer_class(rachas, many=True)
                return Response(data=serializers.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': "Acesso restrito"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(e.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        racha = Rachas.objects.get(codigo=kwargs['pk'])
        serializer = self.serializer_class(racha, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            racha = Rachas.objects.get(codigo=kwargs['pk'])
            serializers = self.serializer_class(racha)
            return Response(data=serializers.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'message': 'Registro não existe!'}, status=status.HTTP_404_NOT_FOUND)

class RegistrosPartidasViewSet(ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = RegistroPartida.objects.all()
    serializer_class = RegistrosPartidasSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.request.GET.get('partida'):
            queryset = queryset.filter(partida__pk=self.request.GET.get('partida'))
        if self.request.GET.get('jogador_gol'):
            queryset = queryset.filter(gol__pk=self.request.GET.get('jogador_gol'))
        if self.request.GET.get('jogador_assistencia'):
            queryset = queryset.filter(assistencia__pk=self.request.GET.get('jogador_assistencia'))
        if self.request.GET.get('racha'):
            queryset = queryset.filter(partida__racha__pk=self.request.GET.get('racha'))
        return queryset



class RankingRachaViewSet(ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = JogadoresRacha.objects.all()
    serializer_class = RachaRakingSerializer


    def get_queryset(self):
        queryset = self.queryset
        if self.request.GET.get('partida'):
            queryset = queryset.filter(partida__pk=self.request.GET.get('partida'))
        if self.request.GET.get('racha'):
            queryset = queryset.filter(racha__codigo=self.request.GET.get('racha'))
        return queryset


    # def get_queryset(self):
    #     queryset = self.queryset
    #     queryset = queryset.filter(racha__pk=self.request.GET.get('racha_pk'))
    #     return queryset



class JogadoresRachaViewSet(ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = JogadoresRacha.objects.all()
    serializer_class = JogadoresRachaSerializer


    def get_queryset(self):
        queryset = self.queryset
        if self.request.GET.get('racha'):
            queryset = queryset.filter(racha__codigo=self.request.GET.get('racha'))
        if self.request.GET.get('jogador'):
            queryset = queryset.filter(jogador__pk=self.request.GET.get('jogador'))
        return queryset


class JogadoresNaoRachaViewSet(ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Jogadores.objects.filter()
    serializer_class = JogadoresSerializer


    def get_queryset(self):
        queryset = self.queryset
        if self.request.GET.get('racha'):
            ids = []
            jogadores_do_racha = JogadoresRacha.objects.filter(racha__codigo=self.request.GET.get('racha'))
            for j in jogadores_do_racha:
                ids.append(j.jogador.id)
                queryset = queryset.exclude(pk__in=ids)
        return queryset

class DetailJogadorRachaViewSet(ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = JogadoresRacha.objects.all()
    serializer_class = RachaRakingSerializer


    def get_queryset(self):
        jogador = self.request.GET.get('jogador')
        jogador_racha = JogadoresRacha.objects.filter(pk=jogador)
        queryset = jogador_racha
        return queryset



class PartidaViewSet(ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = Partida.objects.all().order_by('-data')
    serializer_class = PartidaSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.request.GET.get('racha'):
            queryset = queryset.filter(racha__codigo=self.request.GET.get('racha'))
        return queryset


class JogadoresPartidaViewSet(ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = JogadoresPartida.objects.all()
    serializer_class = JogadoresPartidaSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.request.GET.get('partida'):
            queryset = queryset.filter(partida__pk=self.request.GET.get('partida'))
        if self.request.GET.get('jogador'):
            queryset = queryset.filter(jogador__pk=self.request.GET.get('jogador'))
        if self.request.GET.get('status'):
            queryset = queryset.filter(presente=self.request.GET.get('status'))
        if self.request.GET.get('racha'):
            queryset = queryset.filter(partida__racha__pk=self.request.GET.get('racha'))
        return queryset



class AddJogadoresPartidaViewSet(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        lista = request.data.get('jogadores')
        for l in lista:
            jogadores = Jogadores.objects.filter(pk=int(l))
        return Response(jogadores)

class DeleteJogadoresPartidaViewSet(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        lista = request.data.get('jogadores')
        for l in lista:
            jogadores = Jogadores.objects.filter(pk=int(l))
        return Response(jogadores)






