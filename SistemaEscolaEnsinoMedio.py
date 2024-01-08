# Importar biblioteca para interagir com bancos de dados SQLite
import sqlite3
# Importa o módulo random para geração de números aleatórios usado para criar o RA e distrubuir as salas
import random

# Conectar ao banco de dados
conexao = sqlite3.connect('BancoEscola.db')
cursor = conexao.cursor()

# Constante para representar o limite de alunos por sala
LIMITE_ALUNOS_POR_SALA = 40

# Função para obter o próximo RA disponível
def obter_proximo_ra(serie, sala):
    # Consulta os RAs já existentes para a série e sala especificadas
    cursor.execute("SELECT ra FROM alunos WHERE serie=? AND sala=?", (serie, sala))
    # Executa uma consulta SQL no banco de dados usando o cursor e cria um conjunto de números inteiros a partir dos resultados
    ras_usados = set(int(result[0]) for result in cursor.fetchall())

    while True:
        # Gera um número aleatório de 7 dígitos
        ra_intermediario = str(random.randint(1000000, 9999999))
        # Concatena a série, os dígitos aleatórios e o número da sala para formar o RA completo, sendo série o primeiro dígito e sala o último, com 7 aleatórios entre eles
        novo_ra = int(f"{serie}{ra_intermediario}{sala}")
        # Verifica se o RA gerado é único para a série e sala
        if novo_ra not in ras_usados:
            return str(novo_ra)

# Função para verificar se uma sala está lotada
def sala_lotada(serie, sala):
    # Consulta a quantidade de alunos na sala
    cursor.execute("SELECT COUNT(*) FROM alunos WHERE serie=? AND sala=?", (serie, sala))
    # Obtém o resultado da consulta como uma tupla e acessa o primeiro (e único) elemento (contagem de alunos)
    quantidade_alunos = cursor.fetchone()[0]
    return quantidade_alunos >= LIMITE_ALUNOS_POR_SALA

# Função para encontrar uma sala vazia e alocar o aluno aleatoriamente
def alocar_sala_aleatoria(serie):
    salas_disponiveis = [1, 2, 3, 4]

    # Remove salas que já atingiram o limite de alunos
    for sala in range(1, 5):
        if sala_lotada(serie, sala):
            salas_disponiveis.remove(sala)

    if not salas_disponiveis:
        return None  # Todas as salas estão lotadas
    
    # Obtém a a sala de forma aleatória, se disponível
    return random.choice(salas_disponiveis)

# Função para validar entrada de texto, aceitando somente letras e espaços
def validar_texto(pergunta):
    while True:
        resposta = input(pergunta)
        if resposta.replace(" ", "").isalpha():
            return resposta
        else:
            print("Erro de digitação. Por favor, responda apenas com texto.")

# Função para validar entrada de idade, sendo qualquer número maior que 0
def validar_idade(pergunta):
    while True:
        try:
            idade = int(input(pergunta))
            if idade > 0:
                return idade
            else:
                print("A idade deve ser maior que 0. Tente novamente.")
        except ValueError:
            print("Erro de digitação. Por favor, insira um número inteiro para a idade.")

# Função para validar entrada de série, sendo somente 1, 2 e 3
def validar_serie():
    while True:
        try:
            serie = int(input("Série (1, 2 ou 3): "))
            if serie in [1, 2, 3]:
                return serie
            else:
                print("A série deve ser 1, 2 ou 3. Tente novamente.")
        except ValueError:
            print("Erro de digitação. Por favor, insira um número inteiro para a série.")

# Função para validar entrada de UF, aceita somente 2 letras, nada diferente disso
def validar_uf(pergunta):
    while True:
        uf = input(pergunta).upper()

        if len(uf) == 2 and uf.isalpha():
            return uf
        else:
            print("Erro. A UF deve conter exatamente 2 letras maiúsculas. Tente novamente.")

# Função para cadastrar um novo aluno
def cadastrar_aluno():
    print("\n== Cadastrar Novo Aluno ==\n")

    # Solicita dados do aluno
    nome = validar_texto("Nome do aluno: ")
    idade = validar_idade("Idade do aluno: ")
    cidade_nascimento = validar_texto("Cidade de nascimento do aluno: ")
    uf = validar_uf("UF do aluno (2 letras maiúsculas). Estrangeiro colocar NA (Não Aplicável): ")

    # Garante que a UF fornecida tenha exatamente 2 caracteres, solicitando correção caso contrário.
    while len(uf) != 2:
        print("Erro de digitação. A UF deve conter exatamente 2 caracteres.")
        uf = input("UF do aluno (2 caracteres): ").upper()

    # Solicita ao usuário se o aluno é estrangeiro, aceitando apenas 'S' ou 'N' como respostas válidas.
    estrangeiro = input("O aluno é estrangeiro? (S/N): ").upper()

    # Garante que a resposta sobre ser estrangeiro seja 'S' ou 'N', solicitando correção caso contrário.
    while estrangeiro not in ['S', 'N']:
        print("Erro de digitação. Responda com 'S' para Sim ou 'N' para Não.")
        estrangeiro = input("O aluno é estrangeiro? (S/N): ").upper()

    # Aloca o aluno em uma sala aleatória disponível
    serie = validar_serie()
    sala = alocar_sala_aleatoria(serie)

    if sala is None:
        # Informa ao usuário que todas as salas estão lotadas
        print("\nDesculpe, todas as salas estão lotadas. Não há vagas no momento. Por favor, retorne no próximo trimestre.\n")
        return

    # Obtém o próximo RA disponível
    ra = obter_proximo_ra(serie, sala)

    # Insere o aluno na tabela 'alunos'
    cursor.execute("INSERT INTO alunos (nome, idade, cidade_nascimento, uf, estrangeiro, serie, sala, ra) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (nome, idade, cidade_nascimento, uf, estrangeiro, serie, sala, ra))
    conexao.commit()

    # Informa ao usuário que o aluno foi cadastrado com sucesso
    print(f"\nAluno {nome} cadastrado com RA {ra} na Série {serie}, Sala {sala}.\n")

# Função para remover um aluno
def remover_aluno():
    print("\n== Remover Aluno ==\n")

    # Solicita o RA do aluno a ser removido
    ra_aluno_remover = input("Digite o RA do aluno a ser removido: ")

    # Consulta o nome e RA do aluno pelo RA fornecido
    cursor.execute("SELECT nome, ra FROM alunos WHERE ra=?", (ra_aluno_remover,))
    aluno_remover = cursor.fetchone()

    # Verifica se o aluno foi encontrado
    if aluno_remover:
        # Pede confirmação ao usuário antes de remover
        confirmacao = input(f"Tem certeza que deseja excluir o aluno {aluno_remover[0]} (RA: {aluno_remover[1]})? (S/N): ").upper()

        if confirmacao == 'S':
            # Remove o aluno da tabela 'alunos'
            cursor.execute("DELETE FROM alunos WHERE ra=?", (ra_aluno_remover,))
            conexao.commit()
            # Informa ao usuário que o aluno foi removido com sucesso
            print(f"\nAluno {aluno_remover[0]} (RA: {aluno_remover[1]}) excluído com sucesso!\n")
        else:
            # Informa ao usuário que a exclusão foi cancelada
            print("\nExclusão cancelação cancelada.\n")
    else:
        # Informa ao usuário que o aluno não foi encontrado
        print("\nAluno não encontrado.\n")

# Função para alterar o cadastro de um aluno
def alterar_cadastro_aluno():
    print("\n== Alterar Cadastro do Aluno ==\n")

    # Solicita o RA do aluno a ser alterado
    ra_aluno_alterar = input("Digite o RA do aluno a ser alterado: ")

    # Consulta os dados do aluno pelo RA fornecido
    cursor.execute("SELECT * FROM alunos WHERE ra=?", (ra_aluno_alterar,))
    aluno_alterar = cursor.fetchone()

    # Verifica se o aluno foi encontrado
    if aluno_alterar:
        print(f"\nDados atuais do aluno {aluno_alterar[1]} (RA: {aluno_alterar[6]}):")
        print(f"1. Nome: {aluno_alterar[1]}")
        print(f"2. Idade: {aluno_alterar[2]}")
        print(f"3. Cidade de Nascimento: {aluno_alterar[3]}")
        print(f"4. UF: {aluno_alterar[7]}")
        print(f"5. Estrangeiro: {aluno_alterar[8]}")

        try:
            # Solicita o número do campo a ser alterado
            numero_campo = int(input("\nDigite o número do campo a ser alterado (1-5) ou 0 para cancelar: "))

            # Verifica se o número do campo é 0; se sim, cancela a alteração e encerra a função.
            if numero_campo == 0:
                print("\nAlteração cancelada.")
                return

            # Verifica se o número do campo está no intervalo de 1 a 5.
            if 1 <= numero_campo <= 5:
                novo_valor = None

                # Determina qual campo está sendo alterado e solicita a entrada do usuário com base nesse campo.
                if numero_campo == 1:
                    novo_valor = validar_texto("Novo nome do aluno: ")
                elif numero_campo == 2:
                    novo_valor = validar_idade("Nova idade do aluno: ")
                elif numero_campo == 3:
                    novo_valor = validar_texto("Nova cidade de nascimento do aluno: ")
                elif numero_campo == 4:
                    # Para a UF, solicita a entrada do usuário e valida se a UF tem exatamente 2 caracteres.
                    novo_valor = validar_uf("Nova UF do aluno (2 letras maiúsculas). Estrangeiro colocar NA (Não Aplicável): ")
                    while len(novo_valor) != 2:
                        print("Erro de digitação. A UF deve conter exatamente 2 caracteres.")
                        novo_valor = input("Nova UF do aluno (2 caracteres): ").upper()
                elif numero_campo == 5:
                    # Para a resposta sobre ser estrangeiro, solicita a entrada do usuário e valida se a resposta é 'S' ou 'N'.
                    novo_valor = input("O aluno é estrangeiro? (S/N): ").upper()
                    while novo_valor not in ['S', 'N']:
                        print("Erro de digitação. Responda com 'S' para Sim ou 'N' para Não.")
                        novo_valor = input("O aluno é estrangeiro? (S/N): ").upper()

                # Pede confirmação ao usuário antes de alterar
                confirmacao = input(f"\nTem certeza que deseja alterar o campo {numero_campo} para '{novo_valor}'? (S/N): ").upper()

                if confirmacao == 'S':
                    # Atualiza o campo na tabela 'alunos'
                    coluna_alterar = None

                    # Indica qual número representa a qual campo da tabela
                    if numero_campo == 1:
                        coluna_alterar = "nome"
                    elif numero_campo == 2:
                        coluna_alterar = "idade"
                    elif numero_campo == 3:
                        coluna_alterar = "cidade_nascimento"
                    elif numero_campo == 4:
                        coluna_alterar = "uf"
                    elif numero_campo == 5:
                        coluna_alterar = "estrangeiro"

                    # Executa uma instrução SQL de UPDATE no banco de dados para alterar um valor específico em uma coluna da tabela "alunos".
                    cursor.execute(f"UPDATE alunos SET {coluna_alterar}=? WHERE ra=?", (novo_valor, ra_aluno_alterar))
                    # Confirma as alterações no banco de dados.
                    conexao.commit()
                    print("\nAlteração realizada com sucesso.")
                else:
                    print("\nAlteração cancelada.")
            else:
                print("\nOpção inválida. Tente novamente.")

        # Trata exceções do tipo ValueError que podem ocorrer durante a execução do bloco "try".
        except ValueError:
            print("\nPor favor, insira um número válido.")

    else:
        print("\nAluno não encontrado.\n")

# Função para listar alunos por série e sala
def listar_alunos():
    print("\n== Listar Alunos por Série e Sala ==\n")

    # Consulta todos os alunos ordenados por série e sala
    cursor.execute("SELECT * FROM alunos ORDER BY serie, sala")
    resultados = cursor.fetchall()

    # Verifica se há alunos cadastrados
    if not resultados:
        # Informa ao usuário que não há alunos cadastrados
        print("Não consta nenhum aluno cadastrado no sistema.")
    else:
        # Exibe a lista de alunos
        for aluno in resultados:
            print(f"{aluno[4]} Série, Sala {aluno[5]} - {aluno[1]} (RA: {aluno[6]})")

# Função principal
def main():
    while True:
        print("\nBem-vindo ao Sistema da Escola de Ensino Médio!\n")

        try:
            # Solicita a opção do usuário e converte para inteiro
            opcao = int(input(
                "[1] Cadastrar Novo Aluno\n"
                "[2] Remover Aluno\n"
                "[3] Listar Alunos por Série e Sala\n"
                "[4] Alterar Cadastro do Aluno\n"
                "[0] Sair\n"
                "Escolha sua opção: "
            ))

            # Indica qual número representa a opção que o usuário vai escolher
            if opcao == 1:
                cadastrar_aluno()
            elif opcao == 2:
                remover_aluno()
            elif opcao == 3:
                listar_alunos()
            elif opcao == 4:
                alterar_cadastro_aluno()
            elif opcao == 0:
                print("\nObrigado por utilizar o Sistema da Escola de Ensino Médio. Até mais!\n")
                break
            else:
                print("\nOpção inválida. Tente novamente.\n")

        except ValueError:
            # Trata exceção se o usuário inserir algo que não é um número
            print("\nPor favor, insira um número válido.\n")

if __name__ == "__main__":
    main()

# Fecha a conexão com o banco de dados ao sair do programa
conexao.close()
