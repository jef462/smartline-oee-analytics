import sqlite3
import pandas as pd

conn = sqlite3.connect('sql/smartline_dw.db')
df = pd.read_sql_query("""
    SELECT f.*, e.estacao, t.turno 
    FROM fato_producao f
    JOIN dim_estacao e ON f.id_estacao = e.id_estacao
    JOIN dim_turno t ON f.id_turno = t.id_turno
""", conn)

# Cenário Atual
custo_atual = df['custo_parada_brl'].sum()
min_parados_atual = df['minutos_parados'].sum()

# Cenário Proposto:
# 1) Manutenção preditiva nos sensores/torque da EST-03_Powertrain (-40% nas paradas dessa estação)
# 2) Kanban eletrônico / abastecimento preventivo no 2º Turno (-50% nas paradas por Falta de Peça no 2º Turno)
df['custo_simulado'] = df['custo_parada_brl']

mask_est03 = df['estacao'] == 'EST-03_Powertrain'
df.loc[mask_est03, 'custo_simulado'] *= 0.60

mask_logistica_t2 = (df['motivo_parada'] == 'Falta de Peça (Logística)') & (df['turno'].str.contains('2º Turno'))
df.loc[mask_logistica_t2, 'custo_simulado'] *= 0.50

custo_novo = df['custo_simulado'].sum()
economia_trimestre = custo_atual - custo_novo
economia_anualizada = economia_trimestre * 4

print("=== SIMULAÇÃO DE IMPACTO OPERACIONAL & FINANCEIRO (90 DIAS) ===")
print(f"Custo Atual de Paradas (Trimestre):    R$ {custo_atual:,.2f}")
print(f"Custo Projetado após Melhorias:        R$ {custo_novo:,.2f}")
print(f"ECONOMIA DIRETA NO TRIMESTRE:          R$ {economia_trimestre:,.2f}")
print(f"PROJEÇÃO DE ECONOMIA ANUAL:            R$ {economia_anualizada:,.2f}")

conn.close()