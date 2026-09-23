# -*- coding: utf-8 -*-
"""Genererar TikZ för uppgift 2 (flöden)."""
import os
OUT = 'gen'
os.makedirs(OUT, exist_ok=True)

POS = {'s': (0, 1.4), 'a': (2.6, 2.8), 'b': (1.6, 0), 'c': (3.9, 0), 't': (5.4, 1.4)}
EDG = [('s', 'a', 3), ('s', 'b', 6), ('b', 'a', 1), ('a', 't', 1), ('a', 'c', 2), ('b', 'c', 5), ('c', 't', 7)]
CAP = {(u, v): c for u, v, c in EDG}
ORDER = [(u, v) for u, v, _ in EDG]


def F(sa, sb, ba, at, ac, bc, ct):
    return dict(zip(ORDER, [sa, sb, ba, at, ac, bc, ct]))


S0 = F(0, 0, 0, 0, 0, 0, 0)
S1 = F(2, 0, 0, 0, 2, 0, 2)
S2 = F(2, 1, 0, 1, 1, 1, 2)
S3 = F(2, 5, 0, 1, 1, 5, 6)
S4 = F(2, 6, 1, 1, 2, 5, 7)          # f2
FSTAR = F(3, 5, 0, 1, 2, 5, 7)       # f*

BBOX = "\\useasboundingbox (-0.45,-0.5) rectangle (5.85,3.3);"


def val(f):
    return f[('s', 'a')] + f[('s', 'b')]


def check(f, cap=CAP):
    for e in ORDER:
        assert 0 <= f[e] <= cap[e], (e, f[e], cap[e])
    for x in 'abc':
        inn = sum(f[e] for e in ORDER if e[1] == x)
        out = sum(f[e] for e in ORDER if e[0] == x)
        assert inn == out, (x, inn, out)


for f in (S0, S1, S2, S3, S4, FSTAR):
    check(f)


def hull(points):
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def reach_blob(reach, label=None):
    pts = hull([POS[v] for v in reach])
    path = " -- ".join(f"({x},{y})" for x, y in pts) + " -- cycle"
    L = ["  \\begin{scope}[on background layer]",
         f"  \\filldraw[plum!13,line width=0.8cm,line join=round] {path};",
         "  \\end{scope}"]
    if label:
        L.append(label)
    return "\n".join(L)


def nodes(extra_node_style=None):
    extra_node_style = extra_node_style or {}
    L = []
    for v, (x, y) in POS.items():
        st = extra_node_style.get(v, '')
        L.append(f"  \\node[fn{(',' + st) if st else ''}] ({v}) at ({x},{y}) {{${v}$}};")
    return "\n".join(L)


def net_pic(f, cap=None, scale=0.95, estyle=None, lab=None, extra='', nstyle=None, satmark=True,
            bbox=True):
    cap = cap or CAP
    estyle = estyle or {}
    lab = lab or {}
    L = [f"\\begin{{tikzpicture}}[scale={scale}]"]
    if bbox:
        L.append(BBOX)
    L.append(nodes(nstyle))
    for e in ORDER:
        u, v = e
        st = estyle.get(e)
        if st is None:
            st = 'sat' if (satmark and f[e] == cap[e] and cap[e] > 0) else 'fe'
        text = lab.get(e, f"{f[e]}/{cap[e]}")
        L.append(f"  \\draw[{st}] ({u}) -- node[fl] {{{text}}} ({v});")
    if extra:
        L.append(extra)
    L.append("\\end{tikzpicture}")
    return "\n".join(L)


def res_pic(f, cap=None, path=None, reach=None, scale=0.95, extra='', nstyle=None, bbox=True,
            dim=None, reach_label=None):
    """path: lista av riktade restkanter (x,y) att markera."""
    cap = cap or CAP
    path = set(path or [])
    dim = set(dim or [])
    L = [f"\\begin{{tikzpicture}}[scale={scale}]"]
    if bbox:
        L.append(BBOX)
    L.append(nodes(nstyle))
    if reach:
        L.append(reach_blob(reach, label=reach_label))
    for e in ORDER:
        u, v = e
        fwd = cap[e] - f[e]
        bwd = f[e]
        both = fwd > 0 and bwd > 0
        for (x, y, amt, base) in ((u, v, fwd, 'res'), (v, u, bwd, 'resb')):
            if amt <= 0:
                continue
            st = base
            if (x, y) in path:
                st = 'aug'
            if (x, y) in dim:
                st += ',opacity=0.3'
            bend = ",bend left=20" if both else ""
            lst = 'fl' if (x, y) not in path else 'fl,text=kthgrass,font=\\scriptsize\\bfseries'
            L.append(f"  \\draw[{st}] ({x}) to[{bend.lstrip(',')}] node[{lst}] {{{amt}}} ({y});"
                     if both else
                     f"  \\draw[{st}] ({x}) -- node[{lst}] {{{amt}}} ({y});")
    if extra:
        L.append(extra)
    L.append("\\end{tikzpicture}")
    return "\n".join(L)


def write(name, text):
    with open(os.path.join(OUT, name), 'w') as fh:
        fh.write(text + "\n")


def pathedges(seq):
    return [(seq[i], seq[i + 1]) for i in range(len(seq) - 1)]


# ----------------------------------------------------------------------
#  Ford–Fulkerson-genomgång
# ----------------------------------------------------------------------
def ff_walk():
    states = [S0, S1, S2, S3, S4]
    paths = [pathedges('sact'), pathedges('sbcat'), pathedges('sbct'), pathedges('sbact'), None]
    caps = [
        "Inget flöde än: restgrafen är bara kapaciteterna. Välj en stig, vilken som helst: $s\\to a\\to c\\to t$, flaskhals $\\min(3,2,7)=2$.",
        "$|f|=2$. Bakåtkanten $c\\to a$ (orange) betyder ”ångra flöde på $a\\to c$”. "
        "Stig $s\\to b\\to c\\to a\\to t$ använder den: $+1$.",
        "$|f|=3$. Stig $s\\to b\\to c\\to t$, flaskhals $\\min(5,4,5)=4$.",
        "$|f|=7$. Stig $s\\to b\\to a\\to c\\to t$, flaskhals 1.",
        "$|f|=8$. Ingen stig $s\\leadsto t$ i $G_f$. Nåbara från $s$: $\\{s,a,b\\}$ — ett minsnitt med kapacitet $1+2+5=8$.",
    ]
    left, right, capt = [], [], []
    for k, (S, P) in enumerate(zip(states, paths), start=1):
        netst = {}
        if P:
            for (x, y) in P:
                pass
        left.append(f"\\only<{k}>{{%\n{net_pic(S)}}}")
        reach = ['s', 'a', 'b'] if P is None else None
        right.append(f"\\only<{k}>{{%\n{res_pic(S, path=P, reach=reach)}}}")
        capt.append(f"\\only<{k}>{{{caps[k - 1]}}}")
    frame = r"""\begin{frame}{Repetition: Ford--Fulkerson på exempelnätet}
\begin{columns}[T]
\begin{column}{0.49\textwidth}
\centering
{\small\bfseries\color{kthnavy}Flöde $f$}\ {\scriptsize(flöde/kapacitet, \textcolor{brick}{röd} = mättad)}\par\smallskip
%LEFT%
\end{column}
\begin{column}{0.49\textwidth}
\centering
{\small\bfseries\color{kthnavy}Restflödesgraf $G_f$}\ {\scriptsize(\textcolor{kthblue}{kvar}, \textcolor{kthorange}{ångra})}\par\smallskip
%RIGHT%
\end{column}
\end{columns}
\vfill
\begin{tcolorbox}[enhanced,halign=left,colback=kthlight!50,colframe=kthsky,boxrule=0.4pt,arc=2pt,
  left=4pt,right=4pt,top=1pt,bottom=1pt,fontupper=\small,height=1.05cm,valign=center]
%CAPT%
\end{tcolorbox}
\end{frame}"""
    frame = (frame.replace('%LEFT%', "\n".join(left)).replace('%RIGHT%', "\n".join(right))
             .replace('%CAPT%', "".join(capt)))
    write('ff-walk.tex', frame)


# ----------------------------------------------------------------------
#  Statiska bilder
# ----------------------------------------------------------------------
def statics():
    SC = 0.72
    # minsnitt: slutflödet med båda minsnitten
    C1 = "plot[smooth,tension=0.7] coordinates {(3.3,3.35) (2.95,2.2) (2.9,1.3) (3.3,0.1) (3.35,-0.5)}"
    cuts = ("  \\draw[cutline] " + C1 + ";\n"
            "  \\node[below,font=\\scriptsize\\bfseries,text=plum] at (3.35,-0.5) {$C_1$};\n"
            "  \\draw[cutline] (4.98,3.3) -- (4.98,-0.5) node[below,font=\\scriptsize\\bfseries,text=plum] {$C_2$};")
    write('minsnitt.tex', net_pic(S4, extra=cuts, scale=0.85, bbox=False))
    write('minsnitt-s.tex', net_pic(S4, extra=cuts, scale=0.8, bbox=False))
    # två olika maxflöden
    write('f2.tex', net_pic(S4, scale=0.66))
    write('fstar.tex', net_pic(FSTAR, scale=0.66))

    # 2a: a->t ökar till 2
    cap_at = dict(CAP)
    cap_at[('a', 't')] = 2
    write('2a-net.tex', net_pic(S4, cap=cap_at, scale=SC,
                                estyle={('a', 't'): '->,draw=kthgrass,line width=1.6pt'},
                                lab={('a', 't'): '\\textbf{1/2}'}))
    write('2a-res.tex', res_pic(S4, cap=cap_at, path=pathedges('sat'), scale=SC))
    f9 = dict(S4)
    f9[('s', 'a')] = 3
    f9[('a', 't')] = 2
    check(f9, cap_at)
    write('2a-ny.tex', net_pic(f9, cap=cap_at, scale=SC))
    # 2a: a->c ökar till 3 — hjälper inte
    cap_ac = dict(CAP)
    cap_ac[('a', 'c')] = 3
    write('2a-ac-net.tex', net_pic(S4, cap=cap_ac, scale=SC,
                                   estyle={('a', 'c'): '->,draw=kthgrass,line width=1.6pt'},
                                   lab={('a', 'c'): '\\textbf{2/3}'}))
    write('2a-res-ac.tex', res_pic(S4, cap=cap_ac, reach=['s', 'a', 'b', 'c'], scale=SC,
                                   extra="  \\node[font=\\scriptsize\\bfseries,text=brick] at (5.2,2.1) {ej nådd};"))

    # 2b fall 2: b->a minskar till 0: omdirigera b->s->a
    cap_ba = dict(CAP)
    cap_ba[('b', 'a')] = 0
    g = dict(S4)
    g[('b', 'a')] = 0            # obalans: b +1, a -1
    imb = ("  \\node[font=\\scriptsize\\bfseries,text=brick,left=1pt of b] {$+1$};\n"
           "  \\node[font=\\scriptsize\\bfseries,text=brick] at (2.05,3.05) {$-1$};")
    write('2b-ba-net.tex', net_pic(g, cap=cap_ba, scale=SC, extra=imb, satmark=True,
                                   estyle={('b', 'a'): '->,draw=black!25,dashed'},
                                   lab={('b', 'a'): '0/0'}))
    write('2b-ba-res.tex', res_pic(g, cap=cap_ba, path=pathedges('bsa'), scale=SC))
    write('2b-ba-ny.tex', net_pic(FSTAR, cap=cap_ba, scale=SC,
                                  estyle={('b', 'a'): '->,draw=black!25,dashed'}, lab={('b', 'a'): '0/0'}))

    # 2b fall 3: a->c minskar till 1: ingen stig a~>c; tryck tillbaka a->s och t->c
    cap_ac1 = dict(CAP)
    cap_ac1[('a', 'c')] = 1
    h = dict(S4)
    h[('a', 'c')] = 1           # obalans: a +1, c -1
    imb2 = ("  \\node[font=\\scriptsize\\bfseries,text=brick] at (2.05,3.05) {$+1$};\n"
            "  \\node[font=\\scriptsize\\bfseries,text=brick] at (4.45,-0.25) {$-1$};")
    write('2b-ac-net.tex', net_pic(h, cap=cap_ac1, scale=SC, extra=imb2))
    reach_a = ['s', 'a', 'b']
    write('2b-ac-res.tex', res_pic(h, cap=cap_ac1, path=pathedges('as') + pathedges('tc'), reach=reach_a,
                                   scale=SC))
    labA = "  \\node[font=\\small\\bfseries,text=plum] at (0.35,0.1) {$A$};"
    write('2b-ac-A.tex', res_pic(h, cap=cap_ac1, reach=reach_a, scale=0.8, reach_label=labA,
                                 extra="  \\draw[cutline] " + C1 + ";"))
    f7 = dict(h)
    f7[('s', 'a')] = 1
    f7[('c', 't')] = 6
    check(f7, cap_ac1)
    write('2b-ac-ny.tex', net_pic(f7, cap=cap_ac1, scale=SC))

    # flödesuppdelning av f2: stigen genom a->c
    write('f2-stig-ac.tex', net_pic(S4, scale=0.8, satmark=False,
                                    estyle={('s', 'a'): 'aug', ('a', 'c'): 'aug', ('c', 't'): 'aug'}))
    print('värden:', val(S4), val(FSTAR), val(f9), val(f7))


if __name__ == '__main__':
    ff_walk()
    statics()
    print('ok')
