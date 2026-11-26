import sqlite3
import pandas as pd

conn = sqlite3.connect('sql/smartline_dw.db')

# 1. Cálculo Corrigido de OEE e Prejuízo por Estação
q1_oee_estacao = """
WITH metricas_base AS (
    SELECT 
        e.estacao,
        e.area_responsavel,
        COUNT(*) AS total_ciclos,
        SUM(f.tempo_ciclo_real_seg) / 60.0 AS min_operando,
        SUM(f.minutos_parados) AS min_parados,
        AVG(f.tempo_ciclo_padrao_seg) / AVG(f.tempo_ciclo_real_seg) AS performance,
        AVG(f.peca_aprovada) AS qualidade,
        SUM(f.custo_parada_brl) AS prejuizo_brl
    FROM fato_producao f
    JOIN dim_estacao e ON f.id_estacao = e.id_estacao
    GROUP BY e.estacao, e.area_responsavel
),
calculo_oee AS (
    SELECT 
        estacao,
        area_responsavel,
        total_ciclos,
        ROUND((min_operando / (min_operando + min_parados)) * 100, 2) AS disponibilidade_pct,
        ROUND(performance * 100, 2) AS performance_pct,
        ROUND(qualidade * 100, 2) AS qualidade_pct,
        ROUND(((min_operando / (min_operando + min_parados)) * performance * qualidade) * 100, 2) AS oee_pct,
        ROUND(prejuizo_brl, 2) AS prejuizo_brl
    FROM metricas_base
)
SELECT 
    RANK() OVER (ORDER BY oee_pct ASC) AS rank_gargalo,
    estacao,
    disponibilidade_pct,
    performance_pct,
    qualidade_pct,
    oee_pct,
    prejuizo_brl,
    ROUND(prejuizo_brl * 100.0 / SUM(prejuizo_brl) OVER(), 2) AS pct_prejuizo_total
FROM calculo_oee
ORDER BY rank_gargalo;
"""
print("--- 1. RANKING DE OEE REAL E PREJUÍZO POR ESTAÇÃO ---")
print(pd.read_sql_query(q1_oee_estacao, conn).to_string(index=False))

conn.close()