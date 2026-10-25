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

    
 def procurar_utilizador(nome, utilizadores):
    for u in utilizadores:
        if u.nome == nome:
            return u
    return None


def fazer_login(nome, palavra_passe, utilizadores):
    u = procurar_utilizador(nome, utilizadores)

    if u is None:
        return "login_invalido"

    if u.verificar_palavra_passe(palavra_passe):
        return "login_ok"
    else:
        return "login_invalido"


def verificar_permissao(utilizador, permissao):
    if utilizador.tem_permissao(permissao):
        return True
    else:
        return "permissao_negada"