import autentificacao
import cliente
import farmaceutico
import medicamentos
import vendas

def mostrar_menu():
    print("\n      SISTEMA DE FARMÁCIA        ")
    print("1. Autenticação / Login")
    print("2. Gerir Clientes")
    print("3. Gerir Farmacêuticos")
    print("4. Gerir Medicamentos")
    print("5. Registar / Gerir Vendas")
    print("0. Sair")

def main():
    while True:
        mostrar_menu()
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            print("\n-> A abrir menu de Autenticação...")
            nome = input("Nome de utilizador: ").strip()
            senha = input("Palavra-passe: ").strip()
            # Se o módulo autenticacao tiver a função de login/autenticar
            if hasattr(autentificacao, "autenticar"):
                user = autentificacao.autenticar(nome, senha)
                if user:
                    print(f"Login bem-sucedido! Tipo de conta: {user.get('tipo', 'Desconhecido')}")
                else:
                    print("Credenciais inválidas.")
            else:
                print("Módulo de autenticação carregado.")
            
        elif opcao == "2":
            print("\n-> A abrir menu de Clientes...")
            if hasattr(cliente, "menu"):
                cliente.menu()
            else:
                print("Opções de cliente disponíveis no módulo.")
           
        elif opcao == "3":
            print("\n-> A abrir menu de Farmacêuticos...")
            if hasattr(farmaceutico, "menu"):
                farmaceutico.menu()
            else:
                print("Opções de farmacêutico disponíveis no módulo.")
           
        elif opcao == "4":
            print("\n-> A abrir menu de Medicamentos...")
            print("1) Listar medicamentos")
            print("2) Procurar medicamento")
            sub = input("Escolhe uma opção: ").strip()
            if sub == "1":
                try:
                    meds = medicamentos.listar()
                    for m in meds:
                        print(m)
                except Exception as e:
                    print(f"Erro ao listar: {e}")
            elif sub == "2":
                termo = input("Termo de pesquisa: ").strip()
                try:
                    meds = medicamentos.procurar(termo) if hasattr(medicamentos, "procurar") else []
                    for m in meds:
                        print(m)
                except Exception as e:
                    print(f"Erro ao procurar: {e}")
           
        elif opcao == "5":
            print("\n-> A abrir menu de Vendas...")
            print("1) Listar histórico de vendas")
            sub = input("Escolhe uma opção: ").strip()
            if sub == "1":
                try:
                    lista_vendas = vendas.listar_vendas() if hasattr(vendas, "listar_vendas") else []
                    for v in lista_vendas:
                        print(v)
                except Exception as e:
                    print(f"Erro ao listar vendas: {e}")
              
        elif opcao == "0":
            print("\nA sair do sistema. Até breve!")
            break
        else:
            print("\nOpção incorreta! Escolhe uma opção válida.")

if __name__ == "__main__":
    main()