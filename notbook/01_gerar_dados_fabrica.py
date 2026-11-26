import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
n_registros = 15000

# Configurações da linha de montagem modular
estacoes = ['EST-01_Chassi', 'EST-02_Suspensao', 'EST-03_Powertrain', 'EST-04_Eletrica', 'EST-05_Inspecao_Final']
turnos = ['1º Turno (06:00-15:00)', '2º Turno (15:05-00:03)', '3º Turno (00:05-05:55)']
motivos_parada = ['Sem Parada', 'Falha Sensor/PLC', 'Falta de Peça (Logística)', 'Ajuste Torque/Ferramenta', 'Setup/Troca Modelo']

# Gerar datas ao longo de 90 dias
data_inicio = datetime(2026, 8, 1)
datas = [data_inicio + timedelta(minutes=int(x)) for x in np.random.randint(0, 90*24*60, n_registros)]

df = pd.DataFrame({
    'id_apontamento': range(10001, 10001 + n_registros),
    'data_hora': datas,
    'estacao': np.random.choice(estacoes, n_registros, p=[0.18, 0.22, 0.25, 0.20, 0.15]),
    'turno': np.random.choice(turnos, n_registros, p=[0.40, 0.42, 0.18]),
    'tempo_ciclo_padrao_seg': 55.0,
    'tempo_ciclo_real_seg': np.random.normal(56.5, 4.2, n_registros).round(1),
    'peca_aprovada': np.random.choice([1, 0], n_registros, p=[0.975, 0.025]),
    'motivo_parada': np.random.choice(motivos_parada, n_registros, p=[0.84, 0.05, 0.05, 0.04, 0.02]),
})

# Simular gargalos reais (EST-03_Powertrain e Falta de Peça no 2º Turno)
def calcular_parada(row):
    if row['motivo_parada'] == 'Sem Parada':
        return 0.0
    base = np.random.exponential(8.0) + 2.0
    if row['estacao'] == 'EST-03_Powertrain':
        base *= 1.6
    if row['motivo_parada'] == 'Falta de Peça (Logística)' and '2º Turno' in row['turno']:
        base *= 1.4
    return round(base, 1)

df['minutos_parados'] = df.apply(calcular_parada, axis=1)

# Injetar sujeira proposital para o ETL tratar (sensores negativos e linhas duplicadas)
df.loc[10:25, 'tempo_ciclo_real_seg'] = -5.0
df = pd.concat([df, df.iloc[0:45]], ignore_index=True)

df = df.sort_values('data_hora').reset_index(drop=True)
df.to_csv('data/producao_linha_bruto.csv', index=False)

print(f"Dataset industrial gerado com sucesso! Total de linhas: {len(df)}")
print("Arquivo salvo em: data/producao_linha_bruto.csv")