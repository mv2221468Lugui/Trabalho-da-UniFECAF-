import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from src.core import load_data,evaluate,astar,dijkstra,bfs,dfs,cost,route

st.set_page_config(page_title='Sabor Express | Rota Inteligente',page_icon='🚚',layout='wide')
st.title('🚚 Sabor Express | Rota Inteligente')
st.caption('Protótipo acadêmico — ruas, tráfego, pedidos e métricas são simulados.')
g,orders=load_data()
st.sidebar.header('Configurações')
weight=st.sidebar.selectbox('Otimizar por',['time_min','distance_km'],format_func=lambda x:'Tempo estimado' if x=='time_min' else 'Distância')
k=st.sidebar.slider('Número de zonas (K-Means)',1,min(6,len(orders)),3)
rows,labels,centers=evaluate(g,orders,k)
original=sum(r['distance_km'] for r in rows if r['method']=='Ordem original')
optimized=sum(r['distance_km'] for r in rows if r['method']=='Otimizada')
a,b,c=st.columns(3)
a.metric('Pedidos simulados',len(orders));b.metric('Distância base',f'{original:.1f} km');c.metric('Distância otimizada',f'{optimized:.1f} km',delta=f'{(original-optimized)/original*100:.1f}% menor' if original else None,delta_color='normal')
tab1,tab2,tab3=st.tabs(['Mapa e clusters','Rotas por zona','Comparação de algoritmos'])
pos={n:(d['x'],d['y']) for n,d in g.nodes(data=True)}
with tab1:
    fig,ax=plt.subplots(figsize=(10,6))
    nx.draw_networkx_edges(g,pos,ax=ax,edge_color='lightgray')
    nx.draw_networkx_nodes(g,pos,ax=ax,node_color='#e5e7eb',node_size=180)
    nx.draw_networkx_labels(g,pos,ax=ax,font_size=8)
    cmap=plt.get_cmap('tab10')
    for i in range(k):
        nodes=[o['node'] for o,l in zip(orders,labels) if l==i]
        nx.draw_networkx_nodes(g,pos,nodelist=nodes,ax=ax,node_color=[cmap(i)],node_size=400,label=f'Zona {i+1}')
    nx.draw_networkx_nodes(g,pos,nodelist=['N00'],ax=ax,node_color='orange',node_size=650)
    ax.legend();ax.axis('off');st.pyplot(fig);plt.close(fig)
with tab2:
    df=pd.DataFrame([{key:v for key,v in r.items() if key!='path'} for r in rows]);st.dataframe(df,use_container_width=True)
    zone=st.selectbox('Visualizar zona',list(range(1,k+1)))
    stops=[o['node'] for o,l in zip(orders,labels) if l==zone-1]
    seq,path,dist,t=route(g,stops,weight=weight)
    st.write('Sequência:', ' → '.join(seq));st.write(f'Distância: {dist:.2f} km | Tempo: {t:.1f} min')
    fig,ax=plt.subplots(figsize=(10,6));nx.draw_networkx(g,pos,ax=ax,node_color='#dbeafe',node_size=300,font_size=8)
    nx.draw_networkx_edges(g,pos,edgelist=list(zip(path,path[1:])),ax=ax,edge_color='#ef4444',width=3)
    ax.axis('off');st.pyplot(fig);plt.close(fig)
with tab3:
    start=st.selectbox('Origem',list(g.nodes),index=0)
    end=st.selectbox('Destino',list(g.nodes),index=len(g.nodes)-1)
    if start!=end:
        for name,fn in [('A*',astar),('Dijkstra',dijkstra),('BFS',bfs),('DFS',dfs)]:
            path=fn(g,start,end,weight) if name in ('A*','Dijkstra') else fn(g,start,end)
            st.write(f'**{name}**: {" → ".join(path)} | {cost(g,path,"distance_km"):.2f} km | {cost(g,path,"time_min"):.1f} min')
    else:st.info('Selecione pontos diferentes.')
st.info('K-Means agrupa por coordenadas, não por tempo de viagem. A heurística de múltiplas paradas não garante o ótimo global.')
