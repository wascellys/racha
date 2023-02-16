from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from cadastros.models import Jogadores, Rachas, JogadoresRacha, RegistroPartida, Partida, JogadoresPartida
from django.contrib.auth.models import User
from django.db import transaction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username']


class JogadoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jogadores
        fields = ['id', 'nome', 'telefone', 'foto']

    def create(self, validated_data):
        try:
            user = User()
            nome = validated_data.get('nome').split(' ')
            primNome = ''
            segNome = ''
            for n in range(len(nome)):
                if (n < (len(nome) / 2.0)):
                    primNome += nome[n] + ' '
                else:
                    segNome += nome[n] + ' '

            with transaction.atomic():
                telefone = validated_data.get('telefone')
                user.username = telefone
                user.first_name = primNome
                user.last_name = segNome
                user.set_password(str(telefone))
                user.save()

                jogador = Jogadores.objects.create(**validated_data, user=user)

            return jogador
        except (Exception) as e:
            raise e


class RachasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rachas
        fields = "__all__"


class RachaRakingSerializer(serializers.ModelSerializer):
    jogador = JogadoresSerializer()
    gols = SerializerMethodField()
    assistencias = SerializerMethodField()
    total = SerializerMethodField()
    premios = SerializerMethodField()
    imagem = SerializerMethodField()
    racha = SerializerMethodField()
    participacoes = SerializerMethodField()

    class Meta:
        model = JogadoresRacha
        fields = ['id', 'jogador', 'gols', 'assistencias', 'premios', 'total', 'imagem', 'racha', 'participacoes']

    def get_racha(self, obj):
        return str(obj.racha.nome).upper()

    def get_nome(self, obj):
        return str(obj.jogador.nome).upper()

    def get_gols(self, obj):
        return str(obj.gols())

    def get_assistencias(self, obj):
        return str(obj.assistencias())

    def get_premios(self, obj):
        return str(obj.premios())

    def get_total(self, obj):
        return str(obj.total())

    def get_imagem(self, obj):
        return str(obj.jogador.foto)

    def get_participacoes(self, obj):
        return str(obj.participacoes())


class RegistrosPartidasSerializer(serializers.ModelSerializer):
    jogador_gol = SerializerMethodField(read_only=True)
    jogador_gol_foto = SerializerMethodField(read_only=True)
    jogador_assistencia = SerializerMethodField(read_only=True)
    jogador_assistencia_foto = SerializerMethodField(read_only=True)

    class Meta:
        model = RegistroPartida
        fields = ['id', 'gol', 'assistencia', 'tempo', 'partida', 'jogador_gol', 'jogador_gol_foto',
                  'jogador_assistencia', 'jogador_assistencia_foto']

    def get_jogador_gol(self, obj):
        return str(obj.gol).upper()

    def get_jogador_gol_foto(self, obj):
        return obj.gol.get_photo()

    def get_jogador_assistencia(self, obj):
        if obj.assistencia:
            return str(obj.assistencia).upper()
        return None


    def get_jogador_assistencia_foto(self, obj):
        if obj.assistencia:
            return obj.assistencia.get_photo()

        return None


class PartidaSerializer(serializers.ModelSerializer):
    racha_nome = SerializerMethodField(read_only=True)

    class Meta:
        model = Partida
        fields = ['id', 'data', 'racha', 'status', 'encerramento', 'racha_nome']

    def get_racha_nome(self, obj):
        return str(obj.racha.nome).upper()


class JogadoresPartidaSerializer(serializers.ModelSerializer):
    jogador_nome = SerializerMethodField(read_only=True)
    foto = SerializerMethodField(read_only=True)
    gols = SerializerMethodField(read_only=True)
    assistencias = SerializerMethodField(read_only=True)

    class Meta:
        model = JogadoresPartida
        fields = ['id', 'presente', 'jogador', 'partida', 'jogador_nome','foto','gols','assistencias']

    def get_jogador_nome(self, obj):
        return str(obj.jogador.nome).upper()

    def get_gols(self, obj):
        return str(obj.gols())

    def get_assistencias(self, obj):
        return str(obj.assistencias())

    def get_foto(self, obj):
        return obj.jogador.get_photo()


class JogadoresRachaSerializer(serializers.ModelSerializer):
    jogador_nome = SerializerMethodField(read_only=True)
    racha_nome = SerializerMethodField(read_only=True)
    jogador_imagem = SerializerMethodField(read_only=True)

    class Meta:
        model = JogadoresRacha
        fields = ['id', 'jogador', 'racha', 'jogador_nome', 'racha_nome', 'jogador_imagem']

    def get_jogador_nome(self, obj):
        return str(obj.jogador.nome).upper()

    def get_racha_nome(self, obj):
        return str(obj.racha.nome).upper()

    def get_jogador_imagem(self, obj):
        return obj.jogador.get_photo()
