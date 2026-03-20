import os
import time
import random
import string

# ===============================
# Consolidação dos resultados
# ===============================
def consolidar_resultados(resultados):
    total_linhas = 0
    total_palavras = 0
    total_caracteres = 0

    contagem_global = {
        "erro": 0,
        "warning": 0,
        "info": 0
    }

    for r in resultados:
        total_linhas += r["linhas"]
        total_palavras += r["palavras"]
        total_caracteres += r["caracteres"]

        for chave in contagem_global:
            contagem_global[chave] += r["contagem"][chave]

    return {
        "linhas": total_linhas,
        "palavras": total_palavras,
        "caracteres": total_caracteres,
        "contagem": contagem_global
    }


# ===============================
# Processamento de arquivo
# ===============================
def processar_arquivo(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.readlines()

    total_linhas = len(conteudo)
    total_palavras = 0
    total_caracteres = 0

    contagem = {
        "erro": 0,
        "warning": 0,
        "info": 0
    }

    for linha in conteudo:
        palavras = linha.split()

        total_palavras += len(palavras)
        total_caracteres += len(linha)

        for p in palavras:
            if p in contagem:
                contagem[p] += 1

        
        for _ in range(1000):
            pass

    return {
        "linhas": total_linhas,
        "palavras": total_palavras,
        "caracteres": total_caracteres,
        "contagem": contagem
    }


# ===============================
# Função do Trabalhador
# ===============================
def consumidor_worker(fila_tarefas, fila_resultados):
    """Pega os arquivos da fila, processa e guarda o resultado."""
    while True:
        caminho = fila_tarefas.get()
        if caminho is None: 
            break
        resultado = processar_arquivo(caminho)
        fila_resultados.put(resultado)


# ===============================
# Execução
# =========================================================
def executar_serial(pasta):
    resultados = []

    inicio = time.time()


    import multiprocessing as mp
    
    num_processos = 12  # 2, 4, 8 ou 12 
    
    
    fila_tarefas = mp.Queue(maxsize=50) 
    fila_resultados = mp.Queue()
    
    
    consumidores = []
    for _ in range(num_processos):
        p = mp.Process(target=consumidor_worker, args=(fila_tarefas, fila_resultados))
        p.start()
        consumidores.append(p)
        
    
    arquivos = os.listdir(pasta)
    for arquivo in arquivos:
        caminho = os.path.join(pasta, arquivo)
        fila_tarefas.put(caminho) 
        
    
    for _ in range(num_processos):
        fila_tarefas.put(None)
        
    
    for _ in arquivos:
        resultados.append(fila_resultados.get())
        
    
    for p in consumidores:
        p.join()
 

    fim = time.time()

    resumo = consolidar_resultados(resultados)

    print("\n=== EXECUÇÃO PARALELA ===")
    print(f"Arquivos processados: {len(resultados)}")
    print(f"Tempo total: {fim - inicio:.4f} segundos")

    print("\n=== RESULTADO CONSOLIDADO ===")
    print(f"Total de linhas: {resumo['linhas']}")
    print(f"Total de palavras: {resumo['palavras']}")
    print(f"Total de caracteres: {resumo['caracteres']}")

    print("\nContagem de palavras-chave:")
    for k, v in resumo["contagem"].items():
        print(f"  {k}: {v}")

    return resumo


# ===============================
# Main
# ===============================
if __name__ == "__main__":
     
    
    pasta = "log2" 

    print("Iniciando o programa...")
    executar_serial(pasta)
