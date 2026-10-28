
import autenticacao
import cliente
import farmaceutico
import medicamentos
import vendas

def mostrar_menu():
    print("     SISTEMA DE FARMÁCIA       ")
    print("1. Autenticação / Login")
    print("2. Gerir Clientes")
    print("3. Gerir Farmacêuticos")
    print("4. Gerir Medicamentos")
    print("5. Registar / Gerir Vendas")
    print("0. Sair")

    
def main():
    while True:
        mostrar_menu()
        opcao = input("Escolhe uma opção: ")

        if opcao == "1":
            print("\n-> a abrir menu de Autenticação...")
            
        elif opcao == "2":
            print("\n-> a abrir menu de Clientes...")
           
        elif opcao == "3":
            print("\n-> a abrir menu de Farmacêuticos...")
            
        elif opcao == "4":
            print("\n-> a abrir menu de Medicamentos...")
            
        elif opcao == "5":
            print("\n->  abrir menu de Vendas...")
            
            
        elif opcao == "0":
            print("\na sair do sistema. Até breve!")
            break
        else:
            print("\n Opção incorreta!  escolha uma opção válida.")

if __name__ == "__main__":
    main()