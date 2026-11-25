
# Aprenda+ — Catálogo de Cursos

Projeto desenvolvido para a Avaliação de Grau 2 (G2)
da disciplina de Banco de Dados.

## Informações acadêmicas

- Aluno: Lucas Wagner Araújo
- Curso: Engenharia de Software
- Período: 4º período
- Disciplina: Banco de Dados
- Professor: Fábio Castro

## Objetivo

Desenvolver um sistema de gerenciamento de cursos,
alunos e matrículas utilizando Python e MongoDB,
aplicando conceitos de bancos de dados NoSQL,
modelagem de documentos, validação, CRUD,
transações e agregações.

## Tecnologias utilizadas

- Python
- MongoDB Atlas
- PyMongo
- Python-dotenv
- Git e GitHub

## Estrutura do projeto

    nosql-lab/
    ├── mongo_cursos/
    │   ├── __init__.py
    │   ├── conexao.py
    │   ├── modelagem.py
    │   ├── seed.py
    │   ├── repositorio.py
    │   └── main.py
    ├── .env.example
    ├── .gitignore
    ├── requirements.txt
    └── README.md

## Como executar

### 1. Clonar o repositório

    git clone URL_DO_REPOSITORIO
    cd nosql-lab

### 2. Criar o ambiente virtual

    python -m venv .venv

### 3. Ativar o ambiente virtual

No Windows PowerShell:

    .\.venv\Scripts\Activate.ps1

No Linux ou macOS:

    source .venv/bin/activate

### 4. Instalar as dependências

    python -m pip install -r requirements.txt

### 5. Configurar o MongoDB

Criar um cluster no MongoDB Atlas e configurar
um usuário com as permissões necessárias.

Criar um arquivo .env com base no .env.example:

    MONGO_URI=string_de_conexao
    MONGO_DB=aprendamais

As credenciais não são disponibilizadas no
repositório por questões de segurança.

### 6. Testar a conexão

    python -m mongo_cursos.conexao

### 7. Criar as coleções e validações

    python -m mongo_cursos.modelagem

### 8. Popular o banco de dados

    python -m mongo_cursos.seed

### 9. Executar o sistema

    python -m mongo_cursos.main

## Modelagem do banco de dados

O banco de dados possui três coleções.

### Cursos

Armazena título, categoria, carga horária,
preço, vagas disponíveis, tags, instrutor
e módulos.

Os módulos e o instrutor foram embutidos
no documento do curso, pois essas informações
normalmente são consultadas em conjunto.

Essa abordagem reduz a necessidade de consultas
a outras coleções e facilita a exibição dos cursos.

### Alunos

Armazena nome, e-mail e data de cadastro.

O campo e-mail possui um índice único,
impedindo o cadastro de e-mails duplicados.

### Matrículas

Armazena referências ao aluno e ao curso,
data da matrícula, progresso, situação de
conclusão e avaliação.

As matrículas foram armazenadas em uma coleção
separada porque um aluno pode participar de
vários cursos e um curso pode possuir vários
alunos.

Foi criado um índice composto único utilizando
aluno_id e curso_id para impedir matrículas
duplicadas.

## Validação dos dados

A coleção cursos utiliza JSON Schema para
garantir os campos obrigatórios e impedir
preços e vagas com valores negativos.

O arquivo modelagem.py realiza um teste
inserindo um curso com preço negativo,
demonstrando que o documento é rejeitado.

O sistema também verifica:

- Disponibilidade de vagas.
- Existência do aluno e do curso.
- Duplicidade de matrículas.
- Progresso entre 0 e 100%.
- Avaliações entre 1 e 5.
- Conclusão do curso antes da avaliação.

## Carga inicial

O arquivo seed.py utiliza a biblioteca random
e o método insert_many() para popular o banco.

A carga inicial contém:

- 30 cursos.
- 5 categorias.
- 10 alunos.
- 30 matrículas.

O script verifica os registros existentes
antes das inserções, evitando duplicações
em execuções consecutivas sobre a base inicial.

## Funcionalidades

O sistema possui um menu interativo que permite:

1. Buscar cursos por categoria, preço e tag.
2. Matricular alunos.
3. Atualizar o progresso.
4. Avaliar cursos concluídos.
5. Adicionar módulos.
6. Remover alunos e suas matrículas.
7. Exibir relatórios.

## Relatórios

Foram implementados três relatórios utilizando
o Aggregation Pipeline do MongoDB:

- Quantidade de cursos por categoria.
- Cinco cursos com maior número de matrículas.
- Média das avaliações por curso.

## Controle de transações

As operações de matrícula e exclusão de alunos
utilizam transações para garantir a atomicidade.

Ao realizar uma matrícula, o sistema reduz
uma vaga disponível e insere a matrícula.

Caso ocorra uma falha durante a transação,
as alterações são desfeitas, preservando a
consistência dos dados.

## Pergunta teórica

### Em que situação embutir as matrículas dentro
### do documento do curso seria um erro de modelagem?

Embutir as matrículas seria inadequado quando
um curso possuir uma grande quantidade de alunos
ou quando as matrículas forem atualizadas
frequentemente.

Isso faria o documento crescer continuamente,
podendo atingir o limite de 16 MB por documento
do MongoDB.

Além disso, carregar os dados de um curso junto
com todas as suas matrículas seria desnecessário
em muitas consultas, podendo prejudicar o
desempenho do sistema.

Por isso, foi utilizada uma coleção separada
para as matrículas, com referências aos alunos
e aos cursos, facilitando as consultas,
atualizações e o crescimento da aplicação.

## Referências

- Material apresentado na disciplina de Banco de Dados.
- Documentação oficial do MongoDB.
  https://www.mongodb.com/docs/
- Documentação do PyMongo.
  https://www.mongodb.com/docs/languages/python/pymongo-driver/current/
