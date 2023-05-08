import socket
import os

class Motorista:

    def __init__(self, HOST, PORT):
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.servidor = ('localhost', 6969)
        self.HOST = HOST
        self.PORT = PORT
        self.cliente.bind((self.HOST, self.PORT))


        self.conta_acessada = False
    
    def testar_conexao(self):
        mensagem = "teste".encode()
        self.cliente.sendto(mensagem, self.servidor)
        data = self.cliente.recv(1024).decode()
        print(data)

    def encerrar_conexao(self):
        print("> Encerrando conexão.")
        os.system("pause")
        exit()

    def criar_usuario(self):
        nome = input("> Insira seu nome:\n> ")
        email = input("> Insira seu email:\n> ")
        senha = input("> Insira sua senha:\n> ")
        cpf = input("> Insira seu cpf:\n> ")
        mensagem = "0;create_driver;"+ str(self.PORT) + ";" + nome + ";" + email + ";" + senha + ";" + cpf
        self.cliente.sendto(mensagem.encode(), self.servidor)
        data, addr = self.cliente.recvfrom(1024)
        data = data.decode()
        print("> " + data)

    def criar_pedido(self):
        nome = input("> Insira o nome do Pedido:\n> ")
        status = "1"
        mensagem = "0;create_delivery;" + self.id_cliente + ";"+ nome + ";" + status
        self.cliente.sendto(mensagem.encode(), self.servidor)
        data, addr = self.cliente.recvfrom(1024)
        data = data.decode()
        print(data)
        

    def atualizar_pedido(self):
        self.listar_pedidos()
        pedido = input("> Digite qual pedido você deseja atualizar: \n> ")
        print("----------------------------")
        print("> (1) Pedido criado")
        print("> (2) Coleta Agendada")
        print("> (3) Em transito")
        print("> (4) Entregue")
        status = input("> Digite qual status seu pedido tera: \n> ")
        mensagem = '0;update_status;' + pedido + ';' + status
        self.cliente.sendto(mensagem.encode(), self.servidor)
        data, addr = self.cliente.recvfrom(1024)
        data = data.decode()
        print(data)

    def acessar_conta(self):
        email = input("> Insira seu email:\n> ")
        senha = input("> Insira sua senha:\n> ")
        mensagem = "0;access_driver;" + email + ";" + senha
        self.cliente.sendto(mensagem.encode(), self.servidor)
        data, addr = self.cliente.recvfrom(1024)
        data = data.decode().split(';')
        print(data)
        if (data[0] == '200'):
            self.conta_acessada = True
            self.id_cliente = data[1]
            self.nome = data[2]
        else:
            print("> Algum erro aconteceu.")

    def listar_pedidos(self):
        mensagem = "list_deliveries;" + str(self.id_cliente)
        self.cliente.sendto(mensagem.encode(), self.servidor)
        data, addr = self.cliente.recvfrom(1024)
        print(data.decode())

    def listar_motoristas(self):
        mensagem = "list_drivers"
        self.cliente.sendto(mensagem.encode(), self.servidor)

    def deletar_conta(self):
        mensagem = "0;delete_driver;" + self.id_cliente
        self.cliente.sendto(mensagem.encode(), self.servidor)
        data, addr = self.cliente.recvfrom(1024).decode()
        data = data.split(';')
        if (data[0] == '200'):
            print(data[1])
            self.conta_acessada = False
        else:
            print(data[0])
    
    def iniciar(self):

        while True:
            os.system("cls")
            if not self.conta_acessada:
                print("> Escolha as opções:")
                print("[1] Acessar Conta")
                print("[2] Criar Conta")
                print("[0] Finalizar Conexão")
                resposta = int(input("> "))

                if resposta == 69:
                    self.testar_conexao()
                    os.system("pause")
                elif resposta == 1:
                    self.acessar_conta()
                    os.system("pause")
                elif resposta == 2:
                    self.criar_usuario()
                    os.system("pause")
                elif resposta == 3:
                    self.listar_motoristas()
                    os.system("pause")
                elif resposta == 0:
                    self.encerrar_conexao()
                    break
                else:
                    print("> Opção Inválida!")
                    os.system("pause")
            else:
                print("> Olá " + self.nome + "! O que deseja fazer?")
                print("[1] Criar Pedido")
                print("[2] Atualizar Pedido")
                print("[3] Listar Pedidos")
                print("[4] Deletar Conta")
                print("[0] Finalizar Conexão")
                resposta = int(input("> "))

                if resposta == 1:
                    self.criar_pedido()
                    os.system("pause")
                elif resposta == 2:
                    self.atualizar_pedido()
                    os.system("pause")
                elif resposta == 3:
                    self.listar_pedidos()
                    os.system("pause")
                elif resposta == 4:
                    self.encerrar_conta()
                    os.system("pause")
                elif resposta == 0:
                    self.encerrar_conexao()
                    break
                else:
                    print("> Opção Inválida!")
                    os.system("pause")

if __name__ == '__main__':
    motorista = Motorista('localhost', 7080)
    motorista.iniciar()