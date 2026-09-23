# -*- coding: utf-8 -*-
"""Genererar TikZ för uppgift 4 (julklappsfördelning) och kontrollerar exemplet."""
import os
from collections import deque
OUT = 'gen'
os.makedirs(OUT, exist_ok=True)

TAS = ['Emma', 'Elliot', 'Marcus', 'Lovisa']
ITEMS = ['RTX', 'PS5', 'Xbox', 'Switch']
LABEL = {'RTX': 'RTX 5090', 'PS5': 'PS5 Pro', 'Xbox': 'Xbox Series X', 'Switch': 'Switch 2'}
WISH = {'Emma': ['RTX', 'PS5'], 'Elliot': ['RTX', 'Xbox'], 'Marcus': ['RTX'],
        'Lovisa': ['RTX', 'PS5', 'Switch']}


# ----------------------------------------------------------------------
#  Kontroller
# ----------------------------------------------------------------------
def greedy(wish):
    taken, M = set(), {}
    for p in TAS:
        for it in wish[p]:
            if it not in taken:
                taken.add(it)
                M[p] = it
                break
    return M


def edmonds_karp(wish):
    """Heltalsflöde s->barn->sak->t, alla kapaciteter 1. Returnerar stigarna."""
    cap = {}
    adj = {}

    def add(u, v):
        cap[(u, v)] = cap.get((u, v), 0) + 1
        cap.setdefault((v, u), 0)
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    for p in TAS:
        add('s', p)
    for p in TAS:
        for it in wish[p]:
            add(p, it)
    for it in ITEMS:
        add(it, 't')
    paths = []
    while True:
        par = {'s': None}
        q = deque(['s'])
        while q and 't' not in par:
            u = q.popleft()
            for v in adj[u]:
                if v not in par and cap[(u, v)] > 0:
                    par[v] = u
                    q.append(v)
        if 't' not in par:
            break
        path, v = [], 't'
        while v is not None:
            path.append(v)
            v = par[v]
        path.reverse()
        for a, b in zip(path, path[1:]):
            cap[(a, b)] -= 1
            cap[(b, a)] += 1
        paths.append(path)
    M = {p: it for p in TAS for it in ITEMS if (p, it) in cap and cap[(it, p)] == 1 and it in wish[p]}
    return paths, M


G = greedy(WISH)
assert G == {'Emma': 'RTX', 'Elliot': 'Xbox', 'Lovisa': 'PS5'}, G
PATHS, MFINAL = edmonds_karp(WISH)
assert PATHS == [['s', 'Emma', 'RTX', 't'], ['s', 'Elliot', 'Xbox', 't'], ['s', 'Lovisa', 'PS5', 't'],
                 ['s', 'Marcus', 'RTX', 'Emma', 'PS5', 'Lovisa', 'Switch', 't']], PATHS
assert MFINAL == {'Emma': 'PS5', 'Elliot': 'Xbox', 'Marcus': 'RTX', 'Lovisa': 'Switch'}, MFINAL
# Hall-varianter
W2 = dict(WISH)
W2['Emma'] = ['RTX']
assert len(edmonds_karp(W2)[1]) == 3
W3 = {p: ['RTX'] for p in TAS}
assert len(edmonds_karp(W3)[1]) == 1
# unik perfekt matchning?
import itertools
perfect = [perm for perm in itertools.permutations(ITEMS)
           if all(perm[i] in WISH[TAS[i]] for i in range(4))]
assert perfect == [('PS5', 'Xbox', 'RTX', 'Switch')], perfect


def write(name, text):
    with open(os.path.join(OUT, name), 'w') as fh:
        fh.write(text + "\n")


# ----------------------------------------------------------------------
#  Ritning
# ----------------------------------------------------------------------
YS = [1.65, 0.55, -0.55, -1.65]
XP, XI = 2.3, 6.5
NODES = {'s': (0, 0), 't': (8.8, 0)}
for i, p in enumerate(TAS):
    NODES[p] = (XP, YS[i])
for i, it in enumerate(ITEMS):
    NODES[it] = (XI, YS[i])

STYLES = r"""pers/.style={rounded corners=3pt,draw=kthnavy,fill=white,line width=0.7pt,
    minimum width=15mm,minimum height=5.5mm,inner sep=1pt,font=\footnotesize},
  sak/.style={rounded corners=3pt,draw=kthblue,fill=kthlight,line width=0.7pt,
    minimum width=21mm,minimum height=5.5mm,inner sep=1pt,font=\footnotesize},
  me/.style={draw=black!30,line width=0.7pt},
  mm/.style={draw=kthblue,line width=2.2pt},
  mp/.style={->,draw=kthgrass,line width=2.4pt},
  mb/.style={->,draw=kthorange,line width=2pt,dash pattern=on 4pt off 2pt}"""


def node_lines(with_st=True, fills=None):
    fills = fills or {}
    L = []
    if with_st:
        L.append(r"  \node[fn] (s) at (0,0) {$s$};")
        L.append(r"  \node[fn] (t) at (8.8,0) {$t$};")
    for p in TAS:
        x, y = NODES[p]
        f = fills.get(p, '')
        L.append(f"  \\node[pers{(',' + f) if f else ''}] ({p}) at ({x},{y}) {{{p}}};")
    for it in ITEMS:
        x, y = NODES[it]
        f = fills.get(it, '')
        L.append(f"  \\node[sak{(',' + f) if f else ''}] ({it}) at ({x},{y}) {{{LABEL[it]}}};")
    return L


def wish_edges(wish, style='me', skip=()):
    L = []
    for p in TAS:
        for it in wish[p]:
            if (p, it) in skip:
                continue
            L.append(f"  \\draw[{style}] ({p}.east) -- ({it}.west);")
    return L


def pic_lists(name, wish=WISH, matched=None, fills=None, extra='', scale=0.9, with_st=False):
    matched = matched or {}
    L = [f"\\begin{{tikzpicture}}[scale={scale},{STYLES}]"]
    L += node_lines(with_st, fills)
    L += wish_edges(wish, 'me', skip=set(matched.items()))
    for p, it in matched.items():
        L.append(f"  \\draw[mm] ({p}.east) -- ({it}.west);")
    if with_st:
        for p in TAS:
            L.append(f"  \\draw[fe] (s) -- ({p}.west);")
        for it in ITEMS:
            L.append(f"  \\draw[fe] ({it}.east) -- (t);")
    if extra:
        L.append(extra)
    L.append("\\end{tikzpicture}")
    write(name, "\n".join(L))


def anchor_pair(a, b):
    """Rätt ankarpunkter för en kant mellan två noder (framåt eller bakåt)."""
    def side(u, v):
        if u == 's':
            return 's'
        if u == 't':
            return 't'
        xu = NODES[u][0]
        xv = NODES[v][0]
        return f"{u}.east" if xv > xu else f"{u}.west"
    return side(a, b), side(b, a)


def walk_frame():
    states = [{}, {'Emma': 'RTX'}, {'Emma': 'RTX', 'Elliot': 'Xbox'},
              {'Emma': 'RTX', 'Elliot': 'Xbox', 'Lovisa': 'PS5'}, MFINAL]
    caps = [
        r"Alla kapaciteter är 1. BFS hittar $s\to$ Emma $\to$ RTX $\to t$. Emma får grafikkortet. Tills vidare.",
        r"$s\to$ Elliot $\to$ Xbox $\to t$: RTX-kortet är upptaget, så Elliot tar sitt andra val.",
        r"$s\to$ Lovisa $\to$ PS5 $\to t$. Tre av fyra har en klapp. Marcus står kvar tomhänt.",
        r"Enda stigen: Marcus tar RTX från Emma, Emma tar PS5 från Lovisa, Lovisa tar Switch 2. "
        r"Två bakåtkanter (streckade).",
        r"Flöde 4 = perfekt matchning. Stigen i matchningstermer: alternerande ny, bort, ny, bort, ny.",
    ]
    pics = []
    for k in range(5):
        M = states[k] if k < 4 else MFINAL
        L = [f"\\begin{{tikzpicture}}[scale=0.95,{STYLES}]",
             r"\useasboundingbox (-0.4,-2.1) rectangle (9.2,2.1);"]
        L += node_lines(True)
        L += wish_edges(WISH, 'me', skip=set(M.items()))
        for p in TAS:
            st = 'mm,->' if p in M else 'fe'
            L.append(f"  \\draw[{st}] (s) -- ({p}.west);")
        for it in ITEMS:
            st = 'mm,->' if it in M.values() else 'fe'
            L.append(f"  \\draw[{st}] ({it}.east) -- (t);")
        for p, it in M.items():
            L.append(f"  \\draw[mm] ({p}.east) -- ({it}.west);")
        if k < 4:
            P = PATHS[k]
            for a, b in zip(P, P[1:]):
                back = (a in ITEMS and b in TAS)
                aa, bb = anchor_pair(a, b)
                L.append(f"  \\draw[{'mb' if back else 'mp'}] ({aa}) -- ({bb});")
        L.append("\\end{tikzpicture}")
        pics.append(f"\\only<{k + 1}>{{%\n" + "\n".join(L) + "}")
    capt = "".join(f"\\only<{k + 1}>{{{c}}}" for k, c in enumerate(caps))
    frame = (r"\begin{frame}{Ford--Fulkerson (med BFS) på julklapparna}" "\n"
             r"\centering" "\n" + "\n".join(pics) + "\n"
             r"\par\smallskip{\scriptsize\textcolor{kthblue}{\textbf{matchat}}\quad"
             r"\textcolor{kthgrass}{\textbf{förbättrande stig}}\quad"
             r"\textcolor{kthorange}{\textbf{bakåtkant: ångra}}}" "\n"
             r"\vfill" "\n"
             r"\begin{tcolorbox}[enhanced,halign=left,colback=kthlight!50,colframe=kthsky,boxrule=0.4pt,arc=2pt," "\n"
             r"  left=4pt,right=4pt,top=1pt,bottom=1pt,fontupper=\small,height=1.05cm,valign=center]" "\n"
             + capt + "\n"
             r"\end{tcolorbox}" "\n"
             r"\end{frame}")
    write('match-walk.tex', frame)


if __name__ == '__main__':
    pic_lists('match-lists.tex', scale=0.85)
    pic_lists('match-greedy.tex', matched=G, scale=0.85,
              fills={'Marcus': 'fill=coral!30'})
    pic_lists('match-net.tex', scale=0.8, with_st=True)
    hall_extra = (r"  \begin{scope}[on background layer]" "\n"
                  r"  \fill[plum!15,rounded corners=4pt] ($(Emma.north west)+(-0.12,0.12)$) rectangle ($(Emma.south east)+(0.12,-0.12)$);" "\n"
                  r"  \fill[plum!15,rounded corners=4pt] ($(Marcus.north west)+(-0.12,0.12)$) rectangle ($(Marcus.south east)+(0.12,-0.12)$);" "\n"
                  r"  \fill[plum!15,rounded corners=4pt] ($(RTX.north west)+(-0.12,0.12)$) rectangle ($(RTX.south east)+(0.12,-0.12)$);" "\n"
                  r"  \end{scope}")
    pic_lists('match-hall.tex', wish=W2, scale=0.78, extra=hall_extra,
              fills={'Emma': 'draw=plum,line width=1.2pt', 'Marcus': 'draw=plum,line width=1.2pt',
                     'RTX': 'draw=plum,line width=1.2pt'})
    walk_frame()
    print('girig:', G)
    print('stigar:', PATHS)
    print('slut:', MFINAL)
