from django.core.paginator import Paginator
from application_multi_magasins.models import Magasin

"""Service pour gérer les opérations liées aux magasins."""
def get_paginated_magasins(request, per_page=10):
    """
    Retourne la liste paginée des magasins.
    
    :param request: L'objet HttpRequest pour récupérer les paramètres (ex. la page).
    :param per_page: Nombre d'éléments par page (par défaut 10).
    :return: Un objet Page contenant les magasins pour la page demandée.
    """
    magasins_list = Magasin.objects.all()
    paginator = Paginator(magasins_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
