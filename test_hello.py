"""Fichier de test pour la fonction get_greeting() dans hello.py."""
# test_hello.py
from hello import get_greeting, get_greeting_uppercase

def test_get_greeting():
    """Teste si la fonction get_greeting retourne 'Hello World'"""
    assert get_greeting() == "Hello World."

def test_get_greeting_uppercase():
    """Teste si la fonction get_greeting_uppercase retourne 'HELLO WORLD'"""
    assert get_greeting_uppercase() == "HELLO WORLD."


