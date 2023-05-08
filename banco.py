import sqlite3

class Banco:
    def __init__(self, nome):
        self.nome = nome
        self.iniciar()
    
    def iniciar(self):
        self.banco = sqlite3.connect(self.nome)

        # Cria uma tabela para armazenar os usuários (se ela não existir)
        self.banco.execute('''CREATE TABLE IF NOT EXISTS motoristas
             (ID INTEGER PRIMARY KEY AUTOINCREMENT,
             NOME TEXT NOT NULL,
             EMAIL TEXT NOT NULL UNIQUE,
             SENHA TEXT NOT NULL,
             CPF TEXT NOT NULL UNIQUE);''')

        self.banco.execute('''CREATE TABLE IF NOT EXISTS pedidos
             (ID INTEGER PRIMARY KEY AUTOINCREMENT,
             ID_MOTORISTA INTEGER NOT NULL,
             NOME TEXT NOT NULL,
             STATUS INTEGER NOT NULL,
             FOREIGN KEY(ID_MOTORISTA) REFERENCES motoristas(ID));''')

        self.salvar()
        self.encerrar_conexao()
    
    def salvar(self):
        self.banco.commit()

    def encerrar_conexao(self):
        self.banco.close()

    def criar_pedido(self, ID_motorista, nome, status):
        try:
            self.banco = sqlite3.connect(self.nome)
            self.banco.execute('INSERT INTO pedidos (ID_MOTORISTA, NOME, STATUS) VALUES (?, ?, ?)', (ID_motorista, nome, status))

            self.salvar()
            self.encerrar_conexao()
            return 200
        except:
            return 400
    
    def criar_motorista(self, nome, email, senha, cpf):
        try:
            self.banco = sqlite3.connect(self.nome)
            self.banco.execute('INSERT INTO motoristas (NOME, EMAIL, SENHA, CPF) VALUES (?, ?, ?, ?)', (nome, email, senha, cpf))
            self.salvar()
            self.encerrar_conexao()
            return 200
        except:
            return 400

    def acessar_conta(self, email, senha):
        try:
            self.banco = sqlite3.connect(self.nome)
            cliente = self.banco.execute('SELECT * FROM motoristas WHERE EMAIL = ? AND SENHA = ?', (email, senha))
            for i in cliente:
                id_cliente = i[0]
                nome = i[1]
            self.salvar()
            self.encerrar_conexao()

            return [200, id_cliente, nome]
        except:
            return (400, 'erro')

    def listar_pedidos(self, ID_motorista):
        try:
            self.banco = sqlite3.connect(self.nome)
            pedidos = self.banco.execute('SELECT * FROM pedidos WHERE ID_MOTORISTA = ?', (ID_motorista,)).fetchall()
            self.salvar()
            self.encerrar_conexao()

            return [200, pedidos]
        except:
            return (400, 'erro')

    def listar_motoristas(self):
        try:
            self.banco = sqlite3.connect(self.nome)
            motoristas = self.banco.execute('SELECT * FROM motoristas').fetchall()
            print(motoristas)
            self.salvar()
            self.encerrar_conexao()
            return [200, motoristas]
        except:
            return (400, 'erro')

    def deletar_conta(self, id):
        self.banco = sqlite3.connect('banco.db')
        self.banco.execute("DELETE FROM motoristas WHERE ID=?", (id,))
        mensagem = "> Motorista encerrado com sucesso!"
        codigo = 200
        self.salvar()
        self.encerrar_conexao()
        return [codigo, mensagem]

    def atualizar_pedido(self, id_pedido, status):
        '''
            Possíveis status:
            - Pedido criado (1)
            - Coleta Agendada (2)
            - Em transito (3)
            - Entregue (4)
        '''
        try:
            self.banco = sqlite3.connect(self.nome)
            self.banco.execute('UPDATE pedidos SET STATUS = ? WHERE ID = ?', (status, id_pedido))
            self.salvar()
            self.encerrar_conexao()

            return [200]
        except:
            return (400, 'erro')


def retornar_status_pedido(status):
    if status == 1:
        return "Pedido criado"
    elif status == 2:
        return "Coleta Agendada"
    elif status == 3:
        return "Em transito"
    elif status == 4:
        return "Entregue"