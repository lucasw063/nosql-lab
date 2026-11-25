
from .conexao import obter_banco
from pymongo.errors import WriteError


def criar_colecoes(banco):

    # Regras de validação dos cursos
    validador = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "titulo",
                "categoria",
                "preco",
                "vagas",
                "modulos"
            ],
            "properties": {
                "titulo": {
                    "bsonType": "string"
                },
                "categoria": {
                    "bsonType": "string"
                },
                "preco": {
                    "bsonType": ["double", "int", "long", "decimal"],
                    "minimum": 0
                },
                "vagas": {
                    "bsonType": ["int", "long"],
                    "minimum": 0
                },
                "modulos": {
                    "bsonType": "array"
                }
            }
        }
    }

    # Verifica se as coleções já existem
    colecoes = banco.list_collection_names()

    if "cursos" not in colecoes:
        banco.create_collection(
            "cursos",
            validator=validador
        )
    else:
        banco.command(
            "collMod",
            "cursos",
            validator=validador
        )

    if "alunos" not in colecoes:
        banco.create_collection("alunos")

    if "matriculas" not in colecoes:
        banco.create_collection("matriculas")

    # Impede e-mails duplicados
    banco.alunos.create_index("email", unique=True)

    # Impede matrículas duplicadas
    banco.matriculas.create_index(
        [("aluno_id", 1), ("curso_id", 1)],
        unique=True
    )

    print("Coleções e validações configuradas!")


def testar_validacao(banco):

    curso_invalido = {
        "titulo": "Curso de Teste",
        "categoria": "Tecnologia",
        "preco": -100,
        "vagas": 10,
        "modulos": []
    }

    try:
        resultado = banco.cursos.insert_one(curso_invalido)

    except WriteError as erro:
        if erro.code == 121:
            print("Teste realizado: preço negativo rejeitado!")
        else:
            raise

    else:
        banco.cursos.delete_one({"_id": resultado.inserted_id})
        print("Erro: a validação não funcionou!")


if __name__ == "__main__":

    banco = obter_banco()

    criar_colecoes(banco)

    testar_validacao(banco)
