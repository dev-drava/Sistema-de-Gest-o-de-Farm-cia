from utilizador import Utilizador

class Farmaceutico(Utilizador):
    def __init__(self, id, nome, palavra_passe):
        super().__init__(id, nome, palavra_passe, tipo="Farmaceutico")

    def obter_permissoes(self):
        return [
            "listar_medicamentos",
            "registar_venda",
            "repor_stock",
            "ver_vendas_proprias",
            "ver_stock",
        ]