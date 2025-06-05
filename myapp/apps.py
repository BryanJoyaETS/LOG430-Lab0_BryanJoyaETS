"""
Module de configuration de l'application myapp.
"""

from django.apps import AppConfig


class MyappConfig(AppConfig):
    """
    Configuration de l'application myapp.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
