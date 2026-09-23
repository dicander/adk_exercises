# -*- coding: utf-8 -*-
"""Genererar TikZ för uppgift 1 (Kruskal/Prim-genomgångar m.m.)."""
import os
OUT = 'gen'
os.makedirs(OUT, exist_ok=True)

POS = {'a': (3.1, 5.2), 'b': (2.1, 4.2), 'c': (4.3, 4.1), 'd': (1.0, 3.1), 'e': (3.1, 3.1),
       'f': (4.7, 2.1), 'g': (1.0, 1.0), 'h': (3.1, 1.0), 'i': (0.0, 0.0)}
EDGES = [('a', 'c', 1, 'above right'), ('b', 'e', 2, 'above right'), ('e', 'h', 3, 'left'),
         ('g', 'h', 4, 'below'), ('b', 'd', 5, 'above left'), ('d', 'g', 6, 'right'),
         ('a', 'g', 7, 'left'), ('g', 'i', 8, 'above left'), ('a', 'b', 9, 'above left'),
         ('e', 'f', 10, 'above right')]
W = {frozenset((u, v)): w for u, v, w, _ in EDGES}
VERT = sorted(POS)


def key(u, v):
    return frozenset((u, v))


def edge_path(u, v, label, pos, lab_style='gw'):
    if {u, v} == {'a', 'g'}:
        return (f"(a) .. controls (-0.2,5.4) and (-0.4,1.3) .. "
                f"node[{lab_style},{pos},pos=0.5]{{{label}}} (g)")
    return f"({u}) -- node[{lab_style},{pos}]{{{label}}} ({v})"


def edge_only_path(u, v):
    if {u, v} == {'a', 'g'}:
        return "(a) .. controls (-0.2,5.4) and (-0.4,1.3) .. (g)"
    return f"({u}) -- ({v})"


def ranges(states, default):
    """Komprimera en lista av tillstånd (overlay 1..N) till (spec, tillstånd)."""
    out = []
    n = len(states)
    start = 0
    for k in range(1, n + 1):
        if k == n or states[k] != states[start]:
            s = states[start]
            a, b = start + 1, k
            if s != default:
                if b == n:
                    spec = f"{a}-"
                elif a == b:
                    spec = f"{a}"
                else:
                    spec = f"{a}-{b}"
                out.append((spec, s))
            start = k
    return out


def opts(states, default):
    return ",".join(f"onslide=<{sp}>{{{st}}}" for sp, st in ranges(states, default))


def nodes(vstyle=None, scale_font=None):
    """vstyle: dict v -> extra style string (statisk) eller lista per overlay."""
    lines = []
    for v in VERT:
        x, y = POS[v]
        st = ''
        if vstyle and v in vstyle:
            s = vstyle[v]
            st = s if isinstance(s, str) else opts(s, '')
        lines.append(f"  \\node[gv{(',' + st) if st else ''}] ({v}) at ({x},{y}) {{${v}$}};")
    return "\n".join(lines)


def static_pic(estyle=None, vstyle=None, scale=0.8, labels=None, extra='', glow=None,
               lab_style='gw', font=None):
    """estyle: dict frozenset->style; labels: dict frozenset->text."""
    estyle = estyle or {}
    labels = labels or {}
    L = [f"\\begin{{tikzpicture}}[scale={scale}{(',every node/.append style={font=' + font + '}') if font else ''}]"]
    L.append(nodes(vstyle))
    L.append("  \\begin{scope}[on background layer]")
    if glow:
        for (u, v) in glow:
            L.append(f"  \\draw[kthorange!55,line width=7pt,line cap=round] {edge_only_path(u, v)};")
    for u, v, w, pos in EDGES:
        st = estyle.get(key(u, v), 'ge')
        lab = labels.get(key(u, v), str(w))
        L.append(f"  \\draw[{st}] {edge_path(u, v, lab, pos, lab_style)};")
    L.append("  \\end{scope}")
    if extra:
        L.append(extra)
    L.append("\\end{tikzpicture}")
    return "\n".join(L)


def write(name, text):
    with open(os.path.join(OUT, name), 'w') as f:
        f.write(text + "\n")


# ----------------------------------------------------------------------
#  KRUSKAL
# ----------------------------------------------------------------------
def kruskal_frames():
    order = sorted(EDGES, key=lambda e: e[2])
    parent = {v: v for v in VERT}
    size = {v: 1 for v in VERT}
    color = {}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    N = len(order) + 1
    est = {key(u, v): ['ge'] * N for u, v, _, _ in EDGES}
    vst = {v: [''] * N for v in VERT}
    acc = {}
    ncomp = [9]
    weight = [0]
    ntree = [0]
    snapshots = []  # per overlay: (comp count, tree weight, #edges)
    snapshots.append((9, 0, 0))
    next_color = iter(['comp1', 'comp2', 'comp3'])
    tree_adj = {v: [] for v in VERT}
    cycles = {}

    def tree_path(s, t):
        prev = {s: None}
        stack = [s]
        while stack:
            x = stack.pop()
            for y in tree_adj[x]:
                if y not in prev:
                    prev[y] = x
                    stack.append(y)
        p = []
        x = t
        while prev[x] is not None:
            p.append((prev[x], x))
            x = prev[x]
        return p

    for idx, (u, v, w, _) in enumerate(order):
        ov = idx + 2  # overlay där kanten prövas
        ru, rv = find(u), find(v)
        ok = ru != rv
        acc[key(u, v)] = ok
        if ok:
            # union by size, färg: den större behåller sin färg
            cu, cv = color.get(ru), color.get(rv)
            if size[ru] < size[rv]:
                ru, rv = rv, ru
                cu, cv = cv, cu
            parent[rv] = ru
            size[ru] += size[rv]
            color[ru] = cu or cv or next(next_color)
            tree_adj[u].append(v)
            tree_adj[v].append(u)
            weight[0] += w
            ntree[0] += 1
            ncomp[0] -= 1
        else:
            cycles[ov] = tree_path(u, v)
        # kant-tillstånd
        for k in range(ov - 1, N):
            o = k + 1
            if o == ov:
                est[key(u, v)][k] = 'nyss' if ok else 'rejnu'
            elif o > ov:
                est[key(u, v)][k] = 'mst' if ok else 'rej'
        # hörnfärger vid denna overlay
        for x in VERT:
            r = find(x)
            c = color.get(r, '') if size[r] > 1 else ''
            for k in range(ov - 1, N):
                vst[x][k] = c
        snapshots.append((ncomp[0], weight[0], ntree[0]))

    # --- graf
    L = ["\\begin{tikzpicture}[scale=0.76]"]
    L.append(nodes(vst))
    L.append("  \\begin{scope}[on background layer]")
    for ov, path in cycles.items():
        for (x, y) in path:
            L.append(f"  \\draw[kthorange!55,line width=7pt,line cap=round,visible on=<{ov}>] "
                     f"{edge_only_path(x, y)};")
    for u, v, w, pos in EDGES:
        o = opts(est[key(u, v)], 'ge')
        L.append(f"  \\draw[ge{(',' + o) if o else ''}] {edge_path(u, v, str(w), pos)};")
    L.append("  \\end{scope}")
    L.append("\\end{tikzpicture}")
    graph = "\n".join(L)

    # --- kantlista
    T = ["\\begin{tikzpicture}[x=1cm,y=-0.40cm,font=\\small]"]
    T.append("  \\node[anchor=west,font=\\footnotesize\\bfseries,text=kthnavy] at (-0.35,-0.9) "
             "{Alla kanter, globalt sorterade};")
    for idx, (u, v, w, _) in enumerate(order):
        ov = idx + 2
        y = idx
        ok = acc[key(u, v)]
        T.append(f"  \\fill[kthorange!22,visible on=<{ov}>] (-0.35,{y}-0.45) rectangle (5.6,{y}+0.45);")
        T.append(f"  \\node[visible on=<{ov}>,text=kthorange] at (-0.18,{y}) {{$\\blacktriangleright$}};")
        T.append(f"  \\node[anchor=east] at (0.55,{y}) {{{w}}};")
        T.append(f"  \\node[anchor=west] at (0.75,{y}) {{${u}$--${v}$}};")
        if ok:
            T.append(f"  \\node[anchor=west,visible on=<{ov}->] at (1.75,{y}) {{\\ja}};")
        else:
            T.append(f"  \\node[anchor=west,visible on=<{ov}->,font=\\scriptsize,text=brick] at (1.75,{y}) "
                     f"{{\\nej\\ samma komponent $\\Rightarrow$ cykel}};")
    T.append("\\end{tikzpicture}")
    table = "\n".join(T)

    caps = {
        1: "Sortera \\emph{alla} kanter. Varje hörn är en egen komponent.",
        2: "$a$--$c$ förbinder två olika komponenter $\\Rightarrow$ ta den.",
        3: "$b$--$e$: på andra sidan grafen. Kruskal bryr sig inte om \\emph{var} kanten är "
           "— bara att den är billigast \\emph{globalt}.",
        4: "$e$--$h$ $\\Rightarrow$ ta den.",
        5: "$g$--$h$ $\\Rightarrow$ ta den.",
        6: "$b$--$d$ $\\Rightarrow$ ta den.",
        7: "$d$--$g$: $d$ och $g$ hänger redan ihop via $d$--$b$--$e$--$h$--$g$. Kanten skulle sluta en cykel.",
        8: "$a$--$g$ förenar $\\{a,c\\}$ med den stora komponenten.",
        9: "$g$--$i$ $\\Rightarrow$ ta den.",
        10: "$a$--$b$: redan förbundna via $a$--$g$--$h$--$e$--$b$ $\\Rightarrow$ cykel.",
        11: "$e$--$f$ $\\Rightarrow$ ta den. $|V|-1=8$ kanter, vikt $40$. Klart.",
    }
    stat = []
    for ov in range(1, N + 1):
        nc, wt, ne = snapshots[ov - 1]
        stat.append(f"\\only<{ov}>{{Komponenter: {nc}\\quad Kanter i $T$: {ne}\\quad Vikt: {wt}}}")
    capt = "".join(f"\\only<{k}>{{{t}}}" for k, t in caps.items())

    frame = r"""\begin{frame}{Kruskal på uppgiftens graf}
\begin{columns}[T]
\begin{column}{0.47\textwidth}
\centering
%GRAPH%
\end{column}
\begin{column}{0.5\textwidth}
%TABLE%

\vskip2pt
{\footnotesize\color{kthblue}%STAT%}
\end{column}
\end{columns}
\vfill
\begin{tcolorbox}[enhanced,colback=kthlight!50,colframe=kthsky,boxrule=0.4pt,arc=2pt,
  left=4pt,right=4pt,top=1pt,bottom=1pt,fontupper=\small,height=0.95cm,valign=center]
%CAPT%
\end{tcolorbox}
\end{frame}"""
    frame = (frame.replace('%GRAPH%', graph).replace('%TABLE%', table)
             .replace('%STAT%', "".join(stat)).replace('%CAPT%', capt))
    write('kruskal.tex', frame)


# ----------------------------------------------------------------------
#  PRIM
# ----------------------------------------------------------------------
def prim_frames(root='a'):
    adj = {v: [] for v in VERT}
    for u, v, w, _ in EDGES:
        adj[u].append((v, w))
        adj[v].append((u, w))
    INF = float('inf')
    keyv = {v: INF for v in VERT}
    par = {v: None for v in VERT}
    keyv[root] = 0
    intree = set()
    states = []  # per overlay: dict
    # overlay 1: init
    states.append(dict(key=dict(keyv), par=dict(par), intree=set(intree), just=None, dec={}, new=set()))
    order = []
    while len(intree) < len(VERT):
        u = min((x for x in VERT if x not in intree), key=lambda x: (keyv[x], x))
        intree.add(u)
        order.append(u)
        dec = {}
        new = set()
        for v, w in sorted(adj[u]):
            if v not in intree and w < keyv[v]:
                if keyv[v] < INF:
                    dec[v] = (keyv[v], w)
                else:
                    new.add(v)
                keyv[v] = w
                par[v] = u
        states.append(dict(key=dict(keyv), par=dict(par), intree=set(intree), just=u, dec=dec, new=new))
    N = len(states)
    est = {key(u, v): [] for u, v, _, _ in EDGES}
    vst = {v: [] for v in VERT}
    for s in states:
        for u, v, w, _ in EDGES:
            k = key(u, v)
            iu, iv = u in s['intree'], v in s['intree']
            tree_edge = (iv and s['par'][v] == u) or (iu and s['par'][u] == v)
            just_edge = s['just'] is not None and s['par'][s['just']] is not None and \
                k == key(s['just'], s['par'][s['just']])
            if iu and iv:
                st = ('nyss' if just_edge else 'mst') if tree_edge else 'faint'
            elif iu or iv:
                x = v if iu else u  # hörnet utanför trädet
                y = u if iu else v
                st = 'cand' if s['par'][x] == y else 'faint'
            else:
                st = 'ge'
            est[k].append(st)
        for v in VERT:
            if v in s['intree']:
                vst[v].append('intree')
            elif s['key'][v] < INF:
                vst[v].append('draw=kthorange,line width=1.1pt')
            else:
                vst[v].append('')

    def fmt(x):
        return '\\infty' if x == INF else str(x)

    # nyckel-etiketter
    lab_anchor = {'a': 'north west', 'b': 'south east', 'c': 'south west', 'd': 'south east',
                  'e': 'south west', 'f': 'south west', 'g': 'north west', 'h': 'north west',
                  'i': 'north west'}
    lab_dir = {'a': 'above left', 'b': 'above left', 'c': 'above right', 'd': 'above left',
               'e': 'above right', 'f': 'above right', 'g': 'below right', 'h': 'below right',
               'i': 'below right'}
    L = ["\\begin{tikzpicture}[scale=0.76]"]
    L.append(nodes(vst))
    L.append("  \\begin{scope}[on background layer]")
    for u, v, w, pos in EDGES:
        o = opts(est[key(u, v)], 'ge')
        L.append(f"  \\draw[ge{(',' + o) if o else ''}] {edge_path(u, v, str(w), pos)};")
    L.append("  \\end{scope}")
    L.append("\\end{tikzpicture}")
    graph = "\n".join(L)

    # prioritetskö-tabell
    blocks = []
    for k, s in enumerate(states):
        ov = k + 1
        q = sorted([(s['key'][v], v) for v in VERT if v not in s['intree'] and s['key'][v] < INF])
        rows = []
        for kv, v in q:
            p = s['par'][v]
            mark = ''
            if v in s['dec']:
                mark = f"\\ \\textcolor{{brick}}{{(var {s['dec'][v][0]})}}"
            elif v in s['new']:
                mark = "\\ \\textcolor{kthgrass}{(ny)}"
            rows.append(f"${v}$ & ${kv}$ & {('$' + p + '$') if p else '--'}{mark}\\\\")
        ninf = sum(1 for v in VERT if v not in s['intree'] and s['key'][v] == INF)
        if not rows:
            rows.append("\\multicolumn{3}{@{}l}{\\color{black!50}(tom)}\\\\")
        infrow = f"\\multicolumn{{3}}{{@{{}}l}}{{\\color{{black!50}}+ {ninf} hörn med nyckel $\\infty$}}\\\\" if ninf else ""
        tree = ", ".join(f"${x}$" for x in order[:k])
        blocks.append(f"\\only<{ov}>{{%\n\\begin{{tabular}}{{@{{}}l@{{\\quad}}r@{{\\quad}}l@{{}}}}\n"
                      f"\\toprule hörn & key & $\\pi$\\\\\\midrule\n" + "\n".join(rows) + "\n" + infrow +
                      f"\n\\bottomrule\n\\end{{tabular}}\\par\\smallskip\n"
                      f"{{\\scriptsize\\color{{kthblue}}Utplockade: {tree if tree else '--'}}}}}")
    pq = "\n".join(blocks)

    caps = {
        1: "Starta i $a$: $\\mathit{key}[a]=0$, alla andra $\\infty$. Alla hörn ligger i kön.",
        2: "Plocka ut $a$. Grannarna får nycklar: $c$ (1), $g$ (7), $b$ (9).",
        3: "Plocka ut $c$ (1). Inga nya grannar. Kön är lokal: bara kanter \\emph{ut ur trädet} räknas.",
        4: "Plocka ut $g$ (7). Nya nycklar: $h$ (4), $d$ (6), $i$ (8).",
        5: "Plocka ut $h$ (4). Ny nyckel: $e$ (3).",
        6: "Plocka ut $e$ (3). \\textsc{Decrease-Key}: $b$ går från 9 till 2. Ny: $f$ (10).",
        7: "Plocka ut $b$ (2). \\textsc{Decrease-Key}: $d$ går från 6 till 5.",
        8: "Plocka ut $d$ (5). Kanten $d$--$g$ (6) blev aldrig trädkant.",
        9: "Plocka ut $i$ (8).",
        10: "Plocka ut $f$ (10). Vikt $1+7+4+3+2+5+8+10=40$. Samma träd som Kruskal (unika vikter!).",
    }
    capt = "".join(f"\\only<{k}>{{{t}}}" for k, t in caps.items())
    frame = r"""\begin{frame}{Prim på uppgiftens graf (rot $a$)}
\begin{columns}[T]
\begin{column}{0.47\textwidth}
\centering
%GRAPH%
\end{column}
\begin{column}{0.5\textwidth}
{\footnotesize\bfseries\color{kthnavy}Prioritetskö $Q$ (nyckel = billigaste kant in i trädet)}\par\smallskip
\footnotesize
%PQ%
\end{column}
\end{columns}
\vfill
\begin{tcolorbox}[enhanced,colback=kthlight!50,colframe=kthsky,boxrule=0.4pt,arc=2pt,
  left=4pt,right=4pt,top=1pt,bottom=1pt,fontupper=\small,height=0.95cm,valign=center]
%CAPT%
\end{tcolorbox}
\end{frame}"""
    frame = frame.replace('%GRAPH%', graph).replace('%PQ%', pq).replace('%CAPT%', capt)
    write('prim.tex', frame)
    return order


# ----------------------------------------------------------------------
#  STATISKA BILDER
# ----------------------------------------------------------------------
MST = {key(u, v) for u, v in [('a', 'c'), ('b', 'e'), ('e', 'h'), ('g', 'h'), ('b', 'd'),
                              ('a', 'g'), ('g', 'i'), ('e', 'f')]}


def statics():
    # uppgiftsgrafen, ren
    write('graf-ren.tex', static_pic(scale=0.78))
    # MST-facit
    write('graf-mst.tex', static_pic({k: 'mst' for k in MST}, scale=0.78))

    # KruskAL GlobAL vs Prim lokal: tillstånd efter första kanten
    kr_style = {k: 'cand' for k in W}
    kr_style[key('a', 'c')] = 'mst'
    kr_style[key('b', 'e')] = 'nyss'
    kr_v = {'a': 'comp1', 'c': 'comp1'}
    write('globlok-kruskal.tex', static_pic(kr_style, kr_v, scale=0.56, font='\\footnotesize'))
    pr_style = {k: 'faint' for k in W}
    pr_style[key('a', 'c')] = 'mst'
    pr_style[key('a', 'b')] = 'cand'
    pr_style[key('a', 'g')] = 'nyss'
    pr_v = {'a': 'intree', 'c': 'intree'}
    write('globlok-prim.tex', static_pic(pr_style, pr_v, scale=0.56, font='\\footnotesize'))

    # Girig promenad: a -> c och sedan stopp
    gw_style = {k: 'faint' for k in W}
    gw_style[key('a', 'c')] = 'nyss'
    extra = ("  \\node[font=\\scriptsize\\bfseries,text=brick,right=3pt of c,align=left] "
             "{Stannar i $c$.\\\\(Inga fler kanter.)};\n"
             "  \\node[font=\\scriptsize,text=kthorange,above right=1pt and 1pt of a] {start};")
    write('girig.tex', static_pic(gw_style, {'a': 'intree', 'c': 'intree'}, scale=0.6,
                                  extra=extra, font='\\footnotesize'))

    # MST vs kortaste-vägträd från a
    spt = {key(u, v) for u, v in [('a', 'c'), ('a', 'g'), ('a', 'b'), ('g', 'h'), ('b', 'e'),
                                  ('g', 'd'), ('g', 'i'), ('e', 'f')]}
    write('kontrast-mst.tex', static_pic({k: ('mst' if k in MST else 'faint') for k in W},
                                         {'a': 'intree'}, scale=0.56, font='\\footnotesize'))
    dist = {'a': 0, 'b': 9, 'c': 1, 'd': 13, 'e': 11, 'f': 21, 'g': 7, 'h': 11, 'i': 15}
    ddir = {'a': 'above left', 'b': 'above left', 'c': 'above right', 'd': 'left', 'e': 'above right',
            'f': 'below', 'g': 'below right', 'h': 'below right', 'i': 'below right'}
    extra = "\n".join(f"  \\node[font=\\scriptsize\\bfseries,text=plum,inner sep=0.5pt,{ddir[v]}=1pt of {v}] {{{d}}};"
                      for v, d in dist.items() if v != 'a')
    write('kontrast-spt.tex', static_pic({k: ('draw=plum,line width=2.6pt' if k in spt else 'faint') for k in W},
                                         {'a': 'intree'}, scale=0.56, font='\\footnotesize'))

    # Snittegenskapen: S = {d,g,i}
    cut_style = {k: 'faint' for k in W}
    for k in [key('b', 'd'), key('a', 'g')]:
        cut_style[k] = 'cand'
    cut_style[key('g', 'h')] = 'nyss'
    cut_style[key('d', 'g')] = 'ge'
    cut_style[key('g', 'i')] = 'ge'
    extra = ("  \\begin{scope}[on background layer]\n"
             "  \\fill[plum!15,rounded corners=10pt] (-0.55,-0.5) -- (1.55,0.6) -- (1.6,3.6) -- (0.55,3.75) -- (-0.55,1.5) -- cycle;\n"
             "  \\end{scope}\n"
             "  \\node[font=\\scriptsize\\bfseries,text=plum] at (0.55,4.1) {$S$};")
    write('snitt.tex', static_pic(cut_style, None, scale=0.56, extra=extra, font='\\footnotesize'))
    cyc_style = {k: 'faint' for k in W}
    for k in [key('b', 'd'), key('g', 'h'), key('e', 'h'), key('b', 'e')]:
        cyc_style[k] = 'draw=kthgrass,line width=2pt'
    cyc_style[key('d', 'g')] = 'rejnu'
    write('cykel.tex', static_pic(cyc_style, None, scale=0.56, font='\\footnotesize'))

    # Borůvka runda 1 och 2
    r1 = {key(u, v) for u, v in [('a', 'c'), ('b', 'e'), ('e', 'h'), ('g', 'h'), ('b', 'd'),
                                 ('g', 'i'), ('e', 'f')]}
    b1 = {k: ('mst' if k in r1 else 'ge') for k in W}
    v1 = {v: 'comp1' for v in 'ac'}
    v1.update({v: 'comp2' for v in 'bdefghi'})
    write('boruvka1.tex', static_pic(b1, v1, scale=0.56, font='\\footnotesize'))
    b2 = {k: ('mst' if k in r1 else 'faint') for k in W}
    b2[key('a', 'g')] = 'nyss'
    b2[key('a', 'b')] = 'cand'
    write('boruvka2.tex', static_pic(b2, {v: 'comp2' for v in VERT}, scale=0.56, font='\\footnotesize'))

    # Skog vs träd efter fyra kanter
    kf = {k: 'ge' for k in W}
    for k in [key('a', 'c'), key('b', 'e'), key('e', 'h'), key('g', 'h')]:
        kf[k] = 'mst'
    kfv = {'a': 'comp1', 'c': 'comp1', 'b': 'comp2', 'e': 'comp2', 'h': 'comp2', 'g': 'comp2'}
    write('skog.tex', static_pic(kf, kfv, scale=0.56, font='\\footnotesize'))
    pf = {k: 'ge' for k in W}
    for k in [key('a', 'c'), key('a', 'g'), key('g', 'h'), key('e', 'h')]:
        pf[k] = 'mst'
    pfv = {v: 'intree' for v in 'acghe'}
    write('trad.tex', static_pic(pf, pfv, scale=0.56, font='\\footnotesize'))

    # Lika vikter: d--g = 5 ger två MST
    tie_lab = {key('d', 'g'): '\\textbf{\\textcolor{brick}{5}}'}
    t1 = {k: ('mst' if k in MST else 'faint') for k in W}
    t1[key('d', 'g')] = 'faint'
    write('tie1.tex', static_pic(t1, None, scale=0.5, labels=tie_lab, font='\\footnotesize'))
    t2 = dict(t1)
    t2[key('b', 'd')] = 'faint'
    t2[key('d', 'g')] = 'mst'
    write('tie2.tex', static_pic(t2, None, scale=0.5, labels=tie_lab, font='\\footnotesize'))

    # Viktbyte 5 <-> 6: MST ändras
    sw_lab = {key('b', 'd'): '\\textbf{\\textcolor{brick}{6}}', key('d', 'g'): '\\textbf{\\textcolor{brick}{5}}'}
    sw = {k: ('mst' if k in MST else 'faint') for k in W}
    sw[key('b', 'd')] = 'faint'
    sw[key('d', 'g')] = 'mst'
    write('swap.tex', static_pic(sw, None, scale=0.5, labels=sw_lab, font='\\footnotesize'))
    # kvadrerade vikter: SPT ändras (b hänger på e)
    sq_lab = {k: str(w * w) for k, w in W.items()}
    spt2 = {key(u, v) for u, v in [('a', 'c'), ('a', 'g'), ('e', 'b'), ('g', 'h'), ('g', 'd'),
                                   ('g', 'i'), ('h', 'e'), ('e', 'f')]}
    write('sq-spt.tex', static_pic({k: ('draw=plum,line width=2.6pt' if k in spt2 else 'faint') for k in W},
                                   {'a': 'intree'}, scale=0.46, labels=sq_lab, font='\\footnotesize'))


if __name__ == '__main__':
    kruskal_frames()
    order = prim_frames()
    print('Prim order', order)
    statics()
    print('ok')
