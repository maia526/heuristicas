#!/usr/bin/env python3
"""
      Heuristic Optimization     
              2016               
       Template exercise 1       
       Set Covering Problem      
                                 
*************************************
 For this code:                  
   rows = elements               
   cols = subsets                
*************************************

 Code implemented for Heuristics optimization class by:  
 <add_your_name_here>                                   

 Note: Remember to keep your code in order and properly commented. 
"""

import sys
import random
import math
import time
import os
from pathlib import Path

# Algorithm parameters
seed = 1234567
scp_file = ""
output_file = "output.txt"

# Variables to activate algorithms
ch1 = 0
ch2 = 0
bi = 0
fi = 0
re = 0

# Instance static variables
m = 0            # number of rows
n = 0            # number of columns
row = []         # row[i] rows that are covered by column i
col = []         # col[i] columns that cover row i
ncol = []        # ncol[i] number of columns that cover row i
nrow = []        # nrow[i] number of rows that are covered by column i
cost = []        # cost[i] cost of column i

# Solution variables
x = []           # x[i] 0,1 if column i is selected
y = []           # y[i] 0,1 if row i covered by the actual solution
# Note: Use incremental updates for the solution
fx = 0           # sum of the cost of the columns selected in the solution (can be partial)

# Dynamic variables
# Note: use dynamic variables to make easier the construction and modification of solutions.
#       these are just examples of useful variables.
#       these variables need to be updated every time a column is added to a partial solution
#       or when a complete solution is modified
col_cover = []   # col_cover[i] selected columns that cover row i
ncol_cover = 0   # number of selected columns that cover row i

# Result aggregation
results = []


def error_reading_file(text):
    """Print error message and exit."""
    print(text)
    sys.exit(1)


def usage():
    """Print usage information."""
    print("\nUSAGE: lsscp.py [param_name param_value] [options]...")
    print("Parameters:")
    print("  --seed : seed to initialize random number generator")
    print("  --instance: SCP instance to execute.")
    print("  --output: Filename for output results.")
    print("Options:")
    print("  --ch1: random solution construction")
    print("  --ch2: static cost-based greedy values.")
    print("  --re: applies redundancy elimination after construction.")
    print("  --bi: best improvement.")
    print("\n")


def read_parameters(argv):
    """Read parameters from command line."""
    global seed, scp_file, output_file, ch1, ch2, bi, fi, re
    
    if len(argv) <= 1:
        usage()
        sys.exit(1)
    
    i = 1
    while i < len(argv):
        if argv[i] == "--seed":
            if i + 1 >= len(argv):
                print("ERROR: --seed requires a value.")
                usage()
                sys.exit(1)
            seed = int(argv[i + 1])
            i += 2
        elif argv[i] == "--instance":
            if i + 1 >= len(argv):
                print("ERROR: --instance requires a value.")
                usage()
                sys.exit(1)
            scp_file = argv[i + 1]
            i += 2
        elif argv[i] == "--output":
            if i + 1 >= len(argv):
                print("ERROR: --output requires a value.")
                usage()
                sys.exit(1)
            output_file = argv[i + 1]
            i += 2
        elif argv[i] == "--ch1":
            ch1 = 1
            i += 1
        elif argv[i] == "--ch2":
            ch2 = 1
            i += 1
        elif argv[i] == "--bi":
            bi = 1
            i += 1
        elif argv[i] == "--fi":
            fi = 1
            i += 1
        elif argv[i] == "--re":
            re = 1
            i += 1
        else:
            print(f"\nERROR: parameter {argv[i]} not recognized.")
            usage()
            sys.exit(1)
    
    # --instance é opcional: se não fornecido, processa todas as instâncias na pasta data
    # if not scp_file or scp_file == "":
    #     print("Error: --instance must be provided.")
    #     usage()
    #     sys.exit(1)


def read_scp(filename):
    global m, n, row, col, ncol, nrow, cost
    
    try:
        fp = open(filename, "r")
    except IOError:
        error_reading_file("ERROR: could not open instance file.")
    
    try:
        # number of rows and columns (may be on same line or different lines)
        line = fp.readline().strip()
        if not line:
            error_reading_file("ERROR: there was an error reading instance file.")
        values = line.split()
        if len(values) < 1:
            error_reading_file("ERROR: there was an error reading instance file.")
        m = int(values[0])
        
        # number of columns (may be on same line as m or next line)
        if len(values) >= 2:
            n = int(values[1])
        else:
            line = fp.readline().strip()
            if not line:
                error_reading_file("ERROR: there was an error reading instance file.")
            values = line.split()
            if len(values) < 1:
                error_reading_file("ERROR: there was an error reading instance file.")
            n = int(values[0])
        
        # Cost of the n columns (may span multiple lines)
        cost = []
        # Cost of the n columns (may span multiple lines)
        cost_values = []
        while len(cost_values) < n:
            line = fp.readline()
            if line is None or line == "":
                error_reading_file("ERROR: unexpected EOF while reading costs.")
            
            line = line.strip()
            if line == "":
                continue  # <-- IMPORTANTE: ignora linha vazia!

            cost_values.extend(line.split())

        # agora convertem
        cost = [int(x) for x in cost_values[:n]]

        
        """ if len(cost_values) < n:
            error_reading_file("ERROR: there was an error reading instance file.")
        
        for j in range(n):
            cost.append(int(cost_values[j])) """
        
        # Info of columns that cover each row
        col = []
        ncol = []
        for i in range(m):
            line = fp.readline().strip()
            if not line:
                error_reading_file("ERROR: there was an error reading instance file.")
            values = line.split()
            if len(values) < 1:
                error_reading_file("ERROR: there was an error reading instance file.")
            ncol_i = int(values[0])
            ncol.append(ncol_i)
            
            col_i = []
            col_values = values[1:] if len(values) > 1 else []
            # Read additional lines if needed
            while len(col_values) < ncol_i:
                line = fp.readline().strip()
                if not line:
                    error_reading_file("ERROR: there was an error reading instance file.")
                col_values.extend(line.split())
            
            if len(col_values) < ncol_i:
                error_reading_file("ERROR: there was an error reading instance file.")
            
            for h in range(ncol_i):
                col_i.append(int(col_values[h]) - 1)  # Convert to 0-based indexing
            col.append(col_i)
        
        # Info of rows that are covered by each column
        # First, count how many rows each column covers
        nrow = [0] * n
        for i in range(m):
            for h in range(ncol[i]):
                nrow[col[i][h]] += 1
        
        # Now, build the row array
        row = []
        k = [0] * n
        for j in range(n):
            row.append([0] * nrow[j])
        
        for i in range(m):
            for h in range(ncol[i]):
                col_idx = col[i][h]
                row[col_idx][k[col_idx]] = i
                k[col_idx] += 1
        
        fp.close()
        
    except (ValueError, IndexError) as e:
        error_reading_file("ERROR: there was an error reading instance file.")


def print_instance(level):
    """Use level>=1 to print more info (check the correct reading)."""
    print("**********************************************")
    print(f"  SCP INSTANCE: {scp_file}")
    print(f"  PROBLEM SIZE\t m = {m}\t n = {n}")
    
    if level >= 1:
        print("  COLUMN COST:")
        for i in range(n):
            print(f"{cost[i]} ", end='')
        print("\n")
        if nrow and len(nrow) > 0:
            print(f"  NUMBER OF ROWS COVERED BY COLUMN 1 is {nrow[0]}")
            if row and len(row) > 0 and len(row[0]) > 0:
                for i in range(nrow[0]):
                    print(f"{row[0][i]} ", end='')
                print()
        if ncol and len(ncol) > 0:
            print(f"  NUMBER OF COLUMNS COVERING ROW 1 is {ncol[0]}")
            if col and len(col) > 0 and len(col[0]) > 0:
                for i in range(ncol[0]):
                    print(f"{col[0][i]} ", end='')
                print()
    
    print("**********************************************\n")


def initialize():
    """Use this function to initialize other variables of the algorithms."""
    pass


def gerarSolucaoGulosa():
    # subconjuntos: lista onde cada item é o conjunto de elementos cobertos por S_i
    # custo[i]: custo do subconjunto i
    # nElementos: tamanho do universo de elementos

    elementosCobertos = [0] * m
    solucao = [0] * len(row)

    while 0 in elementosCobertos:  # enquanto ainda existir elemento descoberto
        melhorIndice = -1
        melhorRazao = -1

        # avalia cada subconjunto
        for i in range(len(row)):

            # conta quantos elementos descobertos o subconjunto i cobre
            novos = 0
            for e in row[i]:
                if elementosCobertos[e] == 0:
                    novos += 1

            if novos == 0:
                continue  # esse subconjunto não ajuda

            razao = novos / cost[i]  # eficiência

            if razao > melhorRazao:
                melhorRazao = razao
                melhorIndice = i

        # adiciona o melhor subconjunto encontrado
        solucao[melhorIndice] = 1
        for e in row[melhorIndice]:
            elementosCobertos[e] = 1

    return solucao


def construirCoverCount(solucao):
    cover_count = [0] * m
    for i in range(len(solucao)):
        if solucao[i] == 1:
            for e in row[i]:
                cover_count[e] += 1
    return cover_count


def ehViavel(cover_count):
    # Viável se todos os elementos têm cover_count >= 1
    return all(c > 0 for c in cover_count)

def eliminarRedundancias(solucao):
    """
    Remove colunas redundantes da solução (colunas que podem ser removidas
    sem tornar a solução inviável). Retorna a solução melhorada e o custo.
    """
    sol = solucao.copy()
    cover_count = construirCoverCount(sol)
    
    # Ordena colunas por custo (menor primeiro) para tentar remover as mais caras primeiro
    colunas_selecionadas = [i for i in range(n) if sol[i] == 1]
    colunas_selecionadas.sort(key=lambda i: cost[i], reverse=True)  # Mais caras primeiro
    
    melhorou = True
    while melhorou:
        melhorou = False
        for j in colunas_selecionadas:
            if sol[j] == 0:
                continue
            # Verifica se pode remover coluna j
            pode_remover = True
            for e in row[j]:
                if cover_count[e] <= 1:
                    pode_remover = False
                    break
            
            if pode_remover:
                # Remove a coluna
                sol[j] = 0
                for e in row[j]:
                    cover_count[e] -= 1
                melhorou = True
                # Remove da lista para não tentar novamente
                colunas_selecionadas.remove(j)
                break
    
    return sol

def bestImprovement_corrigido(solucao_inicial, max_iters=10000):
    """
    Best-improvement 1-flip (iterativo + cover_count incremental).
    Retorna (solucao_final, custo_final, iters).
    solucao_inicial must be VIAVEL (cobre todas as m linhas).
    """
    # sanity
    if not any: pass

    # copia para não mudar a original fora da função
    sol = solucao_inicial.copy()

    # custo atual
    custo_atual = calcularCustoSolucao(sol)

    # construir cover_count inicial (quantas colunas selecionadas cobrem cada linha)
    cover_count = [0] * m
    for j in range(n):
        if sol[j] == 1:
            for e in row[j]:
                cover_count[e] += 1

    # verifica viabilidade
    if not ehViavel(cover_count):
        raise ValueError("A solução inicial deve ser viável!")

    iters = 0
    while iters < max_iters:
        iters += 1
        melhor_delta = 0           # queremos delta < 0 (redução do custo)
        melhor_pos = None

        # avaliar todos os vizinhos 1-flip
        for j in range(n):
            if sol[j] == 1:
                # tentativa de REMOVER coluna j -> verificar se algum elemento ficaria descoberto
                invalido = False
                for e in row[j]:
                    if cover_count[e] == 1:
                        invalido = True
                        break
                if invalido:
                    continue  # não é permitido remover, deixa inviável
                delta = -cost[j]  # custo diminuiria
            else:
                # tentativa de ADICIONAR coluna j -> sempre viável
                delta = cost[j]   # custo aumenta (geralmente > 0), logo não melhora direto

            # queremos o movimento que minimiza (custo_atual + delta); equival. ao menor delta
            if delta < melhor_delta:
                melhor_delta = delta
                melhor_pos = j

        # se não encontrou melhoria, ótimo local
        if melhor_pos is None:
            break

        # aplicar flip em melhor_pos e atualizar cover_count e custo_atual
        j = melhor_pos
        if sol[j] == 0:
            # adiciona
            sol[j] = 1
            custo_atual += cost[j]
            for e in row[j]:
                cover_count[e] += 1
        else:
            # remove
            sol[j] = 0
            custo_atual -= cost[j]
            for e in row[j]:
                cover_count[e] -= 1

        # segue para próxima iteração (best-improvement: reaplica pesquisa completa)
    return sol, custo_atual, iters



def bestImprovement(solucaoCorrente, melhorCusto, qtdSubconjuntos, cont, limite):
    #solucaoCorrente começa com uma solução gulosa válida
    """ 
    Best improvement local search para SCP.
    Em cada iteração, avalia todos os movimentos 1-flip e escolhe o melhor.
    Continua até não encontrar mais melhorias (ótimo local).
    """
    if cont == limite: 
        return melhorCusto
    
    custoCorrente = calcularCustoSolucao(solucaoCorrente)
    # Atualiza melhor custo se a solução atual for melhor
    if custoCorrente < melhorCusto:
        melhorCusto = custoCorrente
    
    print(f'Iteração {cont}: custo atual = {custoCorrente}, melhor custo global = {melhorCusto}')
    
    # Inicializa com o custo atual - queremos encontrar uma melhoria (custo menor)
    melhorCustoIteracao = custoCorrente
    melhorSolucaoIteracao = None
    melhorPos = None
    
    # Avalia todos os movimentos possíveis (só remover colunas, pois adicionar aumenta custo)
    for i in range(0, n):
        if solucaoCorrente[i] == 1:
            # Tenta REMOVER coluna i
            sAvaliado = solucaoCorrente.copy()
            sAvaliado[i] = 0
            cover_count = construirCoverCount(sAvaliado)
            if ehViavel(cover_count):
                # É viável remover - calcula novo custo
                custoAvaliado = custoCorrente - cost[i]
                # Se é melhor que o melhor encontrado até agora nesta iteração
                if custoAvaliado < melhorCustoIteracao:
                    melhorCustoIteracao = custoAvaliado
                    melhorSolucaoIteracao = sAvaliado
                    melhorPos = i
    
    # Se encontrou uma melhoria
    if melhorSolucaoIteracao is not None and melhorCustoIteracao < custoCorrente:
        # Atualiza melhor custo global
        if melhorCustoIteracao < melhorCusto:
            melhorCusto = melhorCustoIteracao
        qtdSubconjuntos = sum(1 for val in melhorSolucaoIteracao if val == 1)
        print(f'  -> Melhoria encontrada: removendo coluna {melhorPos}, novo custo = {melhorCustoIteracao}')
        # Continua a busca a partir da solução melhorada
        return bestImprovement(melhorSolucaoIteracao, melhorCusto, qtdSubconjuntos, cont+1, limite)
    else:
        # Não encontrou melhoria - ótimo local alcançado
        print(f'Ótimo local alcançado na iteração {cont} com custo {melhorCusto}')
        return melhorCusto

def calcularCustoSolucao(solucao):
    return sum(cost[i] for i in range(n) if solucao[i] == 1)

def gerarSolucaoViavelAleatoria():
    """
    m = número de elementos (1..m)
    n = número de subconjuntos (1..n)
    custo = lista de custo dos subconjuntos, tamanho n
    elementosEmSubconjuntos[e] = lista de subconjuntos que contêm o elemento e (1-based)
    """

    solucao = [0] * n                     # 0/1 para cada subconjunto
    elementoCoberto = [0] * (m)       # marca se elemento e está coberto ou não (1-based)

    # enquanto houver elemento descoberto
    while True:
        descobertos = [e for e in range(0, m) if elementoCoberto[e] == 0]
        if not descobertos:
            break  # solução viável

        # escolhemos um elemento descoberto aleatoriamente
        e = random.choice(descobertos)

        # escolhemos aleatoriamente um subconjunto que cobre e
        subconjList = col[e]
        s = random.choice(subconjList)  # subconjunto escolhido

        # ativamos esse subconjunto
        solucao[s] = 1  # pois s é 1-based

        # atualizamos quais elementos ele cobre
        # Para isso, precisamos das listas inversas:
        # subconjuntos -> elementos cobertos
        # Se você ainda não as tem, veja observação abaixo.
    
        # elementosCobertosPorSubconjunto[s] deve ser uma lista dos elementos contidos em s
        for elem in row[s]:
            elementoCoberto[elem] = 1

    return solucao

def gerarSolucaoAleatoria():
    solucaoAleatoria = [0] * n
    for i in range(0, n):
        flip = random.choice([1, 2])
        if flip == 1:
            solucaoAleatoria[i] = 1
    return solucaoAleatoria
    

def main():
    """Main function."""
    global seed, scp_file, results
    
    read_parameters(sys.argv)
    random.seed(seed)  # Set seed
    results = []
    
    # Sempre processa todos os arquivos .txt na pasta data, ignorando --instance
    # Pasta data relativa ao diretório do script
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    
    if not data_dir.exists():
        print(f"ERRO: Diretório {data_dir} não encontrado!")
        return 1
    
    # Lista todos os arquivos .txt na pasta data
    instances = sorted([f for f in os.listdir(data_dir)])
    
    if not instances:
        print(f"Nenhuma instância .txt encontrada em {data_dir}")
        return 1
    
    print(f"Processando {len(instances)} instâncias...")
    print("=" * 80)
    
    # Processa cada instância
    for instance in instances:
        scp_file = str(data_dir / instance)
        process_instance()
    
    if results:
        print("\nTabela de resultados")
        print("=" * 80)
        header = (
            f'{"Instância":<20}'
            f'{"Sol. Gulosa":>15}'
            f'{"Tempo Gulosa (s)":>20}'
            f'{"Sol. BL":>15}'
            f'{"Tempo BL (s)":>20}'
            f'{"Tempo Gulosa + BL (s)":>20}'
        )
        print(header)
        print("-" * 80)
        for row_result in results:
            print(
                f'{row_result["instancia"]:<20}'
                f'{row_result["sol_gulosa"]:>15}'
                f'{row_result["tempo_gulosa"]:>20.6f}'
                f'{row_result["sol_best"]:>15}'
                f'{row_result["tempo_best"]:>20.6f}'
                f'{row_result["tempo_total"]:>20.6f}'
            )
        print("=" * 80)
    
    return 0


def process_instance():
    """Processa uma única instância."""
    global scp_file, results
    
    try:
        read_scp(scp_file)
        # print_instance(1)  # Comentado para reduzir output
        
        if bi == 1:
            inicio_gulosa = time.perf_counter()
            x = gerarSolucaoGulosa()
            fim_gulosa = time.perf_counter()
            tempo_gulosa = fim_gulosa - inicio_gulosa
            custoSolucaoInicial = calcularCustoSolucao(x)
            qtdUns = sum(i == 1 for i in x)

            # Testa também a implementação iterativa (mais eficiente)
            
            inicio_best = time.perf_counter()
            sol_final, custo_final2, its = bestImprovement_corrigido(x, max_iters=10000)
            fim_best = time.perf_counter()
            tempo_best = fim_best - inicio_best

            tempo_total = fim_best-inicio_gulosa
            
            # Extrai apenas o nome do arquivo para a saída
            instance_name = os.path.basename(scp_file)

            results.append(
                {
                    "instancia": instance_name,
                    "sol_gulosa": custoSolucaoInicial,
                    "tempo_gulosa": tempo_gulosa,
                    "sol_best": custo_final2,
                    "tempo_best": tempo_best,
                    "tempo_total": tempo_total
                }
            )
        
        return 0
    except Exception as e:
        instance_name = os.path.basename(scp_file) if scp_file else "unknown"
        print(f'{instance_name} = ERRO: {e}')
        return 1


if __name__ == "__main__":
    sys.exit(main())

