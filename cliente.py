from utilizador import Utilizador

class Cliente(Utilizador):
    def __init__(self, id, nome, palavra_passe, tipo):
        super().__init__(id, nome, palavra_passe, "Cliente")

    def obter_permissoes(self):
        return[
            "listar_medicamentos",
            "pesquisar_medicamentos",
            "efetuar_compra",
            "ver_historico_proprio",
        ]