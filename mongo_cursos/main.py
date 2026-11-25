from . import repositorio as repo
from pymongo.errors import PyMongoError

def selecionar(lista, campo):

    if not lista:
        print("Nenhum registro encontrado.")
        return None

    for numero, item in enumerate(lista, start=1):
        print(f"{numero} - {item[campo]}")

    print("0 - Cancelar")

    escolha = int(input("Selecione: "))

    if escolha == 0:
        return None

    if escolha < 1 or escolha > len(lista):
        raise ValueError("Opção inválida.")

    return lista[escolha - 1]

def menu_buscar_cursos():

    print("\n--- BUSCAR CURSOS ---")

    categoria = input("Categoria: ") or None
    preco = input("Preço máximo: ")
    tag = input("Tag: ") or None

    if preco:
        preco = float(preco.replace(",", "."))
    else:
        preco = None

    cursos = repo.buscar_cursos(categoria, preco, tag)

    for curso in cursos:
        print(
            f"{curso['titulo']} | "
            f"{curso['categoria']} | "
            f"R$ {curso['preco']:.2f} | "
            f"Vagas: {curso['vagas']}"
        )

    print(f"\nTotal encontrado: {len(cursos)}")

def menu_matricular():

    print("\n--- MATRICULAR ALUNO ---")

    alunos = list(repo.banco.alunos.find())

    aluno = selecionar(alunos, "nome")

    if aluno is None:
        return

    cursos = list(
        repo.banco.cursos.find({"vagas": {"$gt": 0}})
    )

    curso = selecionar(cursos, "titulo")

    if curso is None:
        return

    repo.matricular_aluno(
        aluno["_id"],
        curso["_id"]
    )

    print("Matrícula realizada com sucesso!")

def selecionar_matricula():

    alunos = list(repo.banco.alunos.find())

    aluno = selecionar(alunos, "nome")

    if aluno is None:
        return None

    matriculas = list(
        repo.banco.matriculas.find({
            "aluno_id": aluno["_id"]
        })
    )

    for matricula in matriculas:

        curso = repo.banco.cursos.find_one({
            "_id": matricula["curso_id"]
        })

        matricula["descricao"] = (
            f"{curso['titulo']} - "
            f"{matricula['progresso']}%"
        )

    return selecionar(matriculas, "descricao")

def menu_atualizar_progresso():

    print("\n--- ATUALIZAR PROGRESSO ---")

    matricula = selecionar_matricula()

    if matricula is None:
        return

    progresso = int(input("Novo progresso (0 a 100): "))

    repo.atualizar_progresso(
        matricula["_id"],
        progresso
    )

    print("Progresso registrado com sucesso!")

def menu_avaliar():

    print("\n--- AVALIAR CURSO ---")

    matricula = selecionar_matricula()

    if matricula is None:
        return

    nota = int(input("Nota de 1 a 5: "))

    repo.avaliar_curso(
        matricula["_id"],
        nota
    )

    print("Avaliação registrada com sucesso!")

def menu_adicionar_modulo():

    print("\n--- ADICIONAR MÓDULO ---")

    cursos = list(repo.banco.cursos.find())

    curso = selecionar(cursos, "titulo")

    if curso is None:
        return

    titulo = input("Título do módulo: ")
    aulas = input("Aulas separadas por vírgula: ")

    ordem = max(
        (m["ordem"] for m in curso["modulos"]),
        default=0
    ) + 1

    modulo = {
        "ordem": ordem,
        "titulo": titulo,
        "aulas": [
            aula.strip()
            for aula in aulas.split(",")
            if aula.strip()
        ]
    }

    repo.adicionar_modulo(curso["_id"], modulo)

    print("Módulo adicionado com sucesso!")

def menu_remover_aluno():

    print("\n--- REMOVER ALUNO ---")

    alunos = list(repo.banco.alunos.find())

    aluno = selecionar(alunos, "nome")

    if aluno is None:
        return

    confirmar = input(
        f"Excluir {aluno['nome']} e suas matrículas? (s/n): "
    )

    if confirmar.lower() == "s":

        repo.remover_aluno(aluno["_id"])

        print("Aluno e matrículas excluídos!")

    else:
        print("Operação cancelada.")

def menu_relatorios():

    print("\n--- CURSOS POR CATEGORIA ---")

    for item in repo.relatorio_cursos_categoria():
        print(
            f"{item['_id']}: "
            f"{item['quantidade']} cursos"
        )

    print("\n--- CURSOS MAIS MATRICULADOS ---")

    for item in repo.relatorio_cursos_mais_matriculados():
        print(
            f"{item['titulo']}: "
            f"{item['quantidade']} matrículas"
        )

    print("\n--- MÉDIA DAS AVALIAÇÕES ---")

    for item in repo.relatorio_media_avaliacoes():
        print(
            f"{item['titulo']}: "
            f"{item['media']:.2f}/5 | "
            f"{item['quantidade_avaliacoes']} avaliações"
        )

def main():

    while True:

        print("\n========================================")
        print("     APRENDA+ | CATÁLOGO DE CURSOS")
        print("========================================")
        print("1 - Buscar cursos")
        print("2 - Matricular aluno")
        print("3 - Atualizar progresso")
        print("4 - Avaliar curso")
        print("5 - Adicionar módulo")
        print("6 - Remover aluno")
        print("7 - Exibir relatórios")
        print("0 - Sair")

        opcao = input("\nEscolha uma opção: ")

        try:

            if opcao == "1":
                menu_buscar_cursos()

            elif opcao == "2":
                menu_matricular()

            elif opcao == "3":
                menu_atualizar_progresso()

            elif opcao == "4":
                menu_avaliar()

            elif opcao == "5":
                menu_adicionar_modulo()

            elif opcao == "6":
                menu_remover_aluno()

            elif opcao == "7":
                menu_relatorios()

            elif opcao == "0":
                print("Programa encerrado.")
                break

            else:
                print("Opção inválida!")

        except ValueError as erro:
            print("Erro:", erro)

        except PyMongoError as erro:
            print("Erro no banco de dados:", erro)

        input("\nPressione Enter para continuar...")


if __name__ == "__main__":
    main()