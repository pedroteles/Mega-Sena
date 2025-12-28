import pandas as pd

# 1. Carregamento (tenta detectar separador automaticamente)
try:
    df = pd.read_csv('./data/megasena_full_history.csv', sep=';')
except:
    df = pd.read_csv('megasena_full_history.csv', sep=',')

# 2. Definição das Colunas
col_concurso = 'Concurso'
col_data = 'Data do Sorteio'
cols_bolas = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']

# Ajuste de compatibilidade caso o CSV esteja em formato snake_case (gerado pelo get_resultados.py)
if col_concurso not in df.columns:
    df.rename(columns={'concurso': col_concurso}, inplace=True)
if col_data not in df.columns:
    df.rename(columns={'data_do_sorteio': col_data}, inplace=True)
    for i, bola in enumerate(cols_bolas, 1):
        df.rename(columns={f'bola{i}': bola}, inplace=True)

if col_data not in df.columns:
    raise ValueError(f"Coluna '{col_data}' não encontrada. Verifique o CSV.")

# 3. Tratamento de Datas
df['Data_Ref'] = pd.to_datetime(df[col_data], format='%d/%m/%Y', errors='coerce')
df = df.dropna(subset=['Data_Ref'])

# 4. Transformação (Wide -> Long)
# Transforma as 6 colunas de bolas em 1 única coluna 'Dezena'
df_long = df.melt(id_vars=['Data_Ref', col_concurso], value_vars=cols_bolas, value_name='Dezena')
df_long = df_long.dropna(subset=['Dezena'])
df_long['Dezena'] = df_long['Dezena'].astype(int)

# 5. Ordenação Crítica (Fundamental para o diff funcionar)
df_long = df_long.sort_values(['Dezena', 'Data_Ref'])

# 6. Cálculo do Delta (Data Y - Data X)
# O shift(1) pega a data do sorteio anterior DA MESMA DEZENA
df_long['Data_Anterior'] = df_long.groupby('Dezena')['Data_Ref'].shift(1)
df_long['Intervalo_Dias'] = (df_long['Data_Ref'] - df_long['Data_Anterior']).dt.days

# 7. Extração do Recorde Absoluto
idx_max = df_long['Intervalo_Dias'].idxmax()
recorde = df_long.loc[idx_max]

print("-" * 30)
print(f"MAIOR INTERVALO ENCONTRADO:")
print(f"Dezena (Z): {recorde['Dezena']}")
print(f"Data X (Última aparição): {recorde['Data_Anterior'].strftime('%d/%m/%Y')}")
print(f"Data Y (Reaparecimento): {recorde['Data_Ref'].strftime('%d/%m/%Y')}")
print(f"Dias sem sair: {int(recorde['Intervalo_Dias'])}")
print("-" * 30)

# 8. Cálculo de Sequências Consecutivas (Recorde de Aparição)
# Ordena por Dezena e Concurso para verificar a continuidade numérica
df_long = df_long.sort_values(['Dezena', col_concurso])

# Calcula a diferença entre o concurso atual e o anterior para a mesma dezena
# Se a diferença for 1, significa que são concursos seguidos.
df_long['Diff_Concurso'] = df_long.groupby('Dezena')[col_concurso].diff()

# Cria um ID de grupo: incrementa sempre que a diferença não for 1 (quebra da sequência)
# Isso agrupa as sequências consecutivas com um mesmo ID único
df_long['Grupo_Seq'] = (df_long['Diff_Concurso'] != 1).cumsum()

# Conta o tamanho de cada grupo e pega o maior
stats_seq = df_long.groupby(['Dezena', 'Grupo_Seq'])[col_concurso].count().reset_index(name='Qtd_Seguida')
max_seq = stats_seq['Qtd_Seguida'].max()

# Filtra todos os registros que atingiram esse máximo (tratamento de empate)
recordes_seq = stats_seq[stats_seq['Qtd_Seguida'] == max_seq]

print(f"MAIOR SEQUÊNCIA DE SORTEIOS CONSECUTIVOS (Recorde: {max_seq} vezes):")

for _, row in recordes_seq.iterrows():
    dezena = row['Dezena']
    grupo = row['Grupo_Seq']
    
    # Recupera os números dos concursos que compõem essa sequência
    mask_seq = (df_long['Dezena'] == dezena) & (df_long['Grupo_Seq'] == grupo)
    concursos_seq = df_long.loc[mask_seq, col_concurso].tolist()
    
    print(f"- Dezena: {dezena}")
    print(f"  Concursos: {', '.join(map(str, concursos_seq))}")

print("-" * 30)

# 9. Cálculo do Atraso Atual (Qual dezena está há mais tempo sem sair?)
# Pega a data mais recente de todo o histórico carregado
data_ref_atual = df['Data_Ref'].max()

# Agrupa por dezena e pega a última data que ela saiu
ultimas_aparicoes = df_long.groupby('Dezena')['Data_Ref'].max().reset_index()

# Calcula a diferença em dias
ultimas_aparicoes['Dias_Sem_Sair'] = (data_ref_atual - ultimas_aparicoes['Data_Ref']).dt.days

# Ordena para pegar a maior
top_atrasada = ultimas_aparicoes.loc[ultimas_aparicoes['Dias_Sem_Sair'].idxmax()]

print(f"DEZENA MAIS ATRASADA ATUALMENTE:")
print(f"Dezena: {top_atrasada['Dezena']}")
print(f"Última vez sorteada: {top_atrasada['Data_Ref'].strftime('%d/%m/%Y')}")
print(f"Dias sem sair: {top_atrasada['Dias_Sem_Sair']} dias (em relação ao último sorteio da base: {data_ref_atual.strftime('%d/%m/%Y')})")
print("-" * 30)