
class Cliente:
    def __init__(self, id_utilizador, nome, palavra_passe_hash, tipo="Cliente"):
        self.id = id_utilizador
        self.nome = nome
        self.palavra_passe_hash = palavra_passe_hash
        self.tipo = tipo

    def tem_permissao(self, acao):
        permissoes_cliente = ["LISTAR", "PESQUISAR", "COMPRAR", "HISTORICO"]
        return acao in permissoes_cliente