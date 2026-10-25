from utilizador import Utilizador

class Administrador(Utilizador):
    def __init__(self, id, nome, palavra_passe):
        super().__init__(id, nome, palavra_passe,"Admin")
    
    def obter_permissoes(self):
        return[
            "adicionar_medicamento",
            "atualizar_medicamento",
            "remover_medicamento",
            "consultar_stock",
            "criar_farmaceutico",
        ]
    