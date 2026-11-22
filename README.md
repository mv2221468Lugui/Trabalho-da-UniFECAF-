# 🚚 Rota Inteligente — Sabor Express

Projeto acadêmico da disciplina **Artificial Intelligence Fundamentals**. Demonstra otimização de entregas em uma **cidade fictícia**, usando grafos, busca A*, BFS, DFS, Dijkstra e agrupamento K-Means.

> **Aviso:** todos os pontos, ruas, pedidos, tempos e distâncias são **dados simulados**. Nenhuma economia representa resultado operacional real da UPS ou de uma empresa de delivery.

## Problema e objetivos

A Sabor Express planeja entregas manualmente, enfrentando trajetos longos e atrasos. Este protótipo representa ruas por um grafo ponderado, calcula caminhos entre pontos e organiza pedidos em zonas, visando comparar um roteiro na ordem recebida com um roteiro por vizinho mais próximo com refinamento 2-opt.

## Abordagem

- **Grafo:** 25 interseções em malha 5×5; 40 ruas bidirecionais. `distance_km` e `time_min` são pesos sintéticos; depósito `N00`.
- **A\*:** menor custo entre dois nós, com heurística de distância euclidiana. A heurística é admissível para distância (cada aresta tem pelo menos o deslocamento em linha reta) e para tempo (todas as arestas simuladas levam mais de 1 min/km). Logo, o A* encontra o mesmo custo mínimo que Dijkstra no grafo fornecido.
- **Dijkstra:** referência de custo mínimo ponderado.
- **BFS:** minimiza número de arestas, não necessariamente distância/tempo.
- **DFS:** percurso em profundidade; não garante caminho mínimo.
- **K-Means:** agrupa pedidos por proximidade geométrica (coordenadas artificiais); `random_state=42` garante repetibilidade.
- **Roteiro multi-entregas:** para cada grupo, escolhe o próximo pedido pela menor distância de caminho na rede a partir do ponto atual (vizinho mais próximo com refinamento 2-opt); retorna ao depósito. Cada trecho é calculado com A*. **Não garante solução global ótima do problema do caixeiro-viajante (TSP).**
- **Linha de base:** visita pedidos na ordem do CSV, com caminhos mínimos entre paradas, e retorna ao depósito. Assim a comparação mede o efeito da reordenação dos pedidos **mantendo os mesmos grupos e os mesmos caminhos entre paradas**.

## Estrutura

```text
rota-inteligente-sabor-express/
├── app.py                    # Dashboard Streamlit
├── src/
│   ├── core.py               # Grafo, buscas, clustering e roteiros
│   └── generate_outputs.py   # Gera métricas e imagens
├── data/
│   ├── nodes.csv             # Coordenadas e pontos
│   ├── edges.csv             # Ruas e pesos
│   └── deliveries.csv        # Pedidos fictícios
├── outputs/                  # PNG, CSV e JSON gerados
├── docs/
│   ├── metodologia.md
│   └── roteiro_pitch.md
├── tests/test_core.py
├── requirements.txt
└── README.md
```

## Instalação e execução

Recomendado: **Python 3.11 ou 3.12**.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.generate_outputs
python -m unittest discover -s tests -v
python -m streamlit run app.py
```

No Windows, caso a ativação do PowerShell seja bloqueada, execute diretamente `.venv\Scripts\python.exe -m pip install -r requirements.txt` e `.venv\Scripts\python.exe -m streamlit run app.py`.

## Resultados

As métricas reproduzíveis estão em [`outputs/summary.json`](outputs/summary.json) e [`outputs/metrics.csv`](outputs/metrics.csv). As imagens são geradas pelo script, sem manipulação manual.

![Grafo simulado](outputs/grafo.png)
![Zonas K-Means](outputs/clusters.png)
![Comparação de roteiros](outputs/comparacao.png)

**Métricas:** distância total percorrida (km), tempo estimado total (min) e redução percentual de distância frente à linha de base. A avaliação utiliza distância como custo de otimização; o dashboard permite explorar rotas por tempo. A comparação é realizada com três zonas por padrão, cada uma atendida por um entregador fictício. Tempos **não incluem** trânsito variável, espera, preparo, estacionamento ou atendimento ao cliente.

## Limitações

Malha sintética, vias bidirecionais, sem sentido único, horários de pico, janelas de entrega, capacidades de veículos ou tráfego real. K-Means não considera a distância viária. O vizinho mais próximo com refinamento 2-opt pode produzir uma rota pior que a ordem original em alguns grupos; não há garantia de melhoria nem de ótimo global. A soma de tempos não é um tempo de conclusão de frota paralela. O agrupamento usa distância geométrica; a escolha de próximos pontos usa distância viária na avaliação e pode usar tempo no dashboard.

## Melhorias futuras

Dados reais do OpenStreetMap/OSMnx, sentidos de ruas, previsão de tráfego, horários de entrega, restrições de carga, otimização VRP com OR-Tools, análise de sensibilidade e experimentos com múltiplas sementes e cenários.

## Referências para estudo

- Hart, Nilsson e Raphael (1968): *A Formal Basis for the Heuristic Determination of Minimum Cost Paths*.
- Documentação NetworkX: https://networkx.org/documentation/stable/
- Documentação scikit-learn KMeans: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
- UPS ORION (contexto de logística): https://about.ups.com/

## GitHub e apresentação

Crie um repositório público, envie **todos os arquivos** e use o roteiro em [`docs/roteiro_pitch.md`](docs/roteiro_pitch.md). A publicação no GitHub e o upload do vídeo no YouTube são etapas manuais; não são realizados por este pacote.

## Licença

MIT — consulte [`LICENSE`](LICENSE).
