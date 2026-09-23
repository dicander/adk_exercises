# -*- coding: utf-8 -*-
"""Genererar TikZ för uppgift 3 (Eulercykel) och kontrollerar spårningen."""
import os
OUT = 'gen'
os.makedirs(OUT, exist_ok=True)

POS = {1: (0, 0), 2: (1.5, 1.2), 3: (3, 0), 4: (-1.5, 1.2), 5: (-1.5, -1.2), 6: (4.5, 1.2), 7: (4.5, -1.2)}
EDGES = [(1, 2), (2, 3), (3, 1), (1, 4), (4, 5), (5, 1), (3, 6), (6, 7), (7, 3)]


# ----------------------------------------------------------------------
#  Viggos algoritm (PathFinder/Straggler), sorterade grannlistor
# ----------------------------------------------------------------------
def euler_trace():
    adj = {v: sorted([b for a, b in EDGES if a == v] + [a for a, b in EDGES if b == v]) for v in POS}
    marked = set()
    cycle = [1]
    log = []

    def key(u, v):
        return (min(u, v), max(u, v))

    def pathfinder(start, cur):
        path = [cur]
        while cur != start:
            v = next(w for w in adj[cur] if key(cur, w) not in marked)
            marked.add(key(cur, v))
            path.append(v)
            cur = v
        log.append(('tur', start, list(path)))
        return path

    def straggler(path):
        for u in path:
            cycle.append(u)
            for v in adj[u]:
                if key(u, v) not in marked:
                    marked.add(key(u, v))
                    straggler(pathfinder(u, v))

    t = adj[1][0]
    marked.add(key(1, t))
    straggler(pathfinder(1, t))
    return cycle, log


CYCLE, LOG = euler_trace()
assert CYCLE == [1, 2, 3, 6, 7, 3, 1, 4, 5, 1], CYCLE
assert [p for _, _, p in LOG] == [[2, 3, 1], [6, 7, 3], [4, 5, 1]], LOG
assert len(CYCLE) == len(EDGES) + 1


def write(name, text):
    with open(os.path.join(OUT, name), 'w') as fh:
        fh.write(text + "\n")


# turer: (färg, riktade kanter, overlay då turen skapas)
TOURS = [
    ('kthblue', [(1, 2), (2, 3), (3, 1)], 1),
    ('kthgrass', [(3, 6), (6, 7), (7, 3)], 3),
    ('kthorange', [(1, 4), (4, 5), (5, 1)], 5),
]
FINAL_ORDER = {}
for i in range(len(CYCLE) - 1):
    FINAL_ORDER[frozenset((CYCLE[i], CYCLE[i + 1]))] = i + 1
TORTOISE = {2: 2, 3: 3, 4: 3, 5: 1, 6: 1}
NOVL = 6


def graph_walk():
    L = ["\\begin{tikzpicture}[scale=0.92]",
         "  \\useasboundingbox (-2.1,-1.75) rectangle (5.1,1.75);"]
    for v, (x, y) in POS.items():
        L.append(f"  \\node[gv] ({v}) at ({x},{y}) {{{v}}};")
    # grå grundkanter
    for a, b in EDGES:
        L.append(f"  \\draw[faint] ({a}) -- ({b});")
    # turer
    for col, edges, ov in TOURS:
        for a, b in edges:
            L.append(f"  \\draw[->,draw={col},line width=2.2pt,shorten >=1pt,"
                     f"visible on=<{ov}->] ({a}) -- ({b});")
            L.append(f"  \\draw[->,draw={col},line width=3.6pt,opacity=0.35,"
                     f"visible on=<{ov}>] ({a}) -- ({b});")
    # sköldpaddan: grön ring
    for ov, v in TORTOISE.items():
        L.append(f"  \\node[circle,draw=kthgreen,line width=1.6pt,minimum size=8.4mm,"
                 f"visible on=<{ov}>] at ({v}) {{}};")
    # slutlig ordning
    for a, b in EDGES:
        k = FINAL_ORDER[frozenset((a, b))]
        L.append(f"  \\node[circle,fill=white,draw=black!50,inner sep=0.8pt,font=\\scriptsize\\bfseries,"
                 f"visible on=<{NOVL}>] at ($({a})!0.5!({b})$) {{{k}}};")
    L.append("\\end{tikzpicture}")
    return "\n".join(L)


def fmt_list(items, new_from=None, col='kthorange'):
    parts = []
    for i, x in enumerate(items):
        s = str(x)
        if new_from is not None and i >= new_from:
            s = f"\\textcolor{{{col}}}{{\\mathbf{{{x}}}}}"
        parts.append(s)
    return "[" + ",".join(parts) + "]"


def walk_frame():
    cyc_states = [
        ([1], None),
        ([1, 2], 1),
        ([1, 2, 3], 2),
        ([1, 2, 3, 6, 7, 3], 3),
        ([1, 2, 3, 6, 7, 3, 1], 6),
        ([1, 2, 3, 6, 7, 3, 1, 4, 5, 1], 7),
    ]
    steps = [
        r"Märk $(1,2)$. \textbf{Haren} springer längs omärkta kanter: $1\to2\to3\to1$. "
        r"Den fastnar i 1 — starthörnet.",
        r"\textbf{Sköldpaddan} går efter längs stigen. I 2: alla kanter märkta. Gå vidare.",
        r"I 3: omärkta kanter kvar! Skicka ut haren från 3: $3\to6\to7\to3$.",
        r"Sköldpaddan går den nya turen \emph{innan} den fortsätter: 6, 7, 3.",
        r"Tillbaka på första turen. I 1: omärkta kanter. Haren: $1\to4\to5\to1$.",
        r"Sköldpaddan går 4, 5, 1. Klart: $10=|E|+1$ hörn. Siffrorna visar cykelns ordning.",
    ]
    paths = [r"[2,3,1]", r"[2,3,1]", r"[6,7,3]", r"[6,7,3]", r"[4,5,1]", r"[4,5,1]"]
    right = []
    for k in range(NOVL):
        cyc, nf = cyc_states[k]
        right.append(f"\\only<{k + 1}>{{%\n"
                     f"{{\\small\\textbf{{Senaste tur (haren):}}}} ${paths[k]}$\\par\\medskip\n"
                     f"{{\\small\\textbf{{Cykel (sköldpaddan):}}}}\\par\n"
                     f"$\\mathit{{cykel}}={fmt_list(cyc, nf)}$\\par\\medskip\n"
                     f"\\begin{{infobox}}[fontupper=\\footnotesize]{steps[k]}\\end{{infobox}}}}")
    frame = (r"\begin{frame}{Eulercykeln steg för steg}" "\n"
             r"\begin{columns}[T]" "\n"
             r"\begin{column}{0.54\textwidth}" "\n\\centering\n"
             + graph_walk() + "\n"
             r"\par\smallskip{\scriptsize\textcolor{kthblue}{\textbf{tur 1}}\quad"
             r"\textcolor{kthgrass}{\textbf{tur 2}}\quad\textcolor{kthorange}{\textbf{tur 3}}\quad"
             r"\textcolor{kthgreen}{$\bigcirc$ sköldpaddan}}" "\n"
             r"\end{column}" "\n"
             r"\begin{column}{0.43\textwidth}" "\n"
             + "\n".join(right) + "\n"
             r"\end{column}" "\n"
             r"\end{columns}" "\n"
             r"\varstrip{Generalisering}{algoritmen}{var turerna börjar}{att turer skarvas in där sköldpaddan hittar omärkta kanter}" "\n"
             r"\end{frame}")
    write('euler-walk.tex', frame)


def plain_graph(name, scale=0.85, degrees=True):
    deg = {v: sum(1 for e in EDGES if v in e) for v in POS}
    L = [f"\\begin{{tikzpicture}}[scale={scale}]"]
    for v, (x, y) in POS.items():
        L.append(f"  \\node[gv] ({v}) at ({x},{y}) {{{v}}};")
    for a, b in EDGES:
        L.append(f"  \\draw[ge] ({a}) -- ({b});")
    if degrees:
        off = {1: (0, -0.5), 2: (0, 0.5), 3: (0, -0.5), 4: (-0.5, 0), 5: (-0.5, 0), 6: (0.5, 0), 7: (0.5, 0)}
        for v, (dx, dy) in off.items():
            x, y = POS[v]
            L.append(f"  \\node[font=\\scriptsize,text=kthorange] at ({x + dx},{y + dy}) {{{deg[v]}}};")
    L.append("\\end{tikzpicture}")
    write(name, "\n".join(L))


if __name__ == '__main__':
    walk_frame()
    plain_graph('euler-graf.tex')
    print('cykel:', CYCLE)
    print('turer:', LOG)


def hierholzer():
    adj = {v: sorted([b for a, b in EDGES if a == v] + [a for a, b in EDGES if b == v]) for v in POS}
    ptr = {v: 0 for v in POS}
    marked = set()
    S, out = [1], []
    while S:
        u = S[-1]
        while ptr[u] < len(adj[u]) and (min(u, adj[u][ptr[u]]), max(u, adj[u][ptr[u]])) in marked:
            ptr[u] += 1
        if ptr[u] < len(adj[u]):
            v = adj[u][ptr[u]]
            marked.add((min(u, v), max(u, v)))
            S.append(v)
        else:
            out.append(S.pop())
    return out


H = hierholzer()
assert H == [1, 5, 4, 1, 3, 7, 6, 3, 2, 1], H
assert H[::-1] == CYCLE
print('hierholzer:', H)
