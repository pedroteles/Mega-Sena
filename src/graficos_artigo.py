import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time

def main():
    # Configuração Estética
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (16, 20)
    
    # Cenários de Simulação (Quantidade de Jogos)
    n_simulacoes = [10000, 1000000]
    
    # Criação da Figura e Subplots (4 linhas x 2 colunas)
    fig, axes = plt.subplots(len(n_simulacoes), 2)
    
    print("Iniciando simulação... Isso pode levar alguns segundos para N=1.000.000.")

    for i, n in enumerate(n_simulacoes):
        start_time = time.time()
        
        # --- GERAÇÃO DE DADOS OTIMIZADA (VETORIZAÇÃO NUMPY) ---
        # Para simular "amostragem sem reposição" de forma performática para milhões de linhas:
        # 1. Geramos ruído aleatório para uma matriz (N, 60).
        # 2. Usamos argsort para pegar os índices dos 6 menores valores de cada linha.
        # Isso garante unicidade por linha (jogo) sem loops Python lentos.
        
        # Nota: Para N=1.000.000, isso consome cerca de ~480MB de RAM.
        # Se a memória for limitada, ideal seria processar em chunks, 
        # mas aqui priorizamos a elegância vetorial do Numpy.
        ruido = np.random.rand(n, 60)
        jogos = np.argsort(ruido, axis=1)[:, :6] + 1  # +1 para ajustar de 0-59 para 1-60
        
        # Cálculos para as Colunas
        somas = np.sum(jogos, axis=1)
        todas_dezenas = jogos.flatten()
        
        # Contagem de frequência para cada número (1 a 60)
        # bincount é extremamente rápido para contar inteiros não negativos
        contagem = np.bincount(todas_dezenas, minlength=62)[1:61]
        eixo_x_dezenas = np.arange(1, 61)
        
        # --- PLOTAGEM COLUNA 1: FREQUÊNCIA (Lei dos Grandes Números) ---
        ax_freq = axes[i, 0]
        sns.barplot(x=eixo_x_dezenas, y=contagem, ax=ax_freq, color='#3498db', edgecolor='none')
        
        # Formatação Visual Frequência
        titulo_n = f"{n:,}".replace(",", ".") # Formatação PT-BR (1.000)
        ax_freq.set_title(f"Frequência das Dezenas (N = {titulo_n} Jogos)", fontsize=12, fontweight='bold')
        ax_freq.set_ylabel("Contagem de Ocorrências")
        ax_freq.set_xlabel("Dezena (1-60)")
        
        # Ajuste dos ticks do eixo X para não ficarem ilegíveis (mostra a cada 2 ou 5 dependendo do gosto, aqui 2)
        ax_freq.set_xticks(np.arange(0, 60, 2))
        ax_freq.set_xticklabels(np.arange(1, 61, 2))
        ax_freq.tick_params(axis='x', rotation=45, labelsize=8)

        # --- PLOTAGEM COLUNA 2: SOMA (Teorema do Limite Central) ---
        ax_soma = axes[i, 1]
        sns.histplot(somas, kde=True, ax=ax_soma, color='#e67e22', bins=30, line_kws={'linewidth': 2})
        
        # Linha da Média Teórica
        media_teorica = 183
        ax_soma.axvline(media_teorica, color='red', linestyle='--', linewidth=2, label=f'Média Teórica ({media_teorica})')
        
        # Formatação Visual Soma
        ax_soma.set_title(f"Distribuição da Soma das Dezenas (N = {titulo_n})", fontsize=12, fontweight='bold')
        ax_soma.set_ylabel("Frequência / Densidade")
        ax_soma.set_xlabel("Soma das 6 Dezenas")
        ax_soma.legend(loc='upper right')

        print(f"Processado N={titulo_n} em {time.time() - start_time:.4f} segundos.")

    # Ajustes Finais de Layout
    plt.suptitle("Simulação Mega Sena: Lei dos Grandes Números e Teorema do Limite Central", fontsize=20, y=1.005)
    plt.tight_layout()
    
    # Exibir
    plt.show()

if __name__ == "__main__":
    main()