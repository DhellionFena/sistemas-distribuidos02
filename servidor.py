import socket
import time
from banco import Banco, retornar_status_pedido
from random import randint
import threading
import os

class Servidor:
    def __init__(self, ip, porta, nome_banco, lista_de_servidores):
        self.IP = ip
        self.PORTA = porta

        self.tempo = randint(0, 10)
        self.lock = False

        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.servidor.bind((self.IP, self.PORTA))

        self.ativo = True    # Flag de status do servidor
        self.banco = Banco(nome_banco)

        self.lista_de_servidores = lista_de_servidores

    def iniciar(self):
        self.running = True

        while self.ativo:
            print("SERVIDOR DE BANCO: " + str(self.banco.nome).upper() + " TEMPO: " + str(self.tempo))
            data, addr = self.servidor.recvfrom(1024)

            if not self.lock:
                print(f"Server {self.PORTA} recebeu a mensagem '{data.decode()}' de {addr}")

                if data.decode() == "exit":
                    self.ativo = False

                if "request_time" in data.decode():
                    msg = data.decode().split(';')
                    self.resposta_tempo(msg[1], msg[2])

                if "teste" in data.decode():
                    msg = data.decode()
                    print(msg)

                if "update_status" in data.decode():
                    # "0;update_status;id;status"
                    msg = data.decode().split(';')
                    autorizacao = msg[0]
                    id_pedido = msg[2]
                    status = msg[3]
                    if autorizacao == '0':
                        if self.requisicao_tempo():
                            conteudo = id_pedido + ";" + status
                            self.enviar_processo('update_status', conteudo=conteudo)

                            retorno = self.banco.atualizar_pedido(id_pedido, status)
                            if retorno[0] == 200:
                                self.servidor.sendto(f"> Pedido atualizado com Sucesso!".encode(), addr)
                                self.tempo += 1
                            else:
                                self.servidor.sendto("> Ocorreu algum erro ao atualizar pedido.".encode(), addr)

                    else:
                        retorno = self.banco.atualizar_pedido(id_pedido, status)
                        if retorno[0] == 200:
                            print(f"> Pedido atualizado com Sucesso!")
                            self.tempo += 1
                        else:
                            print("> Ocorreu algum erro ao atualizar pedido.")

                if "create_delivery" in data.decode():
                    # "0;create_delivery;id;nome;status"
                    msg = data.decode().split(';')
                    autorizacao = msg[0]
                    id_motorista = msg[2]
                    nome = msg[3]
                    status = msg[4]
                    if autorizacao == '0':
                        if self.requisicao_tempo():
                            conteudo = id_motorista + ";" + nome + ";" + status
                            self.enviar_processo('create_delivery', conteudo=conteudo)
                            retorno = self.banco.criar_pedido(id_motorista, nome, status)
                            if retorno == 200:
                                self.servidor.sendto(f"> Pedido '{nome}' Criado com Sucesso!".encode(), addr)
                                self.tempo += 1
                            else:
                                self.servidor.sendto("> Ocorreu algum erro ao criar o motorista.".encode(), addr)

                    else:
                        retorno = self.banco.criar_pedido(id_motorista, nome, status) 
                        if retorno == 200:
                            print(f"> Pedido '{nome}' Criado com Sucesso!".encode(), addr)
                            self.tempo += 1
                        else:
                            print("> Ocorreu algum erro ao criar o motorista.".encode(), addr)

                if "list_deliveries" in data.decode():
                    msg = data.decode().split(";")
                    lista = self.banco.listar_pedidos(msg[1])
                    print(lista[1])
                    retorno = ''
                    for item in lista[1]:
                        retorno += f"> PEDIDO: {item[2]}  | STATUS: {retornar_status_pedido(item[3])} | ID = ({item[0]})\n"
                    self.servidor.sendto(retorno.encode(), addr)
                    self.tempo += 1

                if "list_drivers" in data.decode():
                    lista = self.banco.listar_motoristas()
                    print(lista[1])

                if "create_driver" in data.decode():
                    # "0;create_driver;NOME;EMAIL;SENHA;CPF"
                    msg = data.decode().split(';')
                    autorizacao = msg[0]
                    cliente = msg[2]
                    if autorizacao == '0':
                        if self.requisicao_tempo():
                            conteudo = msg[3] + ";" + msg[4] + ";" + msg[5] + ";" + msg[6]
                            self.enviar_processo('create_driver', conteudo=conteudo)

                            retorno = self.banco.criar_motorista(nome=msg[3], email=msg[4], senha=msg[5], cpf=msg[6])
                            
                            if retorno == 200:
                                self.servidor.sendto("> Motorista Criado com Sucesso!".encode(), ('localhost',int(cliente)))
                                self.tempo += 1
                            else:
                                self.servidor.sendto("> Ocorreu algum erro ao criar o motorista.".encode(), ('localhost',int(cliente)))

                    else:
                        retorno = self.banco.criar_motorista(nome=msg[2], email=msg[3], senha=msg[4], cpf=msg[5])
                        
                        if retorno == 200:
                            print(f"> Motorista Criado com Sucesso!   ({self.PORTA})")
                            self.tempo += 1
                        else:
                            print("> Ocorreu algum erro ao criar o motorista.")

                if "delete_driver" in data.decode():
                    # "0;create_driver;NOME;EMAIL;SENHA;CPF"
                    msg = data.decode().split(';')
                    autorizacao = msg[0]
                    cliente = msg[2]
                    if autorizacao == '0':
                        if self.requisicao_tempo():
                            conteudo = msg[2]
                            self.enviar_processo('delete_driver', conteudo=conteudo)

                            retorno = self.banco.deletar_conta(cliente)
                            
                            if retorno[0] == 200:
                                mensagem = '200;> Motorista Deletado com Sucesso!'
                                self.servidor.sendto(mensagem.encode(), addr)
                                self.tempo += 1
                            else:
                                self.servidor.sendto("> Ocorreu algum erro ao criar o motorista.".encode(), addr)

                    else:
                        retorno = self.banco.deletar_conta(cliente)
                        
                        if retorno[0] == 200:
                            print(f"> Motorista Deletado com Sucesso!   ({self.PORTA})")
                            self.tempo += 1
                        else:
                            print("> Ocorreu algum erro ao deletar o motorista.")

                if "access_driver" in data.decode():
                    # "0;access_driver;EMAIL;SENHA"
                    msg = data.decode().split(';')
                    retorno = self.banco.acessar_conta(email=msg[2], senha=msg[3])
                    if retorno[0] == 200:
                        mensagem = str(retorno[0]) + ";" + str(retorno[1]) + ";" + str(retorno[2])
                        self.servidor.sendto(mensagem.encode(), addr)
                        self.tempo += 1
                    else:
                        self.servidor.sendto("> Erro".encode(), addr)

            else:
                print("-=-=-=-=-=--=- ZONA DE LOCK -=-=-=-=-=--=-")
                if "request_time" in data.decode():
                    msg = data.decode().split(';')
                    self.resposta_tempo(msg[1], msg[2])
        
        self.servidor.close()
    
    def requisicao_tempo(self):
        lista_aprovacao = []
        tempo_aux = 0
        for servidor in self.lista_de_servidores:
            msg = "request_time;" + str(self.PORTA) + ";" + str(self.tempo)
            self.servidor.sendto(msg.encode(), ('localhost', servidor))
            data, addr = self.servidor.recvfrom(1024)
            data = data.decode().split(';')
            if data[1] == "True":
                lista_aprovacao.append(True)
            else:
                lista_aprovacao.append(False)
                if tempo_aux < int(data[2]):
                    tempo_aux = int(data[2]) + 1
        
        if False in lista_aprovacao:
            self.tempo = tempo_aux
            self.requisicao_tempo()
        
        return True

    def resposta_tempo(self, porta_remetente, tempo_remetente):
        porta_remetente = int(porta_remetente)
        if self.tempo < int(tempo_remetente):
            print("Recebi minha requisicao e posso!")
            msg = "response_time;True"
            self.lock = False
            self.servidor.sendto(msg.encode(), ('localhost', porta_remetente))
            self.tempo = int(tempo_remetente)
        else:
            print(f"Recebi minha requisicao e nao posso! Meu tempo: ({self.tempo})")
            msg = "response_time;False;" + str(self.tempo)
            self.lock = True
            self.servidor.sendto(msg.encode(), ('localhost', porta_remetente))
    
    def enviar_processo(self, flag, conteudo):
        for servidor in self.lista_de_servidores:
            msg = '1;' + flag + ";" + conteudo
            self.servidor.sendto(msg.encode(), ('localhost', servidor))

def iniciar_servidor( host, porta, banco, lista_de_servidores):
    servidor = Servidor(host, porta, banco, lista_de_servidores)
    servidor.iniciar()

if __name__ == '__main__':
    # Criar duas threads para cada servidor HTTP
    servidor1_thread = threading.Thread(target=iniciar_servidor, args=('localhost', 7069, 'banco1', [7070, 7079]))
    servidor2_thread = threading.Thread(target=iniciar_servidor, args=('localhost', 7070, 'banco2', [7069, 7079]))
    servidor3_thread = threading.Thread(target=iniciar_servidor, args=('localhost', 7079, 'banco3', [7069, 7070]))

    # Iniciar as threads
    servidor1_thread.start()
    servidor2_thread.start()
    servidor3_thread.start()

    # Esperar que as threads terminem
    servidor1_thread.join()
    servidor2_thread.join()
    servidor3_thread.join()