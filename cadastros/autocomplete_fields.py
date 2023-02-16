from dal import autocomplete
from cadastros.models import *


class AutocompleteJogadoresPresentes(autocomplete.Select2QuerySetView):
    def get_queryset(self):        
        if not self.request.user.is_authenticated():
            return Cargo.objects.none()

        qs = Jogadores.objects.all().order_by('nome')

        if self.q:
            qs = qs.filter(jogador__icontains=self.q)

        return qs


class AutocompleteAssistente(autocomplete.Select2QuerySetView):
    def get_queryset(self):        
        # qs = Jogadores.objects.all()
        # if self.q:
        #     qs = qs.filter(nome__icontains=self.q)

        # return qs

        if not self.request.user.is_authenticated():
            return Cargo.objects.none()

        qs = Jogadores.objects.all().order_by('nome')

        if self.q:
            qs = qs.filter(jogador__icontains=self.q)

        return qs