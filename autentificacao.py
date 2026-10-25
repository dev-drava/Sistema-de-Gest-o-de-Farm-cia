from admin import Administrador
from farmaceutico import Farmaceutico
from cliente import Cliente

def criar_utilizador(id,nome, palavra_passe, tipo):
    if tipo == "Admin":
        return Administrador(id,nome,palavra_passe)
    elif tipo == "Farmaceutico":
        return Farmaceutico(id,nome,palavra_passe)
    elif tipo == "Cliente":
        return Cliente(id,nome,palavra_passe)
    else:
        return None