class Utilizador:
    def __init__(self,id,nome,palavra_passe,tipo):
        self.id = id
        self.nome = nome
        self.palavra_passe = palavra_passe
        self.tipo = tipo

    def obter_permissoes(self):
        return[]
    def tem_permissao(self, permissao):
        return permissao in self.obter_permissoes()
    
    def verificar_palavra_passe(self,palavra_passe):
        return palavra_passe == self.palavra_passe
