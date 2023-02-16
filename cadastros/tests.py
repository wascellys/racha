from django.test import TestCase

# Create your tests here.



geral = []

racha = Rachas.objects.get(nome__icontains="2020")
jogadores = JogadoresRacha.objects.filter(racha=racha)

for jogador in jogadores:
   ranking = {}
   ranking['jogador'] = jogador.jogador
   ranking['participacao'] = 0 + jogador.participacoes()
   geral.append(ranking)

geral = sorted(geral, key=lambda k: k['participacao'] , reverse=True)





geral = []
jogadores = Jogadores.objects.all()

for jogador in jogadores:
   ranking = {}
   ranking['jogador'] = jogador
   ranking['participacao'] = 0 + jogador.participacoes()
   geral.append(ranking)

geral = sorted(geral, key=lambda k: k['participacao'] , reverse=True)



from cadastros.models import  *
jogador = JogadoresRacha.objects.get(jogador__user__username="edy", racha__pk=4)
jogador.presencas()



presente = JogadoresPartida.objects.filter(jogador=jogador.jogador, partida__racha__pk=4)


from django.contrib.auth.models import User

def create_if_hash():
   username = get_random_string(5)
   if not User.objects.filter(username=username).exists():
      return username
   else:
      return create_if_hash()


import random
from cadastros.models import *
users = User.objects.exclude(pk=1)

def create_telefone():
   x = random.randint(00000000,99999999)
   if not Jogadores.objects.filter(telefone=x).exists():
      return x
   else:
      return create_telefone()


for u in users:
   try:
      jogador = Jogadores()
      jogador.nome = u.get_full_name()
      jogador.telefone = create_telefone()
      jogador.user = u
      jogador.save()
   except:
      print("Deu erro ", u.first_name)




print(x)
