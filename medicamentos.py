class Medicamentos:
    def __init__(self,nome,lote, preco):
        self.nome=nome
        self.lote=lote
        self.preco=preco


    def adicionar_medicamento(self):
        nome=input("Insira o nome do remédio: \n")
        lote=input("Insira o número do lote de distribuição do remédio: \n")
        preco=float(input("Insira o valor "))

    remedio=Medicamentos(nome, lote)