from django.contrib import admin
from cadastros.models import *

# Register your models here.


# class JogadoresAdmin(admin.ModelAdmin):
#     list_display = ('nome','user')
#     search_fields = ('nome','user','telefone','foto')
    
#     def get_queryset(self, request):
#         # queryset = super(JogadoresAdmin,self).get_queryset(request)
#         # return queryset

    # def get_ordering(self, request):
    #     return [self.nome.lower()]

admin.site.register(Jogadores)
admin.site.register(Rachas)
admin.site.register(Premios)
admin.site.register(Partida)
admin.site.register(RegistroPartida)
admin.site.register(PremioPartida)
admin.site.register(JogadoresPartida)
admin.site.register(JogadoresRacha)
admin.site.register(CandidatoPremio)
admin.site.register(Votacao)
admin.site.register(Financeiro)
