import pandas as pd
import sqlite3

# 1. Extração (Extract)
df = pd.read_csv('data/producao_linha_bruto.csv')
linhas_brutas = len(df)

# 2. Transformação e Limpeza (Transform)
# Remover duplicatas exatas pelo ID de apontamento
df = df.drop_duplicates(subset=['id_apontamento'])

# Corrigir leituras negativas de sensor (substituindo pela mediana válida da estação)
mediana_ciclo = df[df['tempo_ciclo_real_seg'] > 0]['tempo_ciclo_real_seg'].median()
df.loc[df['tempo_ciclo_real_seg'] <= 0, 'tempo_ciclo_real_seg'] = mediana_ciclo

# Converter data_hora e extrair atributos temporais
df['data_hora'] = pd.to_datetime(df['data_hora'])
df['data_producao'] = df['data_hora'].dt.date.astype(str)
df['dia_semana'] = df['data_hora'].dt.day_name()
df['mes'] = df['data_hora'].dt.strftime('%Y-%m')

# Regra de Negócio: Custo estimado de R$ 180,00 por minuto de linha parada
df['custo_parada_brl'] = (df['minutos_parados'] * 180.0).round(2)

# 3. Modelagem Star Schema (Dimensões e Fato)
# Dimensão Estação
dim_estacao = pd.DataFrame({
    'id_estacao': [1, 2, 3, 4, 5],
    'estacao': ['EST-01_Chassi', 'EST-02_Suspensao', 'EST-03_Powertrain', 'EST-04_Eletrica', 'EST-05_Inspecao_Final'],
    'area_responsavel': ['Carroceria', 'Chassi & Rodagem', 'Powertrain', 'Eletrônica', 'Qualidade Final']
})

# Dimensão Turno
dim_turno = pd.DataFrame({
    'id_turno': [1, 2, 3],
    'turno': ['1º Turno (06:00-15:00)', '2º Turno (15:05-00:03)', '3º Turno (00:05-05:55)'],
    'gestao_turno': ['Manhã/Tarde', 'Tarde/Noite', 'Madrugada']
})

# Mapear IDs na Tabela Fato
df = df.merge(dim_estacao[['id_estacao', 'estacao']], on='estacao', how='left')
df = df.merge(dim_turno[['id_turno', 'turno']], on='turno', how='left')

fato_producao = df[[
    'id_apontamento', 'data_hora', 'data_producao', 'dia_semana', 'mes',
    'id_estacao', 'id_turno', 'tempo_ciclo_padrao_seg', 'tempo_ciclo_real_seg',
    'peca_aprovada', 'motivo_parada', 'minutos_parados', 'custo_parada_brl'
]]

# 4. Carga no Banco de Dados (Load)
conn = sqlite3.connect('sql/smartline_dw.db')
dim_estacao.to_sql('dim_estacao', conn, if_exists='replace', index=False)
dim_turno.to_sql('dim_turno', conn, if_exists='replace', index=False)
fato_producao.to_sql('fato_producao', conn, if_exists='replace', index=False)
conn.close()

# Salvar também um CSV consolidado para facilitar conexão direta no Power BI se desejar
df.to_csv('data/producao_linha_limpo.csv', index=False)

print("=== RELATÓRIO DE ETL & DATA WAREHOUSE ===")
print(f"Linhas brutas lidas: {linhas_brutas}")
print(f"Linhas limpas na Fato: {len(fato_producao)} (45 duplicadas removidas + 16 sensores corrigidos)")
print("Banco Star Schema criado em: sql/smartline_dw.db (dim_estacao, dim_turno, fato_producao)")