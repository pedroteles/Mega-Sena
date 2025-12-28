import pandas as pd
import secrets
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RangeSlider, TextBox
import matplotlib.cm as cm
from concurrent.futures import ProcessPoolExecutor
import time
import os
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from datetime import datetime

# Definição do total de jogos (Total de combinações da Mega-Sena)
TOTAL_JOGOS = 1_000_000
# TOTAL_JOGOS = 50_063_860  # Para todas as combinações possíveis (60 choose 6)

# Configuração de exibição: 'both', 'freq' (apenas dezenas), 'soma' (apenas somas)
SHOW_GRAPHS = 'soma'

def simular_lote_jogos(qtd_jogos):
    """
    Função worker que retorna os jogos completos, não apenas as somas.
    """
    rng = secrets.SystemRandom()
    
    jogos_gerados = []
    range_dezenas = range(1, 61)
    
    for _ in range(qtd_jogos):
        jogo = rng.sample(range_dezenas, 6)
        jogos_gerados.append(jogo)
        
    return jogos_gerados

def carregar_historico():
    try:
        # Lê o CSV com separador ponto e vírgula
        arquivo = './data/megasena_full_history.csv'
        if not os.path.exists(arquivo):
            arquivo = '../data/megasena_full_history.csv'
            
        df = pd.read_csv(arquivo, sep=';')
        
        # Renomeia coluna para padrão interno se necessário
        if 'Data do Sorteio' in df.columns:
            df.rename(columns={'Data do Sorteio': 'Data Sorteio'}, inplace=True)
            
        # Converte a coluna de data e remove linhas com datas inválidas
        df['Data Sorteio'] = pd.to_datetime(df['Data Sorteio'], dayfirst=True, errors='coerce')
        df.dropna(subset=["Data Sorteio"], inplace=True)
        return df
    except Exception as e:
        print(f"Aviso: Não foi possível carregar o histórico ({e}).")
        return pd.DataFrame()

def main():
    print(f"Iniciando simulação conjunta de {TOTAL_JOGOS:,} jogos...")
    
    # Detecta o número de CPUs lógicas disponíveis
    num_processos = os.cpu_count() or 4
    print(f"Utilizando {num_processos} núcleos de processamento.")
    
    # Divide o trabalho em fatias para cada núcleo
    tamanho_lote = TOTAL_JOGOS // num_processos
    lotes = [tamanho_lote] * num_processos
    
    # Adiciona o resto da divisão ao último lote para garantir o total exato
    lotes[-1] += TOTAL_JOGOS % num_processos
    
    inicio = time.time()
    
    # Lista para agregar todos os jogos na ordem correta
    todos_jogos_lista = []
    
    # Inicia o multiprocessamento
    with ProcessPoolExecutor(max_workers=num_processos) as executor:
        # Mapeia a execução e recupera os resultados
        # O map garante que os resultados venham na ordem dos lotes
        resultados = executor.map(simular_lote_jogos, lotes)
        
        # Agrega os resultados conforme eles ficam prontos
        for i, resultado_parcial in enumerate(resultados):
            todos_jogos_lista.extend(resultado_parcial)
            print(f"Lote {i+1}/{num_processos} processado.")

    # Converte para array numpy para alta performance e economia de memória
    # int16 é suficiente (números até 60)
    arr_jogos = np.array(todos_jogos_lista, dtype=np.int16)
    arr_somas = np.sum(arr_jogos, axis=1)
    
    tempo_total = time.time() - inicio
    print(f"\nSimulação concluída em {tempo_total:.2f} segundos.")

    # --- Carrega e Prepara Dados Históricos ---
    df_historico = carregar_historico()
    
    # Arrays completos que serão filtrados dinamicamente
    dados_historico_full = np.empty((0, 6), dtype=int)
    somas_historico_full = np.array([], dtype=int)
    datas_historico_full = np.array([], dtype='datetime64[ns]')

    if not df_historico.empty:
        cols_bolas = [f'Bola{i}' for i in range(1, 7)]
        dados_historico_full = df_historico[cols_bolas].values.astype(int)
        somas_historico_full = np.sum(dados_historico_full, axis=1)
        datas_historico_full = df_historico['Data Sorteio'].values
        
        data_min_hist = df_historico['Data Sorteio'].min().to_pydatetime()
        data_max_hist = df_historico['Data Sorteio'].max().to_pydatetime()
    else:
        # Define um padrão caso o histórico não seja carregado
        print("AVISO: Histórico não carregado. Usando intervalo de datas padrão.")
        data_max_hist = datetime.now()
        data_min_hist = datetime(1996, 3, 11) # Data do primeiro concurso

    # --- Cálculos Estatísticos Globais ---
    
    media = np.mean(arr_somas)
    desvio_padrao = np.std(arr_somas)

    print("-" * 30)
    print(f"RESULTADOS ESTATÍSTICOS DA SOMA:")
    print(f"Total de Jogos: {len(arr_somas):,}")
    print(f"Média das Somas: {media:.4f} (Teórica: 183.0)")
    print(f"Desvio Padrão: {desvio_padrao:.4f}")
    print("-" * 30)

    # --- Plotagem do Gráfico ---
    print("Gerando gráfico interativo...")

    if SHOW_GRAPHS == 'freq':
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 7))
        ax2 = None
    elif SHOW_GRAPHS == 'soma':
        fig, ax2 = plt.subplots(1, 1, figsize=(12, 7))
        ax1 = None
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
    plt.subplots_adjust(bottom=0.3) # Espaço para os widgets
    
    # Referências para interatividade
    plot_refs = {'bars1': None, 'bars2': None, 'annot1': None, 'annot2': None}
    current_stats = {'total_jogos': 0}

    def update_plot(start_date, end_date, num_simulacoes):
        num_simulacoes = int(num_simulacoes)
        # Filtra dados históricos pelo range de data
        mask_hist = (datas_historico_full >= np.datetime64(start_date)) & (datas_historico_full <= np.datetime64(end_date))
        dados_historico_filtrado = dados_historico_full[mask_hist]
        somas_historico_filtrado = somas_historico_full[mask_hist]

        if dados_historico_filtrado.size > 0:
            numeros_historico_filtrado = dados_historico_filtrado.flatten()
            contagem_historico = np.bincount(numeros_historico_filtrado, minlength=61)[1:]
            total_historico = len(dados_historico_filtrado)
            contagem_somas_historico = np.bincount(somas_historico_filtrado, minlength=350)
        else:
            contagem_historico = np.zeros(60, dtype=int)
            total_historico = 0
            contagem_somas_historico = np.zeros(350, dtype=int)

        fig.suptitle(f"Histórico ({total_historico:,} jogos de {start_date.strftime('%d/%m/%y')} a {end_date.strftime('%d/%m/%y')}) + {num_simulacoes:,} Simulações", fontsize=12)
        if ax1:
            ax1.clear()
        if ax2:
            ax2.clear()

        # Filtra os arrays pelo intervalo de IDs dos jogos
        subset_jogos = arr_jogos[:num_simulacoes]
        subset_somas = arr_somas[:num_simulacoes]
        current_stats['total_jogos'] = len(subset_jogos) + total_historico
        
        if current_stats['total_jogos'] == 0:
            if ax1:
                ax1.text(0.5, 0.5, "Nenhum jogo selecionado", ha='center')
            if ax2:
                ax2.text(0.5, 0.5, "Nenhum jogo selecionado", ha='center')
            plot_refs['bars1'] = None
            plot_refs['bars2'] = None
            return

        # --- GRÁFICO 1: Frequência das Dezenas ---
        # Flatten para contar todas as dezenas sorteadas no lote
        if ax1:
            contagem_simulacao = np.bincount(subset_jogos.flatten(), minlength=61)[1:]
            current_stats['contagem_dezenas_total'] = contagem_historico + contagem_simulacao
            x_dezenas = np.arange(1, 61)
            
            bars1 = ax1.bar(x_dezenas, contagem_historico, color='steelblue', alpha=0.7, label='Histórico')
            bars2 = ax1.bar(x_dezenas, contagem_simulacao, bottom=contagem_historico, color='purple', alpha=0.7, label='Simulação')
            plot_refs['bars1'] = list(bars1) + list(bars2)
            ax1.set_title(f'Frequência das Dezenas (Histórico + Simulação)')
            ax1.set_xlabel('Dezena (1-60)')
            ax1.set_ylabel('Frequência Absoluta')
            ax1.set_xticks(range(0, 61, 5))
            ax1.grid(axis='y', alpha=0.3)

            # Calcula e plota a média de frequência
            total_ocorrencias = contagem_historico.sum() + contagem_simulacao.sum()
            media_freq_abs = total_ocorrencias / 60
            ax1.axhline(media_freq_abs, color='red', linestyle='--', linewidth=1.5)
            ax1.legend()

        # --- GRÁFICO 2: Distribuição das Somas ---
        if ax2:
            contagem_somas_simulacao = np.bincount(subset_somas, minlength=len(contagem_somas_historico))
            
            # Garante que os arrays tenham o mesmo tamanho
            if len(contagem_somas_simulacao) > len(contagem_somas_historico):
                 contagem_somas_historico_plot = np.pad(contagem_somas_historico, (0, len(contagem_somas_simulacao) - len(contagem_somas_historico)))
                 contagem_somas_simulacao_plot = contagem_somas_simulacao
            else:
                 contagem_somas_historico_plot = contagem_somas_historico
                 contagem_somas_simulacao_plot = np.pad(contagem_somas_simulacao, (0, len(contagem_somas_historico) - len(contagem_somas_simulacao)))

            # Filtra apenas índices com dados para plotagem mais limpa
            total_counts = contagem_somas_historico_plot + contagem_somas_simulacao_plot
            valid_indices = np.nonzero(total_counts)[0]
            
            bars2_hist = ax2.bar(valid_indices, contagem_somas_historico_plot[valid_indices], color='steelblue', alpha=0.7, label='Histórico')
            bars2_sim = ax2.bar(valid_indices, contagem_somas_simulacao_plot[valid_indices], bottom=contagem_somas_historico_plot[valid_indices], color='purple', alpha=0.7, label='Simulação')
            plot_refs['bars2'] = list(bars2_hist) + list(bars2_sim)
            
            ax2.set_title(f'Distribuição da Soma (Histórico + Simulação)')
            ax2.set_xlabel('Soma das 6 Dezenas')
            ax2.set_ylabel('Frequência')
            ax2.grid(axis='y', linestyle='--', alpha=0.5)

            # Calcula e plota a média da soma para o conjunto de dados filtrado
            somas_combinadas = np.concatenate((somas_historico_filtrado, subset_somas))
            if somas_combinadas.size > 0:
                media_atual_somas = np.mean(somas_combinadas)
                ax2.axvline(media_atual_somas, color='red', linestyle='dashed', linewidth=1.5, label=f'Média: {media_atual_somas:.2f}')
            ax2.legend()

        # Configura o tooltip (invisível inicialmente)
        if ax1:
            annot1 = ax1.annotate("", xy=(0,0), xytext=(0,10), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9),
                                ha='center')
            annot1.set_visible(False)
            plot_refs['annot1'] = annot1
        
        if ax2:
            annot2 = ax2.annotate("", xy=(0,0), xytext=(0,10), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9),
                                ha='center')
            annot2.set_visible(False)
            plot_refs['annot2'] = annot2

    def hover(event):
        # Verifica em qual eixo o mouse está
        if ax1 and event.inaxes == ax1 and plot_refs['bars1']:
            annot = plot_refs['annot1']
            bars = plot_refs['bars1']
            label_prefix = "Dezena"
        elif ax2 and event.inaxes == ax2 and plot_refs['bars2']:
            annot = plot_refs['annot2']
            bars = plot_refs['bars2']
            label_prefix = "Soma"
        else:
            return
            
        if annot:
            vis = annot.get_visible()
            for bar in bars:
                if bar.contains(event)[0]:
                    x_pos = bar.get_x() + bar.get_width() / 2
                    y_pos = bar.get_y() + bar.get_height()
                    segment_height = bar.get_height()
                    annot.xy = (x_pos, y_pos)
                    
                    if label_prefix == "Dezena":
                        dezena = int(round(x_pos))
                        idx = dezena - 1
                        if 'contagem_dezenas_total' in current_stats and 0 <= idx < 60:
                            total = current_stats['contagem_dezenas_total'][idx]
                            freq_rel = (total / current_stats['total_jogos']) * 100 if current_stats['total_jogos'] > 0 else 0
                            annot.set_text(f"{label_prefix}: {dezena}\nTotal: {int(total)}\nRel: {freq_rel:.2f}%")
                    else:
                        annot.set_text(f"{label_prefix}: {int(x_pos)}\nFreq: {int(segment_height)}")

                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)
    
    # --- Widgets ---
    # Slider para Simulações
    ax_slider_sim = plt.axes([0.15, 0.15, 0.7, 0.03])
    slider_sim = Slider(
        ax=ax_slider_sim,
        label="Número de Simulações",
        valmin=0,
        valmax=TOTAL_JOGOS,
        valinit=TOTAL_JOGOS,
        valstep=1
    )

    # Slider para o Período Histórico
    d_min_num = mdates.date2num(data_min_hist)
    d_max_num = mdates.date2num(data_max_hist)
    ax_slider_date = plt.axes([0.15, 0.08, 0.7, 0.03])
    slider_date = RangeSlider(ax_slider_date, "Período Histórico", d_min_num, d_max_num, valinit=(d_min_num, d_max_num))

    # Caixas de texto para data
    ax_box_start = plt.axes([0.25, 0.02, 0.15, 0.04])
    text_box_start = TextBox(ax_box_start, 'Início:', initial=data_min_hist.strftime('%d/%m/%Y'))
    ax_box_end = plt.axes([0.60, 0.02, 0.15, 0.04])
    text_box_end = TextBox(ax_box_end, 'Fim:', initial=data_max_hist.strftime('%d/%m/%Y'))

    def update_all(event=None):
        num_sim = slider_sim.val
        date_range = slider_date.val
        start_date = mdates.num2date(date_range[0]).replace(tzinfo=None)
        end_date = mdates.num2date(date_range[1]).replace(tzinfo=None)
        
        text_box_start.set_val(start_date.strftime('%d/%m/%Y'))
        text_box_end.set_val(end_date.strftime('%d/%m/%Y'))

        update_plot(start_date, end_date, num_sim)
        fig.canvas.draw_idle()

    def submit_text(text):
        try:
            start_dt = datetime.strptime(text_box_start.text, '%d/%m/%Y')
            end_dt = datetime.strptime(text_box_end.text, '%d/%m/%Y')
            slider_date.set_val((mdates.date2num(start_dt), mdates.date2num(end_dt)))
            update_all()
        except ValueError:
            print("Formato de data inválido. Use DD/MM/AAAA.")
            update_all() # Reseta para o valor do slider

    slider_sim.on_changed(update_all)
    slider_date.on_changed(update_all)
    text_box_start.on_submit(submit_text)
    text_box_end.on_submit(submit_text)

    # Plot inicial com todos os dados
    update_all()

    plt.show()
if __name__ == '__main__':
    main()