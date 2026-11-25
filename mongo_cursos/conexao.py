
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)


def obter_banco():
    uri = os.getenv("MONGO_URI")
    nome_banco = os.getenv("MONGO_DB")

    cliente = MongoClient(uri)

    return cliente[nome_banco]


if __name__ == "__main__":
    try:
        banco = obter_banco()
        banco.command("ping")

        print("Conexão realizada com sucesso!")
        print("Banco de dados:", banco.name)

    except Exception as erro:
        print("Erro na conexão:", erro)
