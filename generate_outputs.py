"""Gera imagens e métricas reproduzíveis em outputs/."""
import csv, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from .core import ROOT,load_data,evaluate,astar,dijkstra,bfs,dfs,cost

def main():
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    g,orders=load_data();rows,labels,centers=evaluate(g,orders)
    with (out/'metrics.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['group','method','stops','distance_km','time_min','sequence']);writer.writeheader()
        for row in rows:writer.writerow({key:row[key] for key in writer.fieldnames})
    pos={n:(d['x'],d['y']) for n,d in g.nodes(data=True)}
    plt.figure(figsize=(10,7))
    nx.draw_networkx(g,pos,node_size=330,font_size=7,edge_color='#a7b3c2',node_color='#d9e9ff')
    nx.draw_networkx_nodes(g,pos,nodelist=['N00'],node_color='#fbbf24',node_size=550)
    plt.title('Mapa simulado de ruas — depósito N00');plt.axis('off');plt.tight_layout();plt.savefig(out/'grafo.png',dpi=170);plt.close()
    plt.figure(figsize=(10,7))
    nx.draw_networkx_edges(g,pos,edge_color='#d1d5db')
    nx.draw_networkx_nodes(g,pos,node_color='#e5e7eb',node_size=160)
    nx.draw_networkx_labels(g,pos,font_size=7)
    palette=plt.get_cmap('tab10')
    for i in range(len(centers)):
        nodes=[o['node'] for o,l in zip(orders,labels) if l==i]
        nx.draw_networkx_nodes(g,pos,nodelist=nodes,node_color=[palette(i)],node_size=380,label=f'Zona {i+1}')
    nx.draw_networkx_nodes(g,pos,nodelist=['N00'],node_color='#fbbf24',node_size=600)
    plt.legend();plt.title('K-Means: zonas de entregas simuladas');plt.axis('off');plt.tight_layout();plt.savefig(out/'clusters.png',dpi=170);plt.close()
    plt.figure(figsize=(9,5))
    x=list(range(1,len(centers)+1));width=.35
    old=[next(r['distance_km'] for r in rows if r['group']==i and r['method']=='Ordem original') for i in x]
    new=[next(r['distance_km'] for r in rows if r['group']==i and r['method']=='Otimizada') for i in x]
    plt.bar([v-width/2 for v in x],old,width,label='Ordem original')
    plt.bar([v+width/2 for v in x],new,width,label='Vizinho mais próximo')
    plt.xticks(x,[f'Zona {i}' for i in x]);plt.ylabel('Distância total (km)');plt.title('Comparação de roteiros por zona');plt.legend();plt.tight_layout();plt.savefig(out/'comparacao.png',dpi=170);plt.close()
    summary={'original_distance_km':round(sum(old),3),'optimized_distance_km':round(sum(new),3),'original_time_min':round(sum(r['time_min'] for r in rows if r['method']=='Ordem original'),2),'optimized_time_min':round(sum(r['time_min'] for r in rows if r['method']=='Otimizada'),2)}
    summary['distance_reduction_pct']=round(100*(summary['original_distance_km']-summary['optimized_distance_km'])/summary['original_distance_km'],2)
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
