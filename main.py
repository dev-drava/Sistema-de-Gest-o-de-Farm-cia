import autentificacao
import cliente
import farmaceutico
import medicamentos
import vendas

def mostrar_menu():
    print("\nSISTEMA DE FARMÁCIA")
    print("1. Gerir Medicamentos")
    print("2. Registar / Gerir Vendas")
    print("0. Sair")

def main():
    while True:
        mostrar_menu()
        opcao = input("Escolhe uma opção: ").strip()
              
        if opcao == "1":
            print("\nAbrindo menu de medicamentos.")
            if hasattr(medicamentos, "menu"):
                medicamentos.menu()
            else:
                try:
                    lista = medicamentos.listar()
                    print("\nMEDICAMENTOS EM STOCK")
                    for m in lista:
                        print(f"ID: {m.get('id')} | Nome: {m.get('nome')} | Preço: {m.get('preco')}€ | Stock: {m.get('stock')}")
                except Exception as e:
                    print(f"Erro ao aceder aos medicamentos: {e}")
              
        elif opcao == "2":
            print("\nAbrindo menu de vendas")
            if hasattr(vendas, "menu"):
                vendas.menu()
            else:
                try:
                    lista_vendas = vendas.listar_vendas()
                    print("\nHISTÓRICO DE VENDAS")
                    for v in lista_vendas:
                        print(v)
                except Exception as e:
                    print(f"Erro ao aceder às vendas: {e}")
              
        elif opcao == "0":
            print("\nEncerrando")
            break
        else:
            print("\nOpção errada, escolha uma correta")

if __name__ == "__main__":
    main()