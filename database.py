
import mysql.connector
from mysql.connector import Error

# Usa a mesma configuração do projeto antigo.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "port": 3307,
    "database": "estoque_inteligente",
}


def conectar():
    """Abre uma conexão com o banco de dados existente."""
    return mysql.connector.connect(**DB_CONFIG)


def testar_conexao():
    """Verifica se o MySQL está acessível."""
    conexao = None

    try:
        conexao = conectar()

        if conexao.is_connected():
            print("Conexão com o MySQL realizada com sucesso!")
            print(f"Banco: {DB_CONFIG['database']}")
            return True

    except Error as erro:
        print(f"Erro ao conectar ao MySQL: {erro}")
        return False

    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()

    return False


if __name__ == "__main__":
    testar_conexao()
