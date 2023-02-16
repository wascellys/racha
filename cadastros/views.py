from django.shortcuts import render, get_object_or_404, redirect
from cadastros.models import *
from django.contrib.auth.models import Permission, User
from django.db import transaction
from cadastros.form import *
from django.contrib import messages
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from datetime import date
from django.utils import timezone
from django.urls import reverse


def hojeAgora():
    return timezone.localtime(timezone.now())


def autenticar(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            if request.POST.get('username') and request.POST.get('password'):
                user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        messages.success(request, 'Bem-vindo {} !'.format(user))
                        return HttpResponseRedirect('/lista_rachas/')
                    else:
                        messages.error(request, 'Jogador com cadastro inativo !')
                        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
                else:
                    messages.error(request, 'Login ou senha incorretos!')
                    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            else:
                messages.error(request, 'Preencha os campos !')
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        else:
            return render(request, 'accounts/login.html')
    else:
        return HttpResponseRedirect('/lista_rachas/')


# @login_required(login_url='/login')
def home(request, pk):
    existe = False
    racha = Rachas.objects.get(id=pk)
    buscar_partida = Partida.objects.filter(racha=pk, data=hojeAgora().date())

    if buscar_partida:
        existe = True

    return render(request, 'home.html', {'racha': racha, 'existe': existe})


@login_required(login_url='/login')
def sair(request):
    logout(request)
    return HttpResponseRedirect('/login/')


@transaction.atomic()
def cadastrar_jogador(request):
    with transaction.atomic():
        if request.method == "POST":
            form = CadastrarJogadorForm(request.POST)
            jogador = Jogadores()
            user = User()
            nome = request.POST.get('nome').split(' ')
            primNome = ''
            segNome = ''
            for n in range(len(nome)):
                if (n < (len(nome) / 2.0)):
                    primNome += nome[n] + ' '
                else:
                    segNome += nome[n] + ' '

            user.username = request.POST.get('telefone')
            user.first_name = primNome
            user.last_name = segNome
            user.set_password(request.POST.get('telefone'))

            jogador.nome = request.POST.get('nome')
            jogador.telefone = request.POST.get('telefone')

            if request.POST.get('url_foto'):
                url = request.POST.get('url_foto').split('//')
                jogador.url_foto = url[1]

            user.save()
            print(user)
            jogador.user = user
            jogador.save()

            print(jogador)

            messages.success(request,
                             'Jogador cadastrado com sucesso.')

            return HttpResponseRedirect('/lista_jogadores/')
        return render(request, 'cadastros/cadastro_jogadores.html')


@login_required(login_url='/login')
def cadastrar_partidas(request, pk):
    if request.method == "POST":
        partida = Partida()
        partida.data = request.POST['data']
        partida.status = True
        racha = Rachas.objects.get(id=pk)
        partida.racha = racha
        partida.save()

        messages.success(request, 'Partida cadastrada com sucesso.')

        return redirect('/lista_partidas_racha/' + str(racha.pk))
    else:
        return render(request, 'cadastros/cadastro_partidas.html')


@login_required(login_url='/login')
def lista_de_rachas(request):
    context = 'lista_rachas'

    if request.user.is_superuser:
        rachas = Rachas.objects.all().order_by('-data_inicio')
        return render(request, 'listas/lista_rachas.html', {'rachas': rachas})
    else:
        if request.user.is_authenticated:
            user_jogador = Jogadores.objects.filter(user=request.user)
            if user_jogador:
                jogador = Jogadores.objects.get(user=request.user)
                rachas = jogador.get_rachas()

                print("RACHAS: ", rachas)
                return render(request, 'listas/lista_rachas.html', {'rachas': rachas, 'segment': context})
            else:
                return render(request, 'listas/lista_rachas.html', {'segment': context})
        else:
            return HttpResponseRedirect('login')


@login_required(login_url='/login')
def criar_partida(request, pk):
    try:
        with transaction.atomic():
            partida = Partida()

            partida.data = hojeAgora().date()
            partida.status = True
            racha = Rachas.objects.get(id=pk)
            partida.racha = racha
            partida.save()

            url = reverse('partida', args=[partida.id])
        return HttpResponseRedirect(url)
    except Exception as e:
        return HttpResponse(e)


@login_required(login_url='/login')
def partida(request, pk):
    partida = Partida.objects.get(id=pk)
    jogadores = JogadoresPartida.objects.filter(partida=partida).order_by('jogador__nome')

    jogadores_ausentes = JogadoresRacha.objects.filter(racha__pk=partida.racha.pk)

    if jogadores:
        for j in jogadores:
            jogadores_ausentes = jogadores_ausentes.exclude(id=j.jogador.id)

    return render(request, 'cadastros/partida.html', {
        'partida': partida, 'jogadores_ausentes': jogadores_ausentes, 'jogadores': jogadores})


@login_required(login_url='/login')
def cadastrar_jogadores_presentes(request, pk):
    partida = Partida.objects.get(pk=pk)
    try:
        jogadores_selecionados = request.POST.getlist('jogadores')

        for i in jogadores_selecionados:
            jogadores_presentes = JogadoresPartida()
            jogador = JogadoresRacha.objects.get(pk=i)
            jogadores_presentes.jogador = jogador.jogador
            jogadores_presentes.partida = partida
            jogadores_presentes.presente = True
            jogadores_presentes.save()

            messages.success(request, 'Jogadores adicionados')

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Exception as e:
        print("DEU FUMO", e)
        messages.error(request, e, 'danger')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url='/login')
def cadastrar_jogadores_racha(request, pk):
    racha = Rachas.objects.get(pk=pk)
    try:
        jogadores_selecionados = request.POST.getlist('jogadores')

        for i in jogadores_selecionados:
            jogador = JogadoresRacha()
            jogador.racha = racha
            jogador.jogador = Jogadores.objects.get(pk=i)
            jogador.save()

            messages.success(request, 'Jogador adicionado ao racha')

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Exception as e:
        messages.error(request, e, 'danger')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url='/login')
def remove_jogador_partida(request):
    try:
        jogadores_selecionados = request.POST.getlist('remover_jogador')

        for adicionados in jogadores_selecionados:
            jogador_para_deletar = JogadoresPartida.objects.get(id=adicionados)
            jogador_para_deletar.delete()

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Partida.DoesNotExist:
        messages.error(request, "Partida não encontrada", 'danger')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except JogadoresPartida.DoesNotExist:
        messages.error(request, "Jogador não cadastrado", 'danger')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url='/login')
def anotar_gol(request):
    print(request.POST)
    try:
        registro_partida = RegistroPartida()

        if 'gol' in request.POST:
            jogador = Jogadores.objects.get(id=request.POST['gol'])

        if request.POST['assistente'] != '':
            assistente = Jogadores.objects.get(id=request.POST['assistente'])
        else:
            assistente = None

        partida_atual = Partida.objects.get(id=request.POST['partida_atual'])

        registro_partida.gol = jogador
        registro_partida.partida = partida_atual
        registro_partida.assistencia = assistente
        registro_partida.tempo = hojeAgora().time()

        registro_partida.save()
        golaco = registro_partida.gol

        messages.error(request, 'Gooooooooooool, é dele, ' +
                       str(golaco) + '', 'warning')

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Exception as e:
        messages.error(request, 'Erro ao realizar o registro' + str(e), 'danger')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def lista_ranking(request, pk):
    geral = []

    racha = Rachas.objects.get(id=pk)
    jogadores = JogadoresRacha.objects.filter(racha=racha.id)

    for jogador in jogadores:
        ranking = {}

        ranking['jogador'] = jogador.jogador
        ranking['foto'] = jogador.jogador.get_foto()
        ranking['total'] = 0 + jogador.total()
        geral.append(ranking)

    geral = sorted(geral, key=lambda k: k['total'], reverse=True)
    return render(request, "listas/lista_ranking.html", {'racha': racha, 'ranking': geral})


def lista_artilharia(request, pk):
    geral = []

    racha = Rachas.objects.get(id=pk)
    jogadores = JogadoresRacha.objects.filter(racha=racha.id)

    for jogador in jogadores:
        ranking = {}

        ranking['jogador'] = jogador.jogador
        ranking['gols'] = 0 + jogador.gols()
        geral.append(ranking)

    geral = sorted(geral, key=lambda k: k['gols'], reverse=True)

    return render(request, "listas/lista_artilharia.html", {'racha': racha, 'ranking': geral})


def lista_assistencia(request, pk):
    geral = []

    racha = Rachas.objects.get(id=pk)
    jogadores = JogadoresRacha.objects.filter(racha=racha.id)

    for jogador in jogadores:
        ranking = {}

        ranking['jogador'] = jogador.jogador
        ranking['assistencias'] = 0 + jogador.assistencias()
        geral.append(ranking)

    geral = sorted(geral, key=lambda k: k['assistencias'], reverse=True)

    return render(request, "listas/lista_assistencias.html", {'racha': racha, 'ranking': geral})


def lista_de_jogadores(request):
    jogadores = Jogadores.objects.all().order_by('nome')
    return render(request, 'listas/lista_jogadores.html', {'jogadores': jogadores})


def lista_de_jogadores_racha(request, pk):
    try:
        racha = Rachas.objects.get(pk=pk)
        jogadores = JogadoresRacha.objects.filter(racha__pk=pk).order_by('jogador__nome')
        return render(request, 'listas/lista_jogadores_racha.html', {'jogadores': jogadores, 'racha': racha})
    except Rachas.DoesNotExists:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def lista_de_partidas(request):
    partidas = Partida.objects.all().order_by('-pk')
    return render(request, 'listas/lista_partidas.html', {'partidas': partidas})


def lista_de_partidas_racha(request, pk):
    partidas = Partida.objects.filter(racha__pk=pk).order_by('-data')

    racha = Rachas.objects.get(pk=pk)
    return render(request, 'listas/lista_partidas.html', {'partidas': partidas, 'racha': racha})

@login_required(login_url='/login')
def registro_partida(request, pk):
    partida = Partida.objects.get(pk=pk)

    registro = RegistroPartida.objects.filter(partida=partida).order_by('-tempo')

    return render(request, 'listas/registro_partida.html', {'registros': registro, 'partida': partida})

@login_required(login_url='/login')
def detalhe_jogador_racha(request, pk, racha_pk):

    jogador = JogadoresRacha.objects.get(jogador__pk=pk, racha__pk=racha_pk)

    return render(request, 'detalhes/detalhe_jogador_racha.html', {'jogador': jogador})

@login_required(login_url='/login')
def lista_premios(request, racha_pk):
    print("RACHA PK: ", racha_pk)
    racha = Rachas.objects.get(pk=racha_pk)
    premios = Premios.objects.filter(racha__pk=racha_pk)

    print(premios)
    return render(request, 'listas/lista_premios.html', {'premios': premios, 'racha': racha})

@login_required(login_url='/login')
def cadastrar_premios(request, racha_pk):
    racha = Rachas.objects.get(pk=racha_pk)
    return render(request, 'cadastros/cadastro_premios.html', {'racha': racha})

@login_required(login_url='/login')
def cadastrar_jogadores_racha(request, racha_pk):
    if request.method == 'POST':
        jogadores_selecionados = request.POST.getlist('jogadores')
        racha = Rachas.objects.get(pk=racha_pk)

        for j in jogadores_selecionados:
            jogador = Jogadores.objects.get(pk=j)
            jogador_racha = JogadoresRacha(jogador=jogador, racha=racha)
            jogador_racha.save()

        url = reverse('lista_de_jogadores_racha', args=[racha.pk])
        return HttpResponseRedirect(url)
    else:
        pks = []
        racha = Rachas.objects.get(pk=racha_pk)
        jogadores_racha = JogadoresRacha.objects.filter(racha=racha)

        for j in jogadores_racha:
            pks.append(j.jogador.pk)

        jogadores = Jogadores.objects.exclude(pk__in=pks)

        return render(request, 'cadastros/cadastro_jogadores_racha.html',
                      {'racha': racha, 'jogadores': jogadores, 'jogadores_racha': jogadores_racha})

@login_required(login_url='/login')
def marcar_presenca(request, partida_pk):
    try:
        partida = Partida.objects.get(pk=partida_pk)
        JogadoresPartida.objects.create(partida=partida, jogador=request.user.jogadores)
        messages.success(request, 'Presença marcada!')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Exception as e:
        messages.error(request, 'Erro ao marcar presença', e)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@login_required(login_url='/login')
def desmarcar_presenca(request, partida_pk):
    try:
        partida = Partida.objects.get(pk=partida_pk)
        jogador = JogadoresPartida.objects.get(partida=partida, jogador=request.user.jogadores)
        jogador.delete()
        messages.success(request, 'Presença cancelada!')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Exception as e:
        messages.error(request, 'Erro ao des'
                                ''
                                'marcar presença', e)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@login_required(login_url='/login')
def cadastrar_candidatos_premio(request, partida_pk):
    partida = Partida.objects.get(pk=partida_pk)

    if request.method == 'POST':
        racha = Partida.objects.get(pk=partida_pk)
        url = reverse('lista_de_jogadores_racha', args=[racha.pk])
        return HttpResponseRedirect(url)
    else:
        premios = Premios.objects.filter(racha=partida.racha).order_by('nome')
        jogadores_presentes = JogadoresPartida.objects.filter(partida=partida, presente=True).order_by('jogador')

        return render(request, 'cadastros/cadastro_candidatos.html',
                      {'partida': partida, 'jogadores': jogadores_presentes, 'premios': premios})

@login_required(login_url='/login')
def lista_balanco(request, racha_pk):
    balanco = Financeiro.objects.filter(racha__pk=racha_pk)
    return render(request, 'listas/lista_balanco.html', {'lista_balanco': balanco})
