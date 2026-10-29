
import threading
import time
import servidor
import app_cliente


def iniciar_servidor():
    threading.Thread(
        target=servidor.iniciar_servidor,
        daemon=True
    ).start()


def main():
    iniciar_servidor()
    time.sleep(1)

    try:
        cliente = app_cliente.ligar()
        app_cliente.menu_inicial(cliente)
        cliente.close()
    except ConnectionRefusedError:
        print("Não foi possível ligar ao servidor.")
    except KeyboardInterrupt:
        print("\nSistema encerrado.")


if __name__ == "__main__":
    main()
