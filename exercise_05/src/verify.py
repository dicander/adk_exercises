import itertools, heapq
# ---------- MST graph ----------
E={('a','c'):1,('b','e'):2,('e','h'):3,('g','h'):4,('b','d'):5,('d','g'):6,('a','g'):7,('g','i'):8,('a','b'):9,('e','f'):10}
V=sorted(set(x for e in E for x in e))
def adj(Ew):
    A={v:[] for v in V}
    for (u,v),w in Ew.items(): A[u].append((v,w)); A[v].append((u,w))
    return A
def kruskal(Ew):
    p={v:v for v in V}
    def f(x):
        while p[x]!=x: x=p[x]
        return x
    T=[];log=[]
    for (u,v),w in sorted(Ew.items(),key=lambda t:t[1]):
        if f(u)!=f(v): p[f(u)]=f(v); T.append((u,v)); log.append((w,u,v,'ok'))
        else: log.append((w,u,v,'rej'))
    return T,log
def prim(Ew,r='a'):
    A=adj(Ew); key={v:float('inf') for v in V}; par={}; key[r]=0; intree=set(); order=[]
    while len(intree)<len(V):
        u=min((v for v in V if v not in intree),key=lambda v:key[v]); intree.add(u); order.append((u,key[u]))
        for v,w in A[u]:
            if v not in intree and w<key[v]: key[v]=w; par[v]=u
    return order,par
def dijkstra(Ew,r='a'):
    A=adj(Ew); d={v:float('inf') for v in V}; d[r]=0; par={}; done=set()
    while len(done)<len(V):
        u=min((v for v in V if v not in done),key=lambda v:d[v]); done.add(u)
        for v,w in A[u]:
            if d[u]+w<d[v]: d[v]=d[u]+w; par[v]=u
    return d,par
T,log=kruskal(E); print('Kruskal',log); print('MST weight',sum(E[e] for e in T))
o,p=prim(E); print('Prim order',o)
d,p=dijkstra(E); print('Dijkstra d',d); spt=[E.get((u,v),E.get((v,u))) for v,u in p.items()]; print('SPT weights',sorted(spt),sum(spt))
E2={e:w*w for e,w in E.items()}; d2,p2=dijkstra(E2); print('squared SPT parents',p2, 'MST',sorted(kruskal(E2)[0])==sorted(T))
Ep={e:w+5 for e,w in E.items()}; print('w+5 SPT parents same?',dijkstra(Ep)[1]==p, 'MST same', sorted(kruskal(Ep)[0])==sorted(T))
Es=dict(E); Es[('b','d')]=6; Es[('d','g')]=5; Ts=kruskal(Es)[0]; print('swap56 MST',Ts,sum(Es[e] for e in Ts),'SPT same?',dijkstra(Es)[1]==p)
# ties d-g=5: enumerate all spanning trees and min weight ones
def all_msts(Ew):
    es=list(Ew); best=None; res=[]
    for comb in itertools.combinations(es,len(V)-1):
        p={v:v for v in V}
        def f(x):
            while p[x]!=x: x=p[x]
            return x
        ok=True
        for u,v in comb:
            if f(u)==f(v): ok=False;break
            p[f(u)]=f(v)
        if not ok: continue
        w=sum(Ew[e] for e in comb)
        if best is None or w<best: best=w; res=[comb]
        elif w==best: res.append(comb)
    return best,res
print('orig MSTs',all_msts(E)[0],len(all_msts(E)[1]))
Et=dict(E); Et[('d','g')]=5; b,r=all_msts(Et); print('tie dg=5',b,len(r))
Et=dict(E); Et[('e','f')]=9; b,r=all_msts(Et); print('tie ef=9',b,len(r))
# cut S={d,g,i}
S={'d','g','i'}; print('cut crossing',[(e,w) for e,w in E.items() if (e[0] in S)!=(e[1] in S)])
# Boruvka round1
cheap={}
for v in V:
    cheap[v]=min([(w,e) for e,w in E.items() if v in e])
print('Boruvka r1',sorted(set(w for w,e in cheap.values())))
