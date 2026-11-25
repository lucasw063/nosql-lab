from .conexao import obter_banco
from bson import ObjectId
from datetime import datetime, timezone

banco = obter_banco()

def buscar_cursos(categoria=None, preco_max=None, tag=None):

    filtros = {}

    if categoria is not None:
        filtros["categoria"] = categoria

    if preco_max is not None:
        filtros["preco"] = {"$lte": preco_max}

    if tag is not None:
        filtros["tags"] = tag

    return list(
        banco.cursos.find(filtros, {"modulos": 0})
    )

def adicionar_modulo(curso_id, modulo):

    resultado = banco.cursos.update_one(
        {"_id": ObjectId(curso_id)},
        {"$push": {"modulos": modulo}}
    )

    return resultado.modified_count

def atualizar_progresso(matricula_id, progresso):

    if progresso < 0 or progresso > 100:
        raise ValueError("O progresso deve estar entre 0 e 100.")

    alteracoes = {
        "$set": {
            "progresso": progresso,
            "concluida": progresso == 100
        }
    }

    if progresso < 100:
        alteracoes["$unset"] = {"avaliacao": ""}

    resultado = banco.matriculas.update_one(
        {"_id": ObjectId(matricula_id)},
        alteracoes
    )

    return resultado.modified_count

def matricular_aluno(aluno_id, curso_id):

    aluno_id = ObjectId(aluno_id)
    curso_id = ObjectId(curso_id)

    with banco.client.start_session() as sessao:
        with sessao.start_transaction():

            aluno = banco.alunos.find_one(
                {"_id": aluno_id},
                session=sessao
            )

            if aluno is None:
                raise ValueError("Aluno não encontrado.")

            curso = banco.cursos.find_one(
                {"_id": curso_id},
                session=sessao
            )

            if curso is None:
                raise ValueError("Curso não encontrado.")

            existente = banco.matriculas.find_one({
                "aluno_id": aluno_id,
                "curso_id": curso_id
            }, session=sessao)

            if existente:
                raise ValueError("Aluno já matriculado neste curso.")

            resultado = banco.cursos.update_one(
                {"_id": curso_id, "vagas": {"$gt": 0}},
                {"$inc": {"vagas": -1}},
                session=sessao
            )

            if resultado.modified_count == 0:
                raise ValueError("Curso sem vagas disponíveis.")

            matricula = {
                "aluno_id": aluno_id,
                "curso_id": curso_id,
                "data": datetime.now(timezone.utc),
                "progresso": 0,
                "concluida": False
            }

            cadastro = banco.matriculas.insert_one(
                matricula, session=sessao
            )

    return cadastro.inserted_id

def avaliar_curso(matricula_id, nota):

    if nota < 1 or nota > 5:
        raise ValueError("A avaliação deve estar entre 1 e 5.")

    resultado = banco.matriculas.update_one(
        {
            "_id": ObjectId(matricula_id),
            "concluida": True
        },
        {
            "$set": {"avaliacao": nota}
        }
    )

    if resultado.matched_count == 0:
        raise ValueError("Matrícula inexistente ou curso não concluído.")

    return resultado.modified_count

def remover_aluno(aluno_id):

    aluno_id = ObjectId(aluno_id)

    with banco.client.start_session() as sessao:
        with sessao.start_transaction():

            matriculas = list(
                banco.matriculas.find(
                    {"aluno_id": aluno_id},
                    session=sessao
                )
            )

            for matricula in matriculas:

                banco.cursos.update_one(
                    {"_id": matricula["curso_id"]},
                    {"$inc": {"vagas": 1}},
                    session=sessao
                )

            banco.matriculas.delete_many(
                {"aluno_id": aluno_id},
                session=sessao
            )

            resultado = banco.alunos.delete_one(
                {"_id": aluno_id},
                session=sessao
            )

    return resultado.deleted_count

def relatorio_cursos_categoria():

    pipeline = [
        {
            "$group": {
                "_id": "$categoria",
                "quantidade": {"$sum": 1}
            }
        },
        {
            "$sort": {"quantidade": -1, "_id": 1}
        }
    ]

    return list(banco.cursos.aggregate(pipeline))

def relatorio_cursos_mais_matriculados():

    pipeline = [
        {
            "$group": {
                "_id": "$curso_id",
                "quantidade": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "cursos",
                "localField": "_id",
                "foreignField": "_id",
                "as": "curso"
            }
        },
        {
            "$unwind": "$curso"
        },
        {
            "$project": {
                "_id": 0,
                "titulo": "$curso.titulo",
                "quantidade": 1
            }
        },
        {
            "$sort": {"quantidade": -1, "titulo": 1}
        },
        {
            "$limit": 5
        }
    ]

    return list(banco.matriculas.aggregate(pipeline))

def relatorio_media_avaliacoes():

    pipeline = [
        {
            "$match": {
                "concluida": True,
                "avaliacao": {"$gte": 1, "$lte": 5}
            }
        },
        {
            "$group": {
                "_id": "$curso_id",
                "media": {"$avg": "$avaliacao"},
                "quantidade_avaliacoes": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "cursos",
                "localField": "_id",
                "foreignField": "_id",
                "as": "curso"
            }
        },
        {
            "$unwind": "$curso"
        },
        {
            "$project": {
                "_id": 0,
                "titulo": "$curso.titulo",
                "media": {"$round": ["$media", 2]},
                "quantidade_avaliacoes": 1
            }
        },
        {
            "$sort": {"media": -1, "titulo": 1}
        }
    ]

    return list(banco.matriculas.aggregate(pipeline))

