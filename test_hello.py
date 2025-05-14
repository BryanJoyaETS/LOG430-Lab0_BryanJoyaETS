"""Fichier de test pour la fonction get_greeting() dans hello.py."""
# test_hello.py
from hello import get_greeting

def test_get_greeting():
    """Teste si la fonction get_greeting retourne 'Hello World'"""
    assert get_greeting() == "Hello World"
