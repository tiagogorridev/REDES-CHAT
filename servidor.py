import socket
import threading

clients, names = {}, {} # Dicionários para armazenar clientes conectados e seus nomes
server_running = True  # Controle para o servidor estar rodando ou não

def broadcast(msg, exclude=None):  # Função para enviar mensagens a todos os clientes, exceto o remetente (opcional)
    for c in clients.values():  # Itera sobre todos os clientes conectados
        if c != exclude:  # Exclui o remetente se necessário
            try:
                c.send((msg + "\n").encode("utf-8"))  # Envia e converte a mensagem
            except:
                pass

def send_active_users(sock=None):  # Envia a lista de usuários ativos para todos
    active_users = ", ".join(names.keys())  # Lista de nomes ativos
    msg = f"Usuários ativos: {active_users}"
    if sock:  # Caso seja para um cliente específico usa o sock
        sock.send((msg + "\n").encode("utf-8"))
    else:
        broadcast(msg)

# Gerencia a interação com um cliente específico
def handle_client(sock, addr):  # Sock é associado ao cliente e Address ao IP e Porta
    try:
        # Solicita nome único
        while True:
            name = sock.recv(1024).decode("utf-8")  # Aguarda e converte o nome
            if name in names:
                sock.send("NOME_EM_USO\n".encode("utf-8"))
            else:
                sock.send("OK\n".encode("utf-8"))
                break

        clients[addr] = sock  # Armazena o socket do cliente no dicionario clients com o addres como chave
        names[name] = addr  # Armazena o address do cliente com nome como chave
        broadcast(f"{name} entrou no chat de {addr[0]}:{addr[1]}")
        send_active_users()

        # Loop para lidar com mensagens do cliente
        while True:
            msg = (sock.recv(1024).decode("utf-8").strip())  # Aguarda, converte e remove os espaços da mensagem

            if msg.startswith("@"): # Verifica se a msg é privada
                try:
                    target_name, private_msg = msg[1:].split(" ", 1)  # Divisão na mensagem (remove o @ inicial e fica: "destinatario: mensagem")
                    if target_name == name:
                        sock.send(
                            "Você não pode enviar mensagens privadas para si mesmo.\n".encode("utf-8"))
                    elif (target_name in names):  # Verifica se o destinatário está conectado
                        target_sock = clients[names[target_name]]  # Obtém o socket do destinatário a partir de names e clients
                        target_sock.send(f"{name}: {private_msg} (privado)\n".encode("utf-8"))
                    else:
                        sock.send(f"Usuário {target_name} não encontrado.\n".encode("utf-8"))
                except ValueError:
                    sock.send("Formato inválido. Use @nome mensagem.\n".encode("utf-8"))
            else:  # Mensagem pública
                broadcast(f"{name}: {msg}", exclude=sock)  # Envia para todos, exceto o remetente
    except:
        pass
    finally:
        # Remove o cliente ao desconectar
        if addr in clients:
            del clients[addr]
        if name in names:
            del names[name]
        broadcast(f"{name} saiu do chat.")
        send_active_users()
        sock.close()  # Fecha o socket do cliente

def start_server():
    global server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket, indicando que será IPv4 e TCP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar o endereço e porta após ser fechado
    server.bind(("0.0.0.0", 12345))  # Associa o socket a um endereço e porta
    server.listen()  # Habilita o socket para aceitar conexões
    print("Servidor está funcionando...")

    # Loop principal para aceitar conexões de clientes
    while server_running:
        try:
            sock, addr = server.accept()  # Aceita uma nova conexão
            threading.Thread(target=handle_client, args=(sock, addr), daemon=True).start()  # Inicia uma thread para cada cliente e será encerrada quando o server for desligado
        except:
            break

def stop_server():
    global server_running
    server_running = False  # Define o estado do servidor como inativo

start_server()
