from django.db import models
from django.contrib.auth.models import User
from time import strftime
import time

from django.utils.crypto import get_random_string


def foto(instance, filename):
    return 'photos/{telefone}_{datetime}.jpg'.format(telefone=instance.telefone, datetime=strftime('%Y%m%d%H%M%S'))


def imagem(instance, filename):
    return 'photos/{nome}_{datetime}.jpg'.format(nome=instance.nome, datetime=strftime('%Y%m%d%H%M%S'))


def create_if_hash():
    return get_random_string(5)
    # if not Rachas.objects.filter(codigo=hash).exists():
    #     return hash
    # else:
    #     return create_if_hash()


class Jogadores(models.Model):
    nome = models.CharField(max_length=250)
    telefone = models.IntegerField()
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="jogador")
    foto = models.ImageField(upload_to=foto, null=True, blank=True, default='')
    url_foto = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['nome']
        unique_together = (("nome", "user"),)

    def __str__(self):
        return str(self.nome)

    def get_foto(self):
        if self.foto:
            return '/media/'+str(self.foto)
        return None

    def gols(self, ):
        gols = RegistroPartida.objects.filter(gol=self)
        if gols:
            return len(gols)
        return 0

    def assistencias(self):
        assistencias = RegistroPartida.objects.filter(assistencia=self)
        if assistencias:
            return len(assistencias)
        return 0

    def participacoes(self):
        return JogadoresPartida.objects.filter(jogador=self).count()

    def get_rachas(self):
        rachas = JogadoresRacha.objects.filter(jogador=self).values('racha__pk')
        return Rachas.objects.filter(pk__in=rachas).order_by('-data_final')


class Rachas(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=100, blank=True, null=True)
    data_inicio = models.DateField()
    data_final = models.DateField()
    image = models.ImageField(upload_to=imagem, null=True, blank=True, default='')
    status = models.BooleanField(blank=True, null=True)
    gol_score = models.CharField(null=True, blank=True, max_length=10)
    assistencia_score = models.CharField(null=True, blank=True, max_length=10)
    presenca_score = models.CharField(null=True, blank=True, max_length=10)
    ativo = models.BooleanField(default=False)
    codigo = models.CharField(max_length=5, default=create_if_hash, unique=True, null=True, blank=True)

    def __str__(self):
        return self.nome

    def get_foto(self):
        if self.image:
            return "/media/" + str(self.image)
        return None


class Premios(models.Model):
    nome = models.CharField(max_length=100)
    score = models.FloatField(default=0.0, null=True, blank=True)
    sigla = models.CharField(max_length=5, blank=True, null=True)
    racha = models.ForeignKey(Rachas, on_delete=models.PROTECT)
    contabilizar_no_geral = models.BooleanField(default=False)

    def __str__(self):
        return str(self.nome) + " - " + str(self.racha)

    def get_contabilizar(self):
        if self.contabilizar_no_geral:
            return "Sim"
        return "Não"


class Partida(models.Model):
    data = models.DateField()
    status = models.BooleanField()
    racha = models.ForeignKey(Rachas, on_delete=models.PROTECT)
    encerramento = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.data) + " (" + str(self.racha) + ")"


class RegistroPartida(models.Model):
    tempo = models.TimeField(null=True, blank=True)
    gol = models.ForeignKey(Jogadores, on_delete=models.PROTECT, related_name='requests_gol')
    assistencia = models.ForeignKey(Jogadores, on_delete=models.PROTECT, blank=True, null=True)
    partida = models.ForeignKey(Partida, on_delete=models.PROTECT)

    def __str__(self):
        return "Gol (" + str(self.gol) + ") | Assistencia (" + str(self.assistencia) + ") -(" + str(self.tempo) + ")"

    def gols(self, ):
        gols = RegistroPartida.objects.filter(gol=self)
        if gols:
            return gols.count()
        else:
            return 0


class PremioPartida(models.Model):
    jogador = models.ForeignKey(Jogadores, on_delete=models.PROTECT)
    premio = models.ForeignKey(Premios, on_delete=models.PROTECT)
    partida = models.ForeignKey(Partida, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.jogador) + " - " + str(self.premio)

    class Meta:
        unique_together = (("jogador", "premio", 'partida'),)


class JogadoresPartida(models.Model):
    jogador = models.ForeignKey(Jogadores, on_delete=models.PROTECT)
    partida = models.ForeignKey(Partida, on_delete=models.PROTECT)
    presente = models.BooleanField(default=False)

    def __str__(self):
        return str(self.jogador.nome) + ' (' + str(self.partida.data) + ')'

    def gols(self, ):
        gols = RegistroPartida.objects.filter(gol=self.jogador, partida=self.partida)
        if gols:
            return gols.count()
        else:
            return 0

    def assistencias(self, ):
        assistencias = RegistroPartida.objects.filter(assistencia=self.jogador, partida=self.partida)
        if assistencias:
            return assistencias.count()
        else:
            return 0


class JogadoresRacha(models.Model):
    jogador = models.ForeignKey(Jogadores, on_delete=models.PROTECT)
    racha = models.ForeignKey(Rachas, on_delete=models.PROTECT)

    class Meta:
        ordering = ['jogador']
        unique_together = (("jogador", "racha"),)

    def __str__(self):
        return self.jogador.nome + ' (' + self.racha.nome + ')'

    def gols(self, ):
        gols = RegistroPartida.objects.filter(gol=self.jogador, partida__racha=self.racha)
        if gols:
            return gols.count()
        else:
            return 0

    def presencas(self, ):
        presente = JogadoresPartida.objects.filter(jogador=self.jogador, partida__racha=self.racha)
        if presente:
            return presente.count()
        else:
            return 0

    def assistencias(self, ):
        assistencias = RegistroPartida.objects.filter(assistencia=self.jogador, partida__racha=self.racha)
        if assistencias:
            return assistencias.count()
        else:
            return 0

    def premios(self):
        premios = Premios.objects.filter(racha=self.racha, contabilizar_no_geral=True)

        lista = []

        for p in premios:
            premio_dic = {}
            premio_partida = PremioPartida.objects.filter(premio=p, partida__racha=self.racha, jogador=self.jogador)
            premio = Premios.objects.get(pk=p.pk)
            premio_dic['premio'] = p.nome
            premio_dic['qtd'] = premio_partida.count()
            premio_dic['total'] = float(premio.score) * premio_dic['qtd']
            lista.append(premio_dic)

        return lista

    def total_premios(self):
        premios = Premios.objects.filter(racha=self.racha, contabilizar_no_geral=True)
        lista = []
        total = 0

        for p in premios:
            premio_dic = {}
            premio_partida = PremioPartida.objects.filter(premio=p, partida__racha=self.racha, jogador=self.jogador)
            premio = Premios.objects.get(pk=p.pk)
            premio_dic['premio'] = p.nome
            premio_dic['qtd'] = premio_partida.count()
            premio_dic['total'] = float(premio.score) * premio_dic['qtd']
            lista.append(premio_dic)

        for l in lista:
            total += l['total']

        return total

    def total(self):
        gols = RegistroPartida.objects.filter(gol=self.jogador, partida__racha=self.racha)
        assistencias = RegistroPartida.objects.filter(assistencia=self.jogador, partida__racha=self.racha)
        total_gols = 0
        total_assistencias = 0
        total = 0

        if gols:
            total_gols += gols.count()
        if assistencias:
            total_assistencias += assistencias.count()

        total += float(total_gols * int(self.racha.gol_score)) + float(
            total_assistencias * float(self.racha.assistencia_score))

        premios = Premios.objects.filter(racha=self.racha, contabilizar_no_geral=True)
        if premios:

            lista = []
            total_premios = 0
            presenca = 0

            if self.racha.presenca_score:
                presente = JogadoresPartida.objects.filter(jogador=self.jogador, partida__racha=self.racha)
                if presente:
                    presenca = presente.count() * float(self.racha.presenca_score)

            for p in premios:
                premio_dic = {}
                premio_partida = PremioPartida.objects.filter(premio=p, partida__racha=self.racha, jogador=self.jogador)
                premio = Premios.objects.get(pk=p.pk)
                premio_dic['qtd'] = premio_partida.count()
                premio_dic['total'] = float(premio.score) * premio_dic['qtd']
                lista.append(premio_dic)

            for l in lista:
                total_premios += l['total']

            return total + total_premios + presenca

        return total

    def participacoes(self):
        total_rachas = Partida.objects.filter(racha=self.racha).count()
        part = JogadoresPartida.objects.filter(jogador=self.jogador, partida__racha=self.racha).count()

        return str(part) + "/" + str(total_rachas)


class CandidatoPremio(models.Model):
    jogador = models.ForeignKey(Jogadores, on_delete=models.PROTECT)
    premio_racha = models.ForeignKey(Premios, on_delete=models.PROTECT)
    partida = models.ForeignKey(Partida, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('jogador', 'premio_racha', 'partida')


class Votacao(models.Model):
    candidato = models.ForeignKey(CandidatoPremio, on_delete=models.PROTECT)
    eleitor = models.ForeignKey(Jogadores, on_delete=models.PROTECT)
    tempo = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('candidato', 'eleitor')


class Financeiro(models.Model):
    CHOICES_TIPO = (
        ('1', 'Mensalidade'),
        ('2', 'Outro'),
    )
    CHOICES_TIPO_ENTRADA = (
        ('1', 'RECEITA'),
        ('2', 'DESPESA'),
    )

    membro = models.ForeignKey(JogadoresRacha, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=100, choices=CHOICES_TIPO)
    entrada = models.CharField(max_length=100, choices=CHOICES_TIPO_ENTRADA)
    observacao = models.CharField(max_length=200, null=True, blank=True)
    valor = models.CharField(max_length=20)
    data = models.DateField()
    racha = models.ForeignKey(Rachas, on_delete=models.PROTECT)

    def get_receitas_racha(self):
        return Financeiro.objects.filter(racha=self.racha, entrada="RECEITA")

    def get_despesas_racha(self):
        return Financeiro.objects.filter(racha=self.racha, entrada="DESPESA")
