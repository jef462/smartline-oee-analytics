# 🏭 SmartLine Analytics — Monitoramento de OEE e Redução de Paradas Industriais

## 1. Contexto do Problema de Negócio
Uma linha de montagem modular automotiva operando em três turnos (incluindo o 2º turno das 15h05 às 00h03) registra perdas recorrentes de produtividade devido a microparadas não programadas e gargalos de abastecimento logístico, acumulando **R$ 5.081.130,00** em custos de parada em um trimestre. O objetivo deste projeto é estruturar um Data Warehouse industrial para mensurar o **OEE (Overall Equipment Effectiveness)**, calcular o **MTTR (Tempo Médio de Reparo)** e priorizar planos de ação com maior retorno financeiro.

## 2. Arquitetura de Dados e Ferramentas
* **Python (Pandas & NumPy):** Simulação de apontamentos de chão de fábrica (15.000 ciclos ao longo de 90 dias) e pipeline de ETL para remoção de duplicatas e saneamento de leituras inválidas de sensores.
* **SQL & Data Warehousing (SQLite):** Modelagem dimensional em **Star Schema** (`fato_producao`, `dim_estacao`, `dim_turno`) e consultas analíticas utilizando `JOIN`, CTEs (`WITH`), agregações condicionais e *Window Functions* (`RANK() OVER()`).
* **Matplotlib:** Painel executivo de indicadores industriais (OEE, MTTR, Pareto de perdas e evolução mensal).

## 3. Painel Executivo e Principais Descobertas
![Painel SmartLine OEE](dashboard/painel_smartline_oee.png)

1. **Gargalo Crítico na EST-03 (Powertrain):** A estação concentra **32,85%** de todo o prejuízo financeiro da linha (**R$ 1.669.032,00** no trimestre), puxando o OEE da estação para baixo devido ao elevado tempo de parada.
2. **Vulnerabilidade Logística no 2º Turno:** O principal ofensor por turno é a **Falta de Peça (Logística) no 2º Turno (15:05–00:03)**, somando **R$ 853.524,00** em prejuízo e o pior MTTR da operação (**15,3 minutos** por ocorrência).
3. **Falhas de Automação:** Paradas por **Falha de Sensor/PLC** aparecem entre os maiores ofensores em todos os turnos (somando mais de **R$ 1,45 milhão** nos três turnos), indicando necessidade de manutenção preditiva nos sensores de presença e torque.

## 4. Plano de Ação e ROI Simulado (Backtesting)
Simulando a implantação de manutenção preventiva na **EST-03_Powertrain** (-40% de paradas) e reabastecimento antecipado via Kanban eletrônico no **2º Turno** (-50% de faltas de peça), o modelo projeta:
* **Custo Atual de Paradas (Trimestre):** R$ 5.081.130,00
* **Custo Projetado após Melhorias:** R$ 4.039.203,60
* **Economia Direta no Trimestre:** **R$ 1.041.926,40** (-20,5% de redução de perdas)
* **Projeção de Economia Anual:** **R$ 4.167.705,60**

## 5. Estrutura do Repositório
* `data/`: Apontamentos brutos (`producao_linha_bruto.csv`) e consolidados (`producao_linha_limpo.csv`).
* `notbook/`: Scripts de geração de dados (`01_gerar_dados_fabrica.py`), ETL Star Schema (`02_etl_star_schema.py`), painel visual (`03_painel_oee.py`) e simulação de ROI (`04_simulacao_roi_oee.py`).
* `sql/`: Banco dimensional (`smartline_dw.db`) e queries analíticas de OEE/MTTR (`01_analise_oee.py`).
* `dashboard/`: Painel executivo exportado (`painel_smartline_oee.png`).