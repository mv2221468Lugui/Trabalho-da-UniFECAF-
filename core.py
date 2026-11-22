"""Motor de roteamento para um mapa urbano inteiramente simulado."""
import csv, math, heapq
from pathlib import Path
import networkx as nx
import numpy as np
from sklearn.cluster import KMeans

ROOT = Path(__file__).resolve().parents[1]

def load_data():
    g = nx.Graph()
    with (ROOT/'data/nodes.csv').open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            g.add_node(r['id'], x=float(r['x']), y=float(r['y']), name=r['name'])
    with (ROOT/'data/edges.csv').open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            g.add_edge(r['source'],r['target'],distance_km=float(r['distance_km']),time_min=float(r['time_min']))
    with (ROOT/'data/deliveries.csv').open(encoding='utf-8',newline='') as f:
        orders=[dict(r) for r in csv.DictReader(f)]
    return g,orders

def heuristic(g,a,b,weight='distance_km'):
    u,v=g.nodes[a],g.nodes[b]
    straight=math.hypot(u['x']-v['x'],u['y']-v['y'])
    # Distâncias das arestas são >= distância euclidiana. Para tempo,
    # velocidade máxima simulada de 60 km/h => 1 minuto por km.
    return straight if weight=='distance_km' else straight

def astar(g,start,end,weight='distance_km'):
    return nx.astar_path(g,start,end,heuristic=lambda a,b:heuristic(g,a,b,weight),weight=weight)

def dijkstra(g,start,end,weight='distance_km'):
    return nx.dijkstra_path(g,start,end,weight=weight)

def bfs(g,start,end):
    return nx.shortest_path(g,start,end) # minimiza quantidade de arestas

def dfs(g,start,end):
    return nx.dfs_tree(g,start).nodes if False else _dfs_path(g,start,end)

def _dfs_path(g,start,end):
    stack=[(start,[start])]; visited=set()
    while stack:
        node,path=stack.pop()
        if node==end:return path
        if node in visited:continue
        visited.add(node)
        for nxt in sorted(g.neighbors(node),reverse=True):
            if nxt not in visited:stack.append((nxt,path+[nxt]))
    raise nx.NetworkXNoPath

def cost(g,path,weight='distance_km'):
    return sum(g[a][b][weight] for a,b in zip(path,path[1:]))

def cluster_orders(g,orders,k=3):
    k=min(k,len(orders))
    coords=np.array([[g.nodes[o['node']]['x'],g.nodes[o['node']]['y']] for o in orders])
    model=KMeans(n_clusters=k,random_state=42,n_init=10)
    return model.fit_predict(coords).tolist(),model.cluster_centers_

def route(g,stops,depot='N00',weight='time_min',optimized=True):
    """Visita cada parada uma vez, retorna ao depósito; heurística vizinho mais próximo."""
    pending=list(dict.fromkeys(stops)); current=depot; sequence=[depot]
    while pending:
        if optimized:
            nxt=min(pending,key=lambda n:(nx.shortest_path_length(g,current,n,weight=weight),n))
        else:nxt=pending[0]
        sequence.append(nxt);pending.remove(nxt);current=nxt
    sequence.append(depot)
    if optimized:
        # 2-opt sobre a sequência de paradas, com custos reais de menor caminho.
        def sequence_cost(seq):
            return sum(nx.shortest_path_length(g,a,b,weight=weight) for a,b in zip(seq,seq[1:]))
        baseline=[depot]+list(dict.fromkeys(stops))+[depot]
        if sequence_cost(baseline)<sequence_cost(sequence):sequence=baseline
        improved=True
        while improved:
            improved=False
            for i in range(1,len(sequence)-2):
                for j in range(i+1,len(sequence)-1):
                    candidate=sequence[:i]+list(reversed(sequence[i:j+1]))+sequence[j+1:]
                    if sequence_cost(candidate)+1e-9<sequence_cost(sequence):
                        sequence=candidate;improved=True
    full=[]
    for a,b in zip(sequence,sequence[1:]):
        segment=astar(g,a,b,weight)
        full.extend(segment if not full else segment[1:])
    return sequence,full,cost(g,full,'distance_km'),cost(g,full,'time_min')

def evaluate(g,orders,k=3):
    labels,centers=cluster_orders(g,orders,k)
    groups={i:[] for i in range(len(centers))}
    for order,label in zip(orders,labels):groups[label].append(order['node'])
    rows=[]
    for i,stops in groups.items():
        for optimized in (False,True):
            seq,path,dist,t=route(g,stops,weight='distance_km',optimized=optimized)
            rows.append(dict(group=i+1,method='Otimizada' if optimized else 'Ordem original',stops=len(stops),distance_km=round(dist,3),time_min=round(t,2),sequence=' → '.join(seq),path=path))
    return rows,labels,centers
