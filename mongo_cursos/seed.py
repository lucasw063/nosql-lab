
import random
from datetime import datetime, timezone
from .conexao import obter_banco


# Garante a mesma sequência de dados aleatórios
random.seed(42)


def gerar_cursos():
    categorias = {
        "Programação": [
            "Python", "Java", "JavaScript",
            "C#", "React", "HTML e CSS"
        ],
        "Dados": [
            "SQL", "MongoDB", "Power BI",
            "Excel", "Ciência de Dados", "Estatística"
        ],
        "Design": [
            "Figma", "Photoshop", "UX Design",
            "UI Design", "Illustrator", "Canva"
        ],
        "Gestão": [
            "Gestão de Projetos", "Scrum", "Kanban",
            "Liderança", "Finanças", "Empreendedorismo"
        ],
        "Marketing": [
            "Marketing Digital", "SEO", "Redes Sociais",
            "Google Ads", "Copywriting", "Branding"
        ]
    }

    cursos = []

    for categoria, titulos in categorias.items():
        for titulo in titulos:

            curso = {
                "titulo": titulo,
                "categoria": categoria,
                "carga_horaria": random.randint(10, 80),
                "preco": round(random.uniform(49, 350), 2),
                "vagas": random.randint(10, 50),
                "tags": [categoria.lower(), "iniciante"],
                "instrutor": {
                    "nome": "Professor " + categoria,
                    "email": categoria.lower() + "@aprendamais.com"
                },
                "modulos": [
                    {
                        "ordem": 1,
                        "titulo": "Introdução",
                        "aulas": ["Apresentação", "Conceitos básicos"]
                    },
                    {
                        "ordem": 2,
                        "titulo": "Desenvolvimento",
                        "aulas": ["Teoria", "Exercícios"]
                    },
                    {
                        "ordem": 3,
                        "titulo": "Conclusão",
                        "aulas": ["Revisão", "Avaliação"]
                    }
                ]
            }

            cursos.append(curso)

    return cursos


def gerar_alunos():

    nomes = [
        "João", "Maria", "Pedro", "Ana", "Carlos",
        "Julia", "Marcos", "Paula", "Rafael", "Camila"
    ]

    alunos = []

    for nome in nomes:

        aluno = {
            "nome": nome,
            "email": nome.lower() + "@email.com",
            "data_cadastro": datetime.now(timezone.utc)
        }

        alunos.append(aluno)

    return alunos


def inserir_novos(colecao, documentos, campo, sessao):

    existentes = colecao.distinct(campo, session=sessao)

    novos = []

    for documento in documentos:
        if documento[campo] not in existentes:
            novos.append(documento)

    if novos:
        colecao.insert_many(novos, session=sessao)


def gerar_matriculas(banco, sessao):

    alunos = list(
        banco.alunos.find(session=sessao).sort("email", 1)
    )

    cursos = list(
        banco.cursos.find(session=sessao).sort("titulo", 1)
    )

    matriculas = []

    for aluno in alunos:

        cursos_escolhidos = random.sample(cursos, 3)

        for curso in cursos_escolhidos:

            progresso = random.choice([0, 25, 50, 75, 100])
            avaliacao = random.randint(1, 5)

            # Verifica se a matrícula já existe
            existente = banco.matriculas.find_one({
                "aluno_id": aluno["_id"],
                "curso_id": curso["_id"]
            }, session=sessao)

            if existente:
                continue

            # Reserva uma vaga no curso
            resultado = banco.cursos.update_one(
                {"_id": curso["_id"], "vagas": {"$gt": 0}},
                {"$inc": {"vagas": -1}},
                session=sessao
            )

            if resultado.modified_count == 0:
                raise ValueError("Curso sem vagas disponíveis!")

            matricula = {
                "aluno_id": aluno["_id"],
                "curso_id": curso["_id"],
                "data": datetime.now(timezone.utc),
                "progresso": progresso,
                "concluida": progresso == 100
            }

            if progresso == 100:
                matricula["avaliacao"] = avaliacao

            matriculas.append(matricula)

    if matriculas:
        banco.matriculas.insert_many(
            matriculas, session=sessao
        )


def popular_banco():

    banco = obter_banco()

    with banco.client.start_session() as sessao:
        with sessao.start_transaction():

            inserir_novos(
                banco.cursos, gerar_cursos(), "titulo", sessao
            )

            inserir_novos(
                banco.alunos, gerar_alunos(), "email", sessao
            )

            gerar_matriculas(banco, sessao)

    print("Carga inicial concluída!")
    print("Cursos:", banco.cursos.count_documents({}))
    print("Alunos:", banco.alunos.count_documents({}))
    print("Matrículas:", banco.matriculas.count_documents({}))


if __name__ == "__main__":
    popular_banco()
