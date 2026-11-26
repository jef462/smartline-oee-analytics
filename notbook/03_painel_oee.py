import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('sql/smartline_dw.db')
plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('SmartLine Analytics — Monitoramento de OEE e Gargalos Industriais', fontsize=16, fontweight='bold', y=0.98)

# --- GRÁFICO 1: OEE (%) por Estação ---
q1 = """
SELECT 
    e.estacao,
    ROUND(((SUM(f.tempo_ciclo_real_seg)/60.0) / ((SUM(f.tempo_ciclo_real_seg)/60.0) + SUM(f.minutos_parados))) * 
    (AVG(f.tempo_ciclo_padrao_seg) / AVG(f.tempo_ciclo_real_seg)) * AVG(f.peca_aprovada) * 100, 1) AS oee_pct
FROM fato_producao f
JOIN dim_estacao e ON f.id_estacao = e.id_estacao
GROUP BY e.estacao
ORDER BY oee_pct ASC
"""
df1 = pd.read_sql_query(q1, conn)
cores_oee = ['#e74c3c' if x < 45 else '#f39c12' if x < 58 else '#27ae60' for x in df1['oee_pct']]
bars1 = axes[0, 0].barh(df1['estacao'], df1['oee_pct'], color=cores_oee)
axes[0, 0].set_title('1. Eficiência Global (OEE %) por Estação (Gargalos)', fontweight='bold')
axes[0, 0].set_xlabel('OEE (%)')
axes[0, 0].set_xlim(0, 80)
for bar in bars1:
    xval = bar.get_width()
    axes[0, 0].text(xval + 1, bar.get_y() + bar.get_height()/2, f'{xval}%', va='center', fontweight='bold')

# --- GRÁFICO 2: Prejuízo Financeiro por Motivo de Parada (R$ Mil) ---
q2 = """
SELECT motivo_parada, SUM(custo_parada_brl) / 1000.0 AS prejuizo_mil
FROM fato_producao
WHERE motivo_parada != 'Sem Parada'
GROUP BY motivo_parada
ORDER BY prejuizo_mil ASC
"""
df2 = pd.read_sql_query(q2, conn)
bars2 = axes[0, 1].barh(df2['motivo_parada'], df2['prejuizo_mil'], color='#2c3e50')
axes[0, 1].set_title('2. Prejuízo Financeiro por Motivo de Parada (R$ Mil)', fontweight='bold')
axes[0, 1].set_xlabel('Prejuízo Acumulado (R$ Mil)')
axes[0, 1].set_xlim(0, df2['prejuizo_mil'].max() * 1.22)
for bar in bars2:
    xval = bar.get_width()
    axes[0, 1].text(xval + 20, bar.get_y() + bar.get_height()/2, f'R$ {xval:,.0f}k', va='center', fontweight='bold')

# --- GRÁFICO 3: Tempo Médio de Reparo (MTTR) por Turno ---
q3 = """
SELECT t.turno, ROUND(AVG(f.minutos_parados), 1) AS mttr_min
FROM fato_producao f
JOIN dim_turno t ON f.id_turno = t.id_turno
WHERE f.motivo_parada != 'Sem Parada'
GROUP BY t.turno
ORDER BY t.turno
"""
df3 = pd.read_sql_query(q3, conn)
bars3 = axes[1, 0].bar(df3['turno'], df3['mttr_min'], color=['#3498db', '#e67e22', '#9b59b6'], width=0.5)
axes[1, 0].set_title('3. Tempo Médio de Reparo (MTTR em Minutos) por Turno', fontweight='bold')
axes[1, 0].set_ylabel('Minutos Médios por Parada')
axes[1, 0].set_ylim(0, 16)
for bar in bars3:
    yval = bar.get_height()
    axes[1, 0].text(bar.get_x() + bar.get_width()/2, yval + 0.4, f'{yval} min', ha='center', fontweight='bold')

# --- GRÁFICO 4: Evolução Mensal do Custo de Paradas (R$ Mil) ---
q4 = """
SELECT mes, SUM(custo_parada_brl) / 1000.0 AS custo_mil
FROM fato_producao
GROUP BY mes
ORDER BY mes
"""
df4 = pd.read_sql_query(q4, conn)
axes[1, 1].plot(df4['mes'], df4['custo_mil'], marker='o', linewidth=3, markersize=8, color='#c0392b')
axes[1, 1].set_title('4. Evolução Mensal do Custo de Ineficiência (R$ Mil)', fontweight='bold')
axes[1, 1].set_ylabel('Custo Total de Paradas (R$ Mil)')
axes[1, 1].set_ylim(df4['custo_mil'].min() * 0.85, df4['custo_mil'].max() * 1.12)
for i, txt in enumerate(df4['custo_mil']):
    axes[1, 1].annotate(f'R$ {txt:,.0f}k', (df4['mes'][i], df4['custo_mil'][i]), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('dashboard/painel_smartline_oee.png', dpi=300)
print("Painel industrial salvo com sucesso em 'dashboard/painel_smartline_oee.png'!")
conn.close()