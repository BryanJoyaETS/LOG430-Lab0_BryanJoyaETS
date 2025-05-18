"""Module hello.py - contient une fonction pour retourner un message de salutation."""

def get_greeting():
    """Retourne une salutation simple."""
    return "Hello World."

def get_greeting_uppercase():
    """Retourne la salutation en majuscules."""
    return get_greeting().upper()

def main():
    """Point d'entrée principal du programme."""
    print(get_greeting())

if __name__ == "__main__":
    main()
