# -*- coding: utf-8 -*-
"""Genererar TikZ för uppgift 6 (julgransbelysning) och verifierar analysen."""
import os
import itertools
OUT = 'gen'
os.makedirs(OUT, exist_ok=True)


def write(name, text):
    with open(os.path.join(OUT, name), 'w') as fh:
        fh.write(text + "\n")


# ----------------------------------------------------------------------
#  Simulering av Viggos algoritm
# ----------------------------------------------------------------------
def run(n, broken, trick=False, trace=False):
    """broken: mängd av index 1..n (gamla lampor o_1..o_n som är trasiga)."""
    works = lambda lamp: lamp == 'N' or lamp not in broken
    sockets = [1] + ['N'] * (n - 1)
    cost = n - 1
    bag = list(range(2, n + 1))
    known_ok = set()
    lit = lambda: all(works(x) for x in sockets)
    states = [(list(sockets), cost, lit(), list(bag))]
    i = 0                                   # 0-indexerad plats
    while bag:
        if lit():
            known_ok.add(sockets[i])
            i += 1
        # (annars: lampan på plats i är gammal och trasig; den skruvas ur)
        nxt = bag.pop(0)
        if trick and not bag and all(k in known_ok for k in range(1, n)) and i == n - 1 and sockets[i] == 'N':
            # alla o_1..o_{n-1} hela, och det lyste inte från början: o_n är trasig
            states.append((list(sockets), cost, lit(), list(bag)))
            break
        sockets[i] = nxt
        cost += 1
        states.append((list(sockets), cost, lit(), list(bag)))
    if not lit():
        sockets[i] = 'N'
        cost += 1
        states.append((list(sockets), cost, lit(), list(bag)))
    # korrekthet: lyser, alla hela gamla sitter i, nya bara för trasiga
    assert lit()
    olds = [x for x in sockets if x != 'N']
    assert sorted(olds) == sorted(set(range(1, n + 1)) - broken), (n, broken, sockets)
    return (cost, states) if trace else cost


for n in range(1, 9):
    for r in range(1, n + 1):
        for B in itertools.combinations(range(1, n + 1), r):
            B = set(B)
            c = run(n, B)
            assert c == 2 * n - 2 + (1 if n in B else 0), (n, B, c)
            if n >= 2:
                ct = run(n, B, trick=True)
                assert ct <= c
                if B == {n}:
                    assert ct == 2 * n - 3, (n, ct)
    if n >= 2:
        assert max(run(n, set(B), trick=True) for r in range(1, n + 1)
                   for B in itertools.combinations(range(1, n + 1), r)) == 2 * n - 1


# ----------------------------------------------------------------------
#  Uttömmande kontroll av den undre gränsen för små n:
#  kortaste väg i konfigurationsgrafen för det bästa adaptiva schemat vore
#  för dyrt; vi kontrollerar i stället solokonfigurationsargumentet:
#  körningen på X (alla trasiga) passerar alla S_j.
# ----------------------------------------------------------------------
def visits_all_solos(n):
    B = set(range(1, n + 1))
    _, states = run(n, B, trace=True)
    seen = set()
    for sockets, _, _, _ in states:
        olds = [x for x in sockets if x != 'N']
        if len(olds) == 1:
            seen.add(olds[0])
    return seen == B


for n in range(1, 9):
    assert visits_all_solos(n)

COST = {B: run(5, set(B)) for B in [(2, 5), (5,), (1, 2, 3, 4, 5), (1,), (2,), (1, 2, 3, 4)]}


# ----------------------------------------------------------------------
#  Ritning
# ----------------------------------------------------------------------
DX = 1.25


def lamps(sockets, lit, broken_known=(), scale=0.9, extra='', labels=True):
    """sockets: lista med 'o1', 'o2', ..., eller 'N'."""
    n = len(sockets)
    L = [f"\\begin{{tikzpicture}}[scale={scale}]"]
    L.append(f"  \\useasboundingbox (0.35,-0.75) rectangle ({DX * n + 0.9},1.25);")
    wire = 'kthorange' if lit else 'black!45'
    L.append(f"  \\draw[{wire},line width=1pt] (0.5,0) -- ({DX * n + 0.75},0);")
    L.append(f"  \\draw[{wire},line width=1pt] (0.5,0) -- (0.5,-0.45) -- ({DX * n + 0.75},-0.45)"
             f" -- ({DX * n + 0.75},0);")
    for k, s in enumerate(sockets, start=1):
        x = DX * k
        new = (s == 'N')
        if lit:
            L.append(f"  \\fill[lampyellow!45] ({x},0.62) circle (0.5);")
            fill = 'lampyellow'
        else:
            fill = 'black!8'
        draw = 'kthgreen' if new else 'kthnavy'
        L.append(f"  \\fill[black!55] ({x - 0.13},0.02) rectangle ({x + 0.13},0.22);")
        L.append(f"  \\filldraw[fill={fill},draw={draw},line width={'1.3pt' if new else '0.7pt'}] "
                 f"({x},0.58) circle (0.34);")
        txt = r'\textbf{N}' if new else f"$o_{{{s[1:]}}}$"
        col = 'kthgreen' if new else 'kthnavy'
        L.append(f"  \\node[font=\\footnotesize,text={col}] at ({x},0.58) {{{txt}}};")
        if labels:
            L.append(f"  \\node[font=\\tiny,text=black!45] at ({x},-0.22) {{{k}}};")
    if extra:
        L.append(extra)
    L.append("\\end{tikzpicture}")
    return "\n".join(L)


def bag_pic(bag, discarded, cost):
    L = [r"\begin{tikzpicture}[scale=0.9]"]
    L.append(r"  \useasboundingbox (-0.2,-0.75) rectangle (4.9,1.25);")
    # säcken
    L.append(r"  \filldraw[fill=sand,draw=bark,line width=0.8pt,rounded corners=6pt] "
             r"(0,-0.5) -- (1.9,-0.5) -- (1.7,0.75) -- (1.25,0.95) -- (0.65,0.95) -- (0.2,0.75) -- cycle;")
    L.append(r"  \draw[bark,line width=1pt] (0.6,0.95) -- (1.3,0.95);")
    L.append(r"  \node[font=\tiny,text=bark] at (0.95,1.13) {säcken};")
    contents = ", ".join(f"$o_{b}$" for b in bag) if bag else r"\textit{tom}"
    L.append(f"  \\node[font=\\scriptsize,text width=1.6cm,align=center] at (0.95,0.2) {{{contents}}};")
    trasig = ", ".join(f"$o_{b}$" for b in discarded) if discarded else "—"
    L.append(f"  \\node[font=\\scriptsize,anchor=west] at (2.25,0.65) {{trasiga: {trasig}}};")
    L.append(f"  \\node[font=\\small\\bfseries,text=kthnavy,anchor=west] at (2.25,0.0) {{byten: {cost}}};")
    L.append(r"\end{tikzpicture}")
    return "\n".join(L)


def walk_frame():
    n = 5
    B = {2, 5}
    # tillstånd: (sockets, lit, bag, trasiga, byten, text)
    steps = [
        (['o1', 'o2', 'o3', 'o4', 'o5'], False, [], [], 0,
         r"Det lyser inte. Minst en lampa är trasig — men vilka?"),
        (['o1', 'N', 'N', 'N', 'N'], True, [2, 3, 4, 5], [], 4,
         r"Byt alla utom plats 1 mot nya: 4 byten. De gamla i säcken. Det lyser! "
         r"\emph{Fantastiskt.} $o_1$ är hel."),
        (['o1', 'o2', 'N', 'N', 'N'], False, [3, 4, 5], [], 5,
         r"Plats 2: ny ut, $o_2$ in. Mörkt. \emph{Ånej.} $o_2$ är trasig."),
        (['o1', 'o3', 'N', 'N', 'N'], True, [4, 5], [2], 6,
         r"$o_2$ ut, $o_3$ in på samma plats. Det lyser. \emph{Otroligt.} $o_3$ är hel."),
        (['o1', 'o3', 'o4', 'N', 'N'], True, [5], [2], 7,
         r"Plats 3: ny ut, $o_4$ in. Det lyser. \emph{Häpnadsväckande.}"),
        (['o1', 'o3', 'o4', 'o5', 'N'], False, [], [2], 8,
         r"Plats 4: ny ut, $o_5$ in. Mörkt: $o_5$ är trasig. Säcken är tom."),
        (['o1', 'o3', 'o4', 'N', 'N'], True, [], [2, 5], 9,
         r"$o_5$ ut, en ny in. \emph{Hilvide.} $9=2n-1$ byten."),
    ]
    # kontroll mot simuleringen
    cost, states = run(n, B, trace=True)
    assert cost == 9
    sim = [([('N' if x == 'N' else f"o{x}") for x in s], c, l) for s, c, l, _ in states]
    mine = [(s, c, l) for s, l, _, _, c, _ in steps[1:]]
    assert sim == mine, (sim, mine)
    L = [r"\begin{frame}{Viggos algoritm steg för steg ($n=5$, trasiga: $o_2$ och $o_5$)}"]
    for k, (sk, lit, bag, disc, c, txt) in enumerate(steps, start=1):
        L.append(f"\\only<{k}>{{%")
        L.append(r"\begin{columns}[T]")
        L.append(r"\begin{column}{0.62\textwidth}\centering")
        L.append(lamps(sk, lit))
        L.append(r"\end{column}")
        L.append(r"\begin{column}{0.35\textwidth}")
        L.append(bag_pic(bag, disc, c))
        L.append(r"\end{column}")
        L.append(r"\end{columns}")
        L.append(r"\medskip")
        L.append(r"\begin{tcolorbox}[enhanced,halign=left,colback=kthlight!50,colframe=kthsky,boxrule=0.4pt,"
                 r"arc=2pt,left=4pt,right=4pt,top=1pt,bottom=1pt,fontupper=\small,height=1.05cm,valign=center]")
        L.append(txt)
        L.append(r"\end{tcolorbox}}")
    L.append(r"\vfill")
    L.append(r"{\footnotesize\color{black!55}Invariant: platserna före $i$ har hela gamla lampor, plats $i$ en gammal "
             r"lampa, platserna efter $i$ nya. (Utropen är lånade från Alice.)}")
    L.append(r"\varstrip{Generalisering}{algoritmen}{vilka lampor som är trasiga}{att varje gammal lampa provas en gång}")
    L.append(r"\end{frame}")
    write('lamp-walk.tex', "\n".join(L))


if __name__ == '__main__':
    walk_frame()
    write('lamp-start.tex', lamps(['o1', 'o2', 'o3', 'o4', 'o5'], False, scale=0.85))
    print('kostnader n=5:', COST)
