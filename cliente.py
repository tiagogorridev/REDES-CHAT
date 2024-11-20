import socket, threading, tkinter as tk
from tkinter import simpledialog, messagebox  # Widgets de entrada de dados e exibição de mensagens

def receive_messages():
    global client
    try:
        while True:
            msg = client.recv(1024).decode('utf-8').strip()  # Aguarda, converte e remove espaços de msg vinda do server
            chat.config(state=tk.NORMAL) # Habilita a edição do widget
            chat.insert(tk.END, msg + '\n')  # Insere a msg no final do widget
            chat.config(state=tk.DISABLED) # Desabilita a edição do widget
    except OSError as e: # Caso a conexão for perdida
        print(f"Erro na recepção de mensagens: {e}")
        if client:
            client.close()
        client = None

# Função para enviar mensagens para o servidor
def send_message(event=None):
    global client
    if not client:  # Verifica se o socket ainda existe
        messagebox.showerror("Erro", "Você não está conectado ao servidor.")
        return

    msg = entry.get().strip()  # Obtém o texto digitado e remove espaços
    if msg:  # Verifica se a mensagem não está vazia
        try:
            if msg.startswith("@"):  # Verifica se é uma mensagem privada
                target_name, private_msg = msg[1:].split(" ", 1)  # Divide o destinatário e a mensagem
                if target_name == username:
                    chat.config(state=tk.NORMAL) # Habilita a edição do widget
                    chat.insert(tk.END, "Você não pode enviar mensagens privadas para si mesmo.\n")
                    chat.config(state=tk.DISABLED)
                else:  # Caso o destinatário seja válido
                    client.send(msg.encode("utf-8"))  # Envia a mensagem ao servidor
                    chat.config(state=tk.NORMAL) 
                    chat.insert(tk.END, f"Você: {private_msg} (privado para {target_name})\n") # Adiciona a msg no final do chat
                    chat.config(state=tk.DISABLED)
            else:  # Mensagem pública
                client.send(msg.encode("utf-8"))
                chat.config(state=tk.NORMAL)
                chat.insert(tk.END, f"Você: {msg}\n")  # Exibe a mensagem no chat local
                chat.config(state=tk.DISABLED)
            entry.delete(0, tk.END)  # Limpa o campo de entrada após enviar a mensagem
        except OSError as e:
            messagebox.showerror("Erro de conexão", f"Falha ao enviar mensagem: {e}")

def exit_chat():
    global client
    try:
        client.close()
    except:
        pass
    client = None  # Remove a referência ao socket
    root.destroy()  # Fecha a janela principal do chat

def request_username():
    while True:
        username = simpledialog.askstring("Nome", "Digite seu nome (sem espaços ou @):")
        if username is None:  # Verifica se o usuário clicou em "Cancelar"
            client.close()
            exit()
        if not username or ' ' in username or '@' in username:  # Verifica se o nome é inválido
            messagebox.showerror("Nome inválido", "O nome não pode conter espaços ou '@'.")
            continue  # Pede o nome novamente
        client.send(username.encode('utf-8'))  # Envia o nome ao servidor
        response = client.recv(1024).decode('utf-8').strip()  # Recebe a resposta do servidor
        if response == "OK":
            return username
        else:
            messagebox.showerror("Nome em uso", "Esse nome já está em uso. Tente outro.")

# Bloco principal para conexão e inicialização do chat
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket, indicando que será IPv4 e TCP
    client.connect(('192.168.1.12', 12345))  # Conecta ao servidor no IP e porta especificados
    username = request_username()
    root = tk.Tk()
    root.title(f"Chat de {username}")
    chat = tk.Text(root, state=tk.DISABLED)  # Cria um campo de texto desabilitado para exibir o chat
    chat.pack()  # Adiciona o widget chat a janela
    entry = tk.Entry(root)  # Cria um campo de entrada para digitar mensagens
    entry.pack()  # Adiciona o campo de entrada à janela
    entry.bind("<Return>", send_message)
    tk.Button(root, text="Enviar", command=send_message).pack()
    tk.Button(root, text="Sair", command=exit_chat).pack()
    threading.Thread(target=receive_messages, daemon=True).start()  # Inicia uma thread para receber mensagens do servidor e é fechada automaticamente quando o finalizado
    root.mainloop()
except Exception as e:
    if client:
        client.close()
    client = None # Fecha o socket cliente
    messagebox.showerror("Erro de conexão", f"Erro: {e}")