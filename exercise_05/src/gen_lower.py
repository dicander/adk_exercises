# -*- coding: utf-8 -*-
"""Genererar TikZ för avsnitt 5 (undre gränser): rutnätet, kurvorna och beslutsträden."""
import os
import itertools
from fractions import Fraction
OUT = 'gen'
os.makedirs(OUT, exist_ok=True)


def write(name, text):
    with open(os.path.join(OUT, name), 'w') as fh:
        fh.write(text + "\n")


# ----------------------------------------------------------------------
#  Insättningssortering: jämförelser, kontrollerat mot uttömmande räkning
# ----------------------------------------------------------------------
def comparisons(a):
    a = list(a)
    c = 0
    for i in range(1, len(a)):
        x = a[i]
        j = i - 1
        while j >= 0:
            c += 1
            if a[j] > x:
                a[j + 1] = a[j]
                j -= 1
            else:
                break
        a[j + 1] = x
    return c


def H(n):
    return sum(Fraction(1, k) for k in range(1, n + 1))


for n in range(1, 8):
    cs = [comparisons(p) for p in itertools.permutations(range(n))]
    assert min(cs) == max(0, n - 1)
    assert max(cs) == n * (n - 1) // 2
    assert Fraction(sum(cs), len(cs)) == Fraction(n * (n - 1), 4) + n - H(n), n


def best(n):
    return n - 1


def worst(n):
    return n * (n - 1) / 2


def avg(n):
    return n * (n - 1) / 4 + n - float(H(n))


# ----------------------------------------------------------------------
#  Rutnätet O/Ω/Θ × bästa/medel/värsta
# ----------------------------------------------------------------------
COLX = [4.05, 7.2, 10.35]
ROWY = [-0.95, -1.95, -2.95]


def grid_frame():
    L = [r"\begin{frame}{Övre och undre gräns är inte bästa och värsta fall}",
         r"\centering",
         r"\begin{tikzpicture}[x=1cm,y=1cm,",
         r"  hd/.style={font=\small\bfseries,text=kthnavy,align=center},",
         r"  rl/.style={font=\small,align=left,anchor=west},",
         r"  cell/.style={draw=black!25,minimum width=30.5mm,minimum height=9.2mm,inner sep=0pt},",
         r"  big/.style={font=\normalsize},",
         r"  loose/.style={font=\scriptsize,text=black!50}]",
         r"  \useasboundingbox (-0.05,0.55) rectangle (11.95,-3.95);"]
    heads = [r"bästa fallet\\[-1pt]{\footnotesize\mdseries $T_{\min}(n)$}",
             r"medelfallet\\[-1pt]{\footnotesize\mdseries $T_{\mathrm{medel}}(n)$}",
             r"värsta fallet\\[-1pt]{\footnotesize\mdseries $T_{\max}(n)$}"]
    for x, h in zip(COLX, heads):
        L.append(f"  \\node[hd] at ({x},0) {{{h}}};")
    rows = [r"$O$\ \ övre gräns", r"$\Omega$\ \ undre gräns", r"$\Theta$\ \ båda"]
    for y, r in zip(ROWY, rows):
        L.append(f"  \\node[rl] at (0,{y}) {{{r}}};")
    for x in COLX:
        for y in ROWY:
            L.append(f"  \\node[cell] at ({x},{y}) {{}};")
    # overlay 1: den felaktiga diagonalen
    wrong = {(0, 2): r"$O$ = värsta", (2, 1): r"$\Theta$ = medel", (1, 0): r"$\Omega$ = bästa"}
    for (r, c), txt in wrong.items():
        L.append(f"  \\node[cell,fill=coral!25,visible on=<1>] at ({COLX[c]},{ROWY[r]}) {{\\small {txt}}};")
    L.append(r"  \node[rotate=12,draw=brick,line width=2pt,text=brick,rounded corners=3pt,"
             r"font=\Huge\bfseries,inner sep=4pt,fill=white,fill opacity=0.85,text opacity=1,"
             r"visible on=<1>] at (7.2,-1.95) {Nej.};")
    # overlay 2-3: insättningssortering
    tight = [[r"$O(n)$", r"$O(n^2)$", r"$O(n^2)$"],
             [r"$\Omega(n)$", r"$\Omega(n^2)$", r"$\Omega(n^2)$"],
             [r"$\Theta(n)$", r"$\Theta(n^2)$", r"$\Theta(n^2)$"]]
    loose = [[r"också $O(n^2)$, $O(n^3)$", r"också $O(n^3)$", r"också $O(n^3)$, $O(2^n)$"],
             [r"också $\Omega(1)$", r"också $\Omega(n)$", r"också $\Omega(n\log n)$"],
             [r"bara den klassen", r"bara den klassen", r"bara den klassen"]]
    hi = {(0, 0), (1, 2)}
    for r in range(3):
        for c in range(3):
            x, y = COLX[c], ROWY[r]
            if (r, c) in hi:
                L.append(f"  \\node[cell,fill=lampyellow!45,draw=kthorange,line width=1pt,visible on=<2->] "
                         f"at ({x},{y}) {{}};")
            L.append(f"  \\node[big,visible on=<2>] at ({x},{y}) {{{tight[r][c]}}};")
            L.append(f"  \\node[big,visible on=<3>] at ({x},{y + 0.14}) {{{tight[r][c]}}};")
            L.append(f"  \\node[loose,visible on=<3>] at ({x},{y - 0.24}) {{{loose[r][c]}}};")
    # etiketter under kolumnerna
    L.append(r"  \node[visible on=<2->,font=\footnotesize\bfseries,text=kthorange] at (4.05,-3.68)"
             r" {\raisebox{0.1ex}{$\blacktriangle$} Bästa fallet har ett ordo};")
    L.append(r"  \node[visible on=<2->,font=\footnotesize\bfseries,text=kthorange] at (10.35,-3.68)"
             r" {\raisebox{0.1ex}{$\blacktriangle$} Värsta fallet har ett $\Omega$};")
    L.append(r"\end{tikzpicture}")
    capt = [
        r"En vanlig bild: tre synonymer. $O$ betyder värsta fallet, $\Omega$ bästa, $\Theta$ medel. "
        r"Den är fel, och den gör resten av kursen svårare än den behöver vara.",
        r"Insättningssortering, alla nio rutor. \textbf{Fallet} väljer \emph{vilken funktion} vi pratar om. "
        r"$O$, $\Omega$, $\Theta$ säger hur \emph{den} växer: uppåt begränsad, nedåt begränsad, eller båda.",
        r"$O$ och $\Omega$ får vara lösa och fortfarande sanna. $\Theta$ får inte det. "
        r"”Värsta fallet är $O(2^n)$” är sant — och helt ointressant.",
    ]
    L.append(r"\vfill")
    L.append(r"\begin{tcolorbox}[enhanced,halign=left,colback=kthlight!50,colframe=kthsky,boxrule=0.4pt,arc=2pt,"
             r"left=4pt,right=4pt,top=1pt,bottom=1pt,fontupper=\small,height=1.25cm,valign=center]")
    L.append("".join(f"\\only<{k + 1}>{{{c}}}" for k, c in enumerate(capt)))
    L.append(r"\end{tcolorbox}")
    L.append(r"\end{frame}")
    write('grid.tex', "\n".join(L))


# ----------------------------------------------------------------------
#  Tre funktioner, inte en: kurvor för insättningssortering
# ----------------------------------------------------------------------
def curves():
    xs, ys = 0.56, 0.054
    N = range(1, 11)
    L = [r"\begin{tikzpicture}[x=%.2fcm,y=%.3fcm]" % (xs, ys)]
    L.append(r"  \draw[->,black!60] (0,0) -- (11,0) node[below left,font=\scriptsize,text=black!70] {$n$};")
    L.append(r"  \draw[->,black!60] (0,0) -- (0,50) node[above right,font=\scriptsize,text=black!70]"
             r" {jämförelser};")
    for n in (2, 4, 6, 8, 10):
        L.append(f"  \\draw[black!40] ({n},0) -- ({n},-0.8) node[below,font=\\tiny,text=black!60] {{{n}}};")
    for v in (10, 20, 30, 40):
        L.append(f"  \\draw[black!40] (0,{v}) -- (-0.15,{v}) node[left,font=\\tiny,text=black!60] {{{v}}};")
    for n in N:
        L.append(f"  \\draw[black!15,line width=3.2pt] ({n},{best(n)}) -- ({n},{worst(n)});")
    for f, col in ((worst, 'brick'), (avg, 'kthorange'), (best, 'kthgrass')):
        pts = " -- ".join(f"({n},{f(n):.3f})" for n in N)
        L.append(f"  \\draw[{col},line width=1pt] {pts};")
        for n in N:
            L.append(f"  \\fill[{col}] ({n},{f(n):.3f}) circle (1.6pt);")
    L.append(r"  \node[font=\scriptsize\bfseries,text=brick,anchor=west] at (10.2,45) {$T_{\max}$};")
    L.append(r"  \node[font=\scriptsize\bfseries,text=kthorange,anchor=west] at (10.2,%.2f)"
             r" {$T_{\mathrm{medel}}$};" % avg(10))
    L.append(r"  \node[font=\scriptsize\bfseries,text=kthgrass,anchor=west] at (10.2,9) {$T_{\min}$};")
    L.append(r"\end{tikzpicture}")
    write('kurvor.tex', "\n".join(L))


# ----------------------------------------------------------------------
#  Beslutsträd för n = 7
# ----------------------------------------------------------------------
TSTY = r"""dn/.style={circle,draw=kthnavy,fill=white,line width=0.6pt,inner sep=0pt,minimum size=6.2mm,font=\scriptsize},
  hit/.style={rectangle,draw=kthgreen,fill=kthmint,inner sep=0pt,minimum size=3.6mm,font=\tiny\bfseries},
  ej/.style={rectangle,draw=black!35,fill=black!8,inner sep=0pt,minimum size=2.6mm},
  te/.style={draw=black!45,line width=0.6pt},
  tl/.style={font=\tiny,text=black!60,inner sep=0.5pt,fill=white}"""


def tree_balanced(scale=0.7, name='dt-bin7.tex', highlight=None):
    """highlight: lista med nodnamn på en körning (för kontrastbilden)."""
    L = [f"\\begin{{tikzpicture}}[scale={scale},{TSTY}]"]
    pos = {4: (0, 0), 2: (-3.4, -1.1), 6: (3.4, -1.1), 1: (-5.1, -2.2), 3: (-1.7, -2.2), 5: (1.7, -2.2),
           7: (5.1, -2.2)}
    for i, (x, y) in pos.items():
        L.append(f"  \\node[dn] (n{i}) at ({x},{y}) {{$a_{i}$}};")
    kids = {4: (2, 6), 2: (1, 3), 6: (5, 7)}
    for p, (l, r) in kids.items():
        L.append(f"  \\draw[te] (n{p}) -- node[tl,pos=0.45] {{$<$}} (n{l});")
        L.append(f"  \\draw[te] (n{p}) -- node[tl,pos=0.45] {{$>$}} (n{r});")
        x, y = pos[p]
        L.append(f"  \\node[hit] (h{p}) at ({x},{y - 1.1}) {{{p}}};")
        L.append(f"  \\draw[te] (n{p}) -- node[tl,pos=0.5] {{$=$}} (h{p});")
    for i in (1, 3, 5, 7):
        x, y = pos[i]
        L.append(f"  \\node[ej] (el{i}) at ({x - 0.65},{y - 1.05}) {{}};")
        L.append(f"  \\node[hit] (h{i}) at ({x},{y - 1.1}) {{{i}}};")
        L.append(f"  \\node[ej] (er{i}) at ({x + 0.65},{y - 1.05}) {{}};")
        L.append(f"  \\draw[te] (n{i}) -- (el{i}); \\draw[te] (n{i}) -- (h{i}); \\draw[te] (n{i}) -- (er{i});")
    L.append(r"\end{tikzpicture}")
    write(name, "\n".join(L))


def tree_linear(scale=0.6, name='dt-lin7.tex'):
    L = [f"\\begin{{tikzpicture}}[scale={scale},{TSTY}]"]
    dx, dy = 1.25, 0.72
    for i in range(1, 8):
        x, y = dx * (i - 1), -dy * (i - 1)
        L.append(f"  \\node[dn] (n{i}) at ({x},{y}) {{$a_{i}$}};")
        L.append(f"  \\node[ej] (el{i}) at ({x - 0.62},{y - dy}) {{}};")
        L.append(f"  \\node[hit] (h{i}) at ({x},{y - dy}) {{{i}}};")
        L.append(f"  \\draw[te] (n{i}) -- (el{i}); \\draw[te] (n{i}) -- (h{i});")
        if i > 1:
            L.append(f"  \\draw[te] (n{i - 1}) -- (n{i});")
    x, y = dx * 6, -dy * 6
    L.append(f"  \\node[ej] (last) at ({x + 0.62},{y - dy}) {{}};")
    L.append(r"  \draw[te] (n7) -- (last);")
    L.append(r"\end{tikzpicture}")
    write(name, "\n".join(L))


# ----------------------------------------------------------------------
#  Reduktion: sortering -> konvext hölje
# ----------------------------------------------------------------------
def hull_pic():
    xs = [-1.8, -0.7, 0.4, 1.1, 1.9]
    s = 0.55
    L = [r"\begin{tikzpicture}[x=0.75cm,y=0.42cm]"]
    L.append(r"  \draw[->,black!50] (-2.3,0) -- (2.4,0) node[right,font=\tiny] {$x$};")
    L.append(r"  \draw[->,black!50] (0,-0.2) -- (0,4.2) node[above,font=\tiny] {$x^2$};")
    L.append(r"  \draw[black!25,domain=-2.0:2.05,samples=40] plot (\x,{\x*\x});")
    pts = [(x, x * x) for x in xs]
    L.append("  \\draw[kthblue,line width=1pt] " + " -- ".join(f"({x},{y:.3f})" for x, y in pts) + " -- cycle;")
    for x, y in pts:
        L.append(f"  \\fill[kthorange] ({x},{y:.3f}) circle (2pt);")
    L.append(r"\end{tikzpicture}")
    write('hull.tex', "\n".join(L))


if __name__ == '__main__':
    grid_frame()
    curves()
    tree_balanced()
    tree_linear()
    tree_balanced(scale=0.56, name="dt-bin7-s.tex")
    hull_pic()
    print('medel n=10:', avg(10))
