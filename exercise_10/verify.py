#!/usr/bin/env python3
"""Kontrollräkning av alla exempel och reduktioner i övning 10-bilderna.

Varje avsnitt skriver ut det som står på bilderna, så att inget i TikZ-figurerna
är handräknat. Kör:  python3 verify.py
"""
import itertools
import random
import sys

random.seed(10)
OK = True


def check(cond, msg):
    global OK
    print(("  ok   " if cond else "  FEL  ") + msg)
    if not cond:
        OK = False


# ---------------------------------------------------------------------------
# 0. Verktygslådan: delmängdssumma med tabell (exemplet på pseudopolynomisk tid)
# ---------------------------------------------------------------------------
print("== 0. Verktygslådan: delmängdssumma med tabell ==")


def delsumma_dp(ps, K):
    """Algoritmen på bilden 'Indatas storlek mäts i bitar'.

    nas[s] är sant om någon delmängd av de tal som hittills behandlats har summan s."""
    nas = [True] + [False] * K
    for p in ps:
        for s in range(K, p - 1, -1):
            if nas[s - p]:
                nas[s] = True
    return nas


nas = delsumma_dp([3, 5, 8, 13], 11)
print("  {3,5,8,13}, K=11: summor som nås:", [s for s in range(12) if nas[s]], "-> svar", "ja" if nas[11] else "nej")
check([s for s in range(12) if nas[s]] == [0, 3, 5, 8, 11], "exemplet: precis summorna 0, 3, 5, 8 och 11 nås, så svaret är ja (3+8)")
rng0 = random.Random(4)  # egen slumpkälla, så att avsnitten nedan får samma slumptal som förut
bad = 0
for _ in range(2000):
    ps = [rng0.randint(1, 15) for _ in range(rng0.randint(1, 8))]
    K0 = rng0.randint(1, 40)
    brute = any(sum(c) == K0 for r in range(len(ps) + 1) for c in itertools.combinations(ps, r))
    bad += delsumma_dp(ps, K0)[K0] != brute
check(bad == 0, "tabellalgoritmen ger samma svar som uttömmande sökning (2000 slumpinstanser)")
# tabellen på bilden: K, antal bitar, och tiden för att gå igenom K rutor med 10^9 rutor per sekund
YEAR = 365.25 * 24 * 3600
for K0, bits in ((255, 8), (10 ** 6, 20), (10 ** 18, 60), (3 * 10 ** 38, 128)):
    sec = K0 / 1e9
    tid = f"{sec * 1000:.3g} ms" if sec < 1 else f"{sec / YEAR:.3g} år"
    print(f"  K = {K0:.3g}: {K0.bit_length()} bitar, {tid} per tal")
    check(K0.bit_length() == bits, f"K = {K0:.3g} skrivs med {bits} bitar")
check(round(1e18 / 1e9 / YEAR) == 32 and 0.9e22 < 3e38 / 1e9 / YEAR < 1.1e22, "10^18 rutor tar 32 år och 3*10^38 rutor ungefär 10^22 år")

# ---------------------------------------------------------------------------
# A. Uppgift 1: kappsäck
# ---------------------------------------------------------------------------
print("== A. Kappsäck ==")
ITEMS = {1: (4, 6), 2: (3, 4), 3: (1, 1), 4: (5, 8), 5: (2, 3), 6: (4, 5)}  # p: (vikt, värde)
S, K = 10, 15
CALLS = 0


def A(P, S, K, items=ITEMS):
    """Beslutsorakel: finns delmängd av P med vikt <= S och värde >= K? (brute force)"""
    global CALLS
    CALLS += 1
    P = list(P)
    for r in range(len(P) + 1):
        for sub in itertools.combinations(P, r):
            if sum(items[p][0] for p in sub) <= S and sum(items[p][1] for p in sub) >= K:
                return True
    return False


def construct(order, S, K, items=ITEMS, verbose=False):
    global CALLS
    CALLS = 0
    P = set(order)
    if not A(P, S, K, items):
        return None, CALLS
    for p in order:
        ans = A(P - {p}, S, K, items)
        if verbose:
            print(f"    A(P - p{p}) = {'ja ' if ans else 'nej'}  ->  P = {sorted(P - {p}) if ans else sorted(P)}")
        if ans:
            P = P - {p}
    return P, CALLS


def is_solution(P, S, K, items=ITEMS):
    return sum(items[p][0] for p in P) <= S and sum(items[p][1] for p in P) >= K


sols = [set(c) for r in range(7) for c in itertools.combinations(ITEMS, r) if is_solution(c, S, K)]
print("  alla lösningar:", [sorted(s) for s in sols])
print("  ordning 1..6:")
P1, c1 = construct([1, 2, 3, 4, 5, 6], S, K, verbose=True)
print("  resultat", sorted(P1), "anrop", c1, "vikt", sum(ITEMS[p][0] for p in P1), "värde", sum(ITEMS[p][1] for p in P1))
print("  ordning 6..1:")
P2, c2 = construct([6, 5, 4, 3, 2, 1], S, K, verbose=True)
print("  resultat", sorted(P2), "anrop", c2, "vikt", sum(ITEMS[p][0] for p in P2), "värde", sum(ITEMS[p][1] for p in P2))
check(is_solution(P1, S, K) and is_solution(P2, S, K), "båda ordningarna ger en lösning")
check(c1 == 7 and c2 == 7, "|P|+1 = 7 anrop")
check(P1 != P2, "olika ordning ger olika lösning")
best = max(sum(ITEMS[p][1] for p in c) for r in range(7) for c in itertools.combinations(ITEMS, r)
           if sum(ITEMS[p][0] for p in c) <= S)
print("  största möjliga värde med S=10:", best, " summa av alla värden:", sum(v for _, v in ITEMS.values()))
# binärsökning efter optimum
lo, hi, steps = 0, sum(v for _, v in ITEMS.values()), 0
trace = []
while lo < hi:
    mid = (lo + hi + 1) // 2
    steps += 1
    ans = A(set(ITEMS), S, mid)
    trace.append((mid, ans))
    if ans:
        lo = mid
    else:
        hi = mid - 1
print("  binärsökning:", trace, "-> K* =", lo, "på", steps, "anrop")
check(lo == best, "binärsökningen hittar optimum")
# kaninhål: lägre mål ger en minimal men inte optimal lösning
P3, _ = construct([1, 2, 3, 4, 5, 6], S, 12)
print("  K=12, ordning 1..6:", sorted(P3), "vikt", sum(ITEMS[p][0] for p in P3), "värde", sum(ITEMS[p][1] for p in P3))
sols12 = [sorted(c) for r in range(7) for c in itertools.combinations(ITEMS, r) if is_solution(c, S, 12)]
print("  antal lösningar för K=12:", len(sols12))

# slumptest: algoritmen ger alltid en lösning när en finns, med <= |P|+1 anrop, och minimal
for _ in range(400):
    n = random.randint(1, 7)
    items = {i: (random.randint(0, 6), random.randint(0, 6)) for i in range(1, n + 1)}
    s, k = random.randint(0, 12), random.randint(0, 14)
    order = list(items)
    random.shuffle(order)
    P, c = construct(order, s, k, items)
    exists = any(is_solution(sub, s, k, items) for r in range(n + 1) for sub in itertools.combinations(items, r))
    if not exists:
        assert P is None
        continue
    assert P is not None and is_solution(P, s, k, items) and c == n + 1
    for p in P:  # minimal: inget element kan tas bort
        assert not A(P - {p}, s, k, items)
check(True, "400 slumpinstanser: resultatet är en (inklusionsminimal) lösning, |P|+1 anrop")


# DP (pseudopolynomisk) mot brute force
def knap_dp(items, S):
    ids = sorted(items)
    M = [[0] * (S + 1) for _ in range(len(ids) + 1)]
    for i, p in enumerate(ids, 1):
        w, v = items[p]
        for c in range(S + 1):
            M[i][c] = M[i - 1][c]
            if c >= w:
                M[i][c] = max(M[i][c], M[i - 1][c - w] + v)
    return M[len(ids)][S]


check(knap_dp(ITEMS, S) == best, f"DP-rekursionen ger samma optimum ({best})")

# ---------------------------------------------------------------------------
# B. Uppgift 2: Internet / hamiltoncykel
# ---------------------------------------------------------------------------
print("== B. Internet ==")


def paths_masks(adj, n, s, t):
    """Alla enkla s-t-stigar som (inre-hörn-mask, kantmängd)."""
    res = []

    def dfs(u, vis, inner, edges):
        if u == t:
            res.append((inner, frozenset(edges)))
            return
        for v in range(n):
            if adj[u] >> v & 1 and not vis >> v & 1:
                e = (min(u, v), max(u, v))
                dfs(v, vis | 1 << v, inner | (1 << v if v != t else 0), edges + [e])

    dfs(s, 1 << s, 0, [])
    return res


def two_disjoint(adj, n, s, t, edge_version=False):
    ps = paths_masks(adj, n, s, t)
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            if edge_version:
                if not (ps[i][1] & ps[j][1]):
                    return True
            else:
                if not (ps[i][0] & ps[j][0]) and ps[i][1] != ps[j][1]:
                    return True
    return False


def adj_of(edges, n):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def all_pairs_two(edges, n, edge_version=False):
    adj = adj_of(edges, n)
    return all(two_disjoint(adj, n, s, t, edge_version) for s in range(n) for t in range(s + 1, n))


def is_ham_cycle(edges, n):
    """Kantmängden är precis en cykel genom alla n hörn."""
    if len(edges) != n or n < 3:
        return False
    adj = adj_of(edges, n)
    if any(bin(a).count("1") != 2 for a in adj):
        return False
    seen, u, prev = 1, 0, -1
    for _ in range(n - 1):
        nxt = [v for v in range(n) if adj[u] >> v & 1 and v != prev]
        prev, u = u, nxt[0]
        if seen >> u & 1:
            return False
        seen |= 1 << u
    return seen == (1 << n) - 1


def has_ham(edges, n):
    if n < 3:
        return False
    es = set(edges)
    for perm in itertools.permutations(range(1, n)):
        cyc = (0,) + perm
        if all((min(cyc[i], cyc[(i + 1) % n]), max(cyc[i], cyc[(i + 1) % n])) in es for i in range(n)):
            return True
    return False


GOOD = {}  # n -> alla delgrafer till K_n med n kanter där varje par har två hörndisjunkta stigar

for n in range(3, 8):
    alle = list(itertools.combinations(range(n), 2))
    good_v, good_e, cycles = set(), set(), set()
    for sub in itertools.combinations(alle, n):
        if all_pairs_two(sub, n):
            good_v.add(sub)
        if n <= 6 and all_pairs_two(sub, n, edge_version=True):
            good_e.add(sub)
        if is_ham_cycle(sub, n):
            cycles.add(sub)
    GOOD[n] = good_v
    msg = f"n={n}: delgrafer med n kanter och T=2 överallt = hamiltoncyklerna ({len(cycles)} st)"
    check(good_v == cycles and (n > 6 or good_e == cycles), msg + (" [hörn- och kantdisjunkt]" if n <= 6 else " [hörndisjunkt]"))
    if n <= 6:  # hela reduktionen, alla grafer
        bad = 0
        for mask in range(1 << len(alle)):
            E = [alle[i] for i in range(len(alle)) if mask >> i & 1]
            Es = set(E)
            red_yes = any(all(e in Es for e in c) for c in good_v)
            if red_yes != has_ham(E, n):
                bad += 1
        check(bad == 0, f"n={n}: reduktionen stämmer för alla {1 << len(alle)} grafer")

# K_{2,3}
K23 = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]
check(all_pairs_two(K23, 5), "K_{2,3}: alla par har två hörndisjunkta stigar (6 kanter räcker)")
check(not any(all_pairs_two(sub, 5) for sub in itertools.combinations(K23, 5)), "K_{2,3}: 5 kanter räcker aldrig")
check(not has_ham(K23, 5), "K_{2,3} saknar hamiltoncykel")
# Prisma
PRISM = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)]
cyc = [(0, 1), (1, 2), (2, 5), (4, 5), (3, 4), (0, 3)]
check(all(e in PRISM for e in cyc) and is_ham_cycle(cyc, 6), "prismat: 1-2-3-6-5-4-1 är en hamiltoncykel")
nham = sum(1 for sub in itertools.combinations(PRISM, 6) if is_ham_cycle(sub, 6))
print("  prismat har", nham, "hamiltoncykler;",
      sum(1 for sub in itertools.combinations(PRISM, 6) if all_pairs_two(sub, 6)), "delgrafer med 6 kanter klarar T=2")

# exakt B / högst B: monotonicitet
bad = 0
for _ in range(300):
    n = random.randint(3, 6)
    alle = list(itertools.combinations(range(n), 2))
    E = [e for e in alle if random.random() < 0.6]
    for b in range(len(E) + 1):
        exact = any(all_pairs_two(sub, n) for sub in itertools.combinations(E, b))
        atmost = any(all_pairs_two(sub, n) for bb in range(b + 1) for sub in itertools.combinations(E, bb))
        if exact != atmost:
            bad += 1
check(bad == 0, "'exakt B' och 'högst B' ger samma svar när B <= |E| (300 slumpgrafer)")

# ---------------------------------------------------------------------------
# B2. Kaninhålet om certifikatet: från flöde till disjunkta stigar
# ---------------------------------------------------------------------------
print("== B2. Flöde och disjunkta stigar ==")


def split_network(n, edges, s, t):
    """Flödesnätet N för hörndisjunkta s-t-stigar i grafen (n, edges).

    Nod 2v är v_in och nod 2v+1 är v_ut.  s och t delas inte: källan är s_ut och
    utloppet t_in.  Alla kapaciteter är 1."""
    cap = {}
    for v in range(n):
        if v != s and v != t:
            cap[(2 * v, 2 * v + 1)] = 1
    for a, b in edges:
        for u, v in ((a, b), (b, a)):
            if u != t and v != s:  # inga bågar ut ur utloppet eller in i källan
                cap[(2 * u + 1, 2 * v)] = 1
    return cap, 2 * s + 1, 2 * t


def plain_network(n, edges, s, t):
    """Flödesnätet för kantdisjunkta stigar: ingen hörndelning, två bågar per kant."""
    cap = {}
    for a, b in edges:
        for u, v in ((a, b), (b, a)):
            if u != t and v != s:
                cap[(u, v)] = 1
    return cap, s, t


def ford_fulkerson(cap, S, T, pref=None, rng=None):
    """Ford-Fulkerson med djupetförstsökning i restflödesgrafen.

    Returnerar (flödet på varje båge, listan av utökande stigar).  pref[u] är en
    fast grannordning (för exemplet på bilden); rng slumpar ordningen."""
    res = dict(cap)
    for (u, v) in cap:
        res.setdefault((v, u), 0)
    nbr = {}
    for (u, v) in sorted(res):
        nbr.setdefault(u, []).append(v)
    aug = []
    while True:
        seen = {S}

        def dfs(u):
            if u == T:
                return [u]
            order = list(nbr.get(u, []))
            if pref and u in pref:
                order = pref[u] + [v for v in order if v not in pref[u]]
            elif rng:
                rng.shuffle(order)
            for v in order:
                if v not in seen and res[(u, v)] > 0:
                    seen.add(v)
                    p = dfs(v)
                    if p:
                        return [u] + p
            return None

        path = dfs(S)
        if not path:
            break
        d = min(res[(a, b)] for a, b in zip(path, path[1:]))
        for a, b in zip(path, path[1:]):
            res[(a, b)] -= d
            res[(b, a)] += d
        aug.append(path)
    return {a: max(0, cap[a] - res[a]) for a in cap}, aug


def flow_value(flow, cap, S, T):
    """Flödets värde, eller None om det inte är ett giltigt heltalsflöde."""
    net = {}
    for (u, v), f in flow.items():
        if f != int(f) or not 0 <= f <= cap[(u, v)]:
            return None
        net[u] = net.get(u, 0) - f
        net[v] = net.get(v, 0) + f
    if any(x for node, x in net.items() if node not in (S, T)):
        return None
    return net.get(T, 0)


def follow_flow(flow, S, T):
    """Bevisets steg 3 och 4: börja i S och följ flödesbågar tills T nås, en gång
    för varje flödesbåge ut ur S.  Returnerar (stigar, antal brott mot beviset)."""
    out = {}
    for (u, v), f in sorted(flow.items()):
        if f:
            out.setdefault(u, []).append(v)
    paths, broken = [], 0
    for first in out.get(S, []):
        path, u = [S, first], first
        while u != T:
            nxt = out.get(u, [])
            if len(nxt) != 1 or nxt[0] in path:  # precis en flödesbåge ut, ingen nod två gånger
                broken += 1
                break
            u = nxt[0]
            path.append(u)
        paths.append(path)
    return paths, broken


def unsplit(path):
    """Slå ihop v_in och v_ut till v igen."""
    res = []
    for x in path:
        if not res or res[-1] != x // 2:
            res.append(x // 2)
    return res


def peel_trails(flow, S, T):
    """Kantversionen: stryk flöde som går åt båda hållen på samma kant, dra sedan ut
    en vandring i taget från S till T och korta av slingorna."""
    f = {a for a, v in flow.items() if v}
    for (u, v) in list(f):
        if (u, v) in f and (v, u) in f:
            f -= {(u, v), (v, u)}
    out = {}
    for (u, v) in sorted(f):
        out.setdefault(u, []).append(v)
    paths = []
    while out.get(S):
        walk, u = [S], S
        while u != T:
            u = out[u].pop()  # flödets bevarande: det finns alltid en oanvänd båge ut
            walk.append(u)
        path = []
        for x in walk:
            if x in path:
                path = path[:path.index(x)]
            path.append(x)
        paths.append(path)
    return paths


def valid_paths(paths, edges, s, t, edge_version=False):
    """Stigarna är enkla s-t-stigar i grafen, olika och parvis disjunkta."""
    es = {(min(a, b), max(a, b)) for a, b in edges}
    used_v, used_e = set(), set()
    for p in paths:
        if p[0] != s or p[-1] != t or len(set(p)) != len(p):
            return False
        pe = {(min(a, b), max(a, b)) for a, b in zip(p, p[1:])}
        if not pe <= es or pe & used_e:
            return False
        if not edge_version and used_v & set(p[1:-1]):
            return False
        used_v |= set(p[1:-1])
        used_e |= pe
    return True


def max_disjoint_brute(adj, n, s, t):
    """Största antalet hörndisjunkta s-t-stigar, genom uttömmande sökning."""
    ps = paths_masks(adj, n, s, t)
    direct = any(inner == 0 for inner, _ in ps)
    masks = {inner for inner, _ in ps if inner}
    memo = {0: 0}

    def f(avail):
        if avail not in memo:
            low = avail & -avail
            r = f(avail ^ low)
            for m in masks:
                if m & low and not m & ~avail:
                    r = max(r, 1 + f(avail ^ m))
            memo[avail] = r
        return memo[avail]

    return f(((1 << n) - 1) & ~(1 << s) & ~(1 << t)) + direct


def max_edge_disjoint_brute(adj, n, s, t):
    """Största antalet kantdisjunkta s-t-stigar, genom uttömmande sökning."""
    idx = {e: i for i, e in enumerate(itertools.combinations(range(n), 2))}
    ms = sorted({sum(1 << idx[e] for e in es) for _, es in paths_masks(adj, n, s, t)})
    best = 0

    def rec(i, used, cnt):
        nonlocal best
        best = max(best, cnt)
        for j in range(i, len(ms)):
            if not ms[j] & used:
                rec(j + 1, used | ms[j], cnt + 1)

    rec(0, 0, 0)
    return best


def add_cycles(flow, S, T, rng, tries=4):
    """Lägg slumpvis valda slutna flödescykler på bågar utan flöde.  Resultatet är
    fortfarande ett heltalsflöde med samma värde -- men inte det Ford-Fulkerson gav."""
    flow = dict(flow)
    added = 0
    for _ in range(tries):
        free = {}
        for (u, v), f in flow.items():
            if f == 0:
                free.setdefault(u, []).append(v)
        starts = [u for u in free if u not in (S, T)]
        if not starts:
            break
        walk = [rng.choice(starts)]
        while walk[-1] in free and walk[-1] not in walk[:-1]:
            walk.append(rng.choice(free[walk[-1]]))
        if walk[-1] in walk[:-1]:
            cyc = walk[walk.index(walk[-1]):]
            for a, b in zip(cyc, cyc[1:]):
                flow[(a, b)] = 1
            added += 1
    return flow, added


# Exemplet på bilden: X, a, b, Y med kanterna X-a, X-b, a-b, a-Y, b-Y
EXN = ["X", "a", "b", "Y"]
EXE = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
cap, S, T = split_network(4, EXE, 0, 3)


def nn(x):
    return EXN[x // 2] + ("" if x // 2 in (0, 3) else "_in" if x % 2 == 0 else "_ut")


def show(path, cap):
    s = nn(path[0])
    for a, b in zip(path, path[1:]):
        s += (" -> " if (a, b) in cap else " <~ ") + nn(b)
    return s


print("  nätet N: noder", sorted({nn(x) for a in cap for x in a}), "och", len(cap), "bågar med kapacitet 1")
flow, aug = ford_fulkerson(cap, S, T, pref={S: [2], 3: [4]})  # X: a_in först; a_ut: b_in först
for i, p in enumerate(aug, 1):
    print(f"  utökande stig {i}:", show(p, cap), "   (<~ = bakåt över en båge med flöde)")
print("  färdigt flöde:", ", ".join(f"{nn(a)}->{nn(b)}" for (a, b), f in sorted(flow.items()) if f))
paths, broken = follow_flow(flow, S, T)
print("  avlästa stigar:", [" - ".join(EXN[v] for v in unsplit(p)) for p in paths])
check(len(aug) == 2 and flow_value(flow, cap, S, T) == 2, "exemplet: två utökningar, flödets värde är 2")
check([unsplit(p) for p in aug] == [[0, 1, 2, 3], [0, 2, 1, 3]], "exemplet: de utökande stigarna är X-a-b-Y och X-b-a-Y, båda genom a och b")
check(not valid_paths([unsplit(p) for p in aug], EXE, 0, 3), "exemplet: de utökande stigarna är inte disjunkta")
check(broken == 0 and sorted(unsplit(p) for p in paths) == [[0, 1, 3], [0, 2, 3]] and valid_paths([unsplit(p) for p in paths], EXE, 0, 3),
      "exemplet: ur flödet läses de disjunkta stigarna X-a-Y och X-b-Y")

# Slumpgrafer, alla par: hörnversionen
rng = random.Random(2350)
cases = notdisj = multi = bad_val = bad_paths = bad_cyc = cyc_added = 0
for _ in range(400):
    n = rng.randint(3, 7)
    alle = list(itertools.combinations(range(n), 2))
    dens = rng.uniform(0.3, 0.9)
    E = [e for e in alle if rng.random() < dens]
    adj = adj_of(E, n)
    for s, t in itertools.permutations(range(n), 2):
        cap, S, T = split_network(n, E, s, t)
        flow, aug = ford_fulkerson(cap, S, T, rng=rng)
        k = flow_value(flow, cap, S, T)
        cases += 1
        if k is None or k != len(aug) or k != max_disjoint_brute(adj, n, s, t):
            bad_val += 1
            continue
        paths, broken = follow_flow(flow, S, T)
        gp = [unsplit(p) for p in paths]
        if broken or len(gp) != k or not valid_paths(gp, E, s, t):
            bad_paths += 1
        if k >= 2:
            multi += 1
            forward = all((a, b) in cap for p in aug for a, b in zip(p, p[1:]))
            if not (forward and valid_paths([unsplit(p) for p in aug], E, s, t)):
                notdisj += 1
        flow2, added = add_cycles(flow, S, T, rng)
        cyc_added += added
        paths2, broken2 = follow_flow(flow2, S, T)
        gp2 = [unsplit(p) for p in paths2]
        if flow_value(flow2, cap, S, T) != k or broken2 or len(gp2) != k or not valid_paths(gp2, E, s, t):
            bad_cyc += 1
check(bad_val == 0, f"hörnversionen: flödets värde = största antalet disjunkta stigar (uttömmande sökning), {cases} fall")
check(bad_paths == 0, "hörnversionen: stigarna som läses av ur flödet är rätt antal, giltiga och disjunkta, i alla fall")
check(bad_cyc == 0, f"hörnversionen: detsamma efter att {cyc_added} slutna flödescykler lagts till (godtyckligt heltalsflöde)")
print(f"  de utökande stigarna var inte disjunkta stigar i {notdisj} av {multi} fall med minst två stigar"
      f" ({100 * notdisj // max(1, multi)} %)")
check(notdisj > 0, "invändningen stämmer: de utökande stigarna är ofta inte disjunkta")

# Slumpgrafer, alla par: kantversionen (ingen hörndelning)
cases = bad_val = bad_paths = bad_cyc = cyc_added = 0
for _ in range(250):
    n = rng.randint(3, 6)
    alle = list(itertools.combinations(range(n), 2))
    dens = rng.uniform(0.3, 0.9)
    E = [e for e in alle if rng.random() < dens]
    adj = adj_of(E, n)
    for s, t in itertools.permutations(range(n), 2):
        cap, S, T = plain_network(n, E, s, t)
        flow, aug = ford_fulkerson(cap, S, T, rng=rng)
        k = flow_value(flow, cap, S, T)
        cases += 1
        if k is None or k != max_edge_disjoint_brute(adj, n, s, t):
            bad_val += 1
            continue
        paths = peel_trails(flow, S, T)
        if len(paths) != k or not valid_paths(paths, E, s, t, edge_version=True):
            bad_paths += 1
        flow2, added = add_cycles(flow, S, T, rng)
        cyc_added += added
        paths2 = peel_trails(flow2, S, T)
        if flow_value(flow2, cap, S, T) != k or len(paths2) != k or not valid_paths(paths2, E, s, t, edge_version=True):
            bad_cyc += 1
check(bad_val == 0, f"kantversionen: flödets värde = största antalet kantdisjunkta stigar (uttömmande sökning), {cases} fall")
check(bad_paths == 0 and bad_cyc == 0,
      f"kantversionen: stigarna kan dras ut ur flödet, även efter {cyc_added} tillagda flödescykler")


# Verifieraren som bara får kanterna: maxflöde för varje par
def flow_verifier(edges, n, need=2):
    for s in range(n):
        for t in range(s + 1, n):
            cap, S, T = split_network(n, edges, s, t)
            flow, _ = ford_fulkerson(cap, S, T)
            if flow_value(flow, cap, S, T) < need:
                return False
    return True


tot = bad = 0
for n in range(3, 7):
    for sub in itertools.combinations(list(itertools.combinations(range(n), 2)), n):
        tot += 1
        bad += flow_verifier(sub, n) != (sub in GOOD[n])
check(bad == 0, f"verifieraren med enbart kanter godkänner precis hamiltoncyklerna ({tot} delgrafer med n kanter, n = 3..6)")

# ---------------------------------------------------------------------------
# B3. Budgeten och Hamiltonstig
# ---------------------------------------------------------------------------
print("== B3. Budgeten och Hamiltonstig ==")


def edge_index(m):
    return {e: i for i, e in enumerate(itertools.combinations(range(m), 2))}


def mask_of(edges, idx):
    return sum(1 << idx[(min(a, b), max(a, b))] for a, b in edges)


def ham_path_masks(n, ends=None):
    """Kantmaskerna för alla hamiltonstigar i K_n (med givna ändpunkter om ends anges)."""
    idx = edge_index(n)
    return sorted({mask_of(list(zip(p, p[1:])), idx) for p in itertools.permutations(range(n))
                   if p[0] < p[-1] and (ends is None or (p[0], p[-1]) == ends)})


def is_connected(g, n, alle):
    adj = adj_of([alle[i] for i in range(len(alle)) if g >> i & 1], n)
    seen, stack = 1, [0]
    while stack:
        new = adj[stack.pop()] & ~seen
        seen |= new
        stack.extend(v for v in range(n) if new >> v & 1)
    return seen == (1 << n) - 1


def describe(g, alle):
    return "{" + ", ".join(f"{a + 1}-{b + 1}" for i, (a, b) in enumerate(alle) if g >> i & 1) + "}"


# Delgrafer med en kant för mycket, och med för få
GOODPLUS = {}
for m in range(3, 7):
    alle = list(itertools.combinations(range(m), 2))
    GOODPLUS[m] = {sub for sub in itertools.combinations(alle, m + 1) if all_pairs_two(sub, m)}
    fewer = any(all_pairs_two(sub, m) for b in range(m) for sub in itertools.combinations(alle, b))
    check(not fewer, f"m={m}: ingen delgraf med färre än m kanter ger varje par två disjunkta stigar")


def two_conn_masks(m):
    """(hamiltoncyklerna i K_m, övriga delgrafer med m+1 kanter som klarar T=2) som kantmasker."""
    idx = edge_index(m)
    cyc = [mask_of(c, idx) for c in GOOD[m]]
    extra = [p for p in (mask_of(c, idx) for c in GOODPLUS[m]) if not any(c & p == c for c in cyc)]
    return cyc, extra


# (a) Hamiltoncykel med budgeten B = |V| + 1 i stället för |V|
for n in range(3, 7):
    alle = list(itertools.combinations(range(n), 2))
    cyc, extra = two_conn_masks(n)
    wrong, wrong_exact, first = 0, 0, None
    for g in range(1 << len(alle)):
        ham = any(c & g == c for c in cyc)
        atmost = ham or any(p & g == p for p in extra)
        exact = atmost and bin(g).count("1") >= n + 1
        wrong += atmost != ham
        wrong_exact += exact != ham
        if atmost != ham and (first is None or bin(g).count("1") < bin(first).count("1")):
            first = g
    print(f"  hamiltoncykel med B=|V|+1, n={n}: fel svar för {wrong} av {1 << len(alle)} grafer"
          f" (läsningen 'exakt B': {wrong_exact})" + (f"; minsta motexempel {describe(first, alle)}" if first is not None else ""))
    if n < 5:
        check(wrong == 0, f"n={n}: för så små grafer råkar B=|V|+1 ge rätt svar")
    if n == 5:
        deg = sorted(sum(1 for i, e in enumerate(alle) if first >> i & 1 and v in e) for v in range(n))
        check(wrong > 0 and bin(first).count("1") == 6 and deg == [2, 2, 2, 3, 3] and not has_ham(
            [alle[i] for i in range(len(alle)) if first >> i & 1], n), "n=5: minsta motexemplet är K_{2,3}")

# (b) Hamiltonstig: nytt hörn z med kant till alla, T = 2, B = |V| + 1
tot = 0
for n in range(2, 7):
    m = n + 1  # G + z har hörnen 0..n-1 och z = n
    idxm = edge_index(m)
    alle = list(itertools.combinations(range(n), 2))
    lift = [1 << idxm[e] for e in alle]
    zmask = sum(1 << idxm[(v, n)] for v in range(n))
    cyc = [mask_of(c, idxm) for c in GOOD[m]]
    hp = ham_path_masks(n)
    bad = 0
    for g in range(1 << len(alle)):
        gz = sum(lift[i] for i in range(len(alle)) if g >> i & 1) | zmask
        bad += any(c & gz == c for c in cyc) != any(p & g == p for p in hp)
    tot += 1 << len(alle)
    check(bad == 0, f"hamiltonstig via extra hörn, n={n}: reduktionen stämmer för alla {1 << len(alle)} grafer")
print(f"  sammanlagt {tot} grafer med 2..6 hörn")

# (b') samma reduktion med en kant för mycket: B = |V| + 2
for n in range(2, 6):
    m = n + 1
    idxm = edge_index(m)
    alle = list(itertools.combinations(range(n), 2))
    lift = [1 << idxm[e] for e in alle]
    zmask = sum(1 << idxm[(v, n)] for v in range(n))
    cyc, extra = two_conn_masks(m)
    hp = ham_path_masks(n)
    wrong, first = 0, None
    for g in range(1 << len(alle)):
        gz = sum(lift[i] for i in range(len(alle)) if g >> i & 1) | zmask
        red = any(c & gz == c for c in cyc) or any(p & gz == p for p in extra)
        if red != any(p & g == p for p in hp):
            wrong += 1
            if first is None or bin(g).count("1") < bin(first).count("1"):
                first = g
    print(f"  hamiltonstig med B=|V|+2, n={n}: fel svar för {wrong} av {1 << len(alle)} grafer"
          + (f"; minsta motexempel {describe(first, alle)}" if first is not None else ""))
    if n == 4:
        deg = sorted(sum(1 for i, e in enumerate(alle) if first >> i & 1 and v in e) for v in range(n))
        check(wrong == 4 and deg == [1, 1, 1, 3], "n=4: B=|V|+2 ger fel svar för precis de fyra stjärnorna K_{1,3}")
STAR = [(0, 1), (0, 2), (0, 3)]
STARZ = STAR + [(v, 4) for v in range(4)]
k23 = [(0, 1), (0, 2), (0, 3), (4, 1), (4, 2), (4, 3)]
check(all(e in [(min(a, b), max(a, b)) for a, b in STARZ] for e in [(min(a, b), max(a, b)) for a, b in k23])
      and all_pairs_two([(min(a, b), max(a, b)) for a, b in k23], 5),
      "stjärnan K_{1,3} plus z innehåller K_{2,3}: sex kanter som ger alla par två disjunkta stigar")

# (c) den frestande reduktionen: G oförändrad, T = 1, B = |V| - 1 (svarar ja precis när G är sammanhängande)
for n in range(2, 7):
    alle = list(itertools.combinations(range(n), 2))
    hp = ham_path_masks(n)
    wrong, first = 0, None
    for g in range(1 << len(alle)):
        if is_connected(g, n, alle) != any(p & g == p for p in hp):
            wrong += 1
            if first is None or bin(g).count("1") < bin(first).count("1"):
                first = g
    print(f"  hamiltonstig med T=1, B=|V|-1, n={n}: fel svar för {wrong} av {1 << len(alle)} grafer"
          + (f"; minsta motexempel {describe(first, alle)}" if first is not None else ""))
    if n == 4:
        check(wrong == 4, "n=4: den frestande reduktionen ger fel svar för precis de fyra stjärnorna")

# T = 1: svaret är ja precis när G är sammanhängande och |V|-1 <= B <= |E|
bad = 0
for n in range(2, 6):
    alle = list(itertools.combinations(range(n), 2))
    graphs = range(1 << len(alle)) if n <= 4 else [rng.getrandbits(len(alle)) for _ in range(60)]
    for g in graphs:
        E = [alle[i] for i in range(len(alle)) if g >> i & 1]
        conn = is_connected(g, n, alle)
        for b in range(len(alle) + 2):
            brute = any(is_connected(mask_of(sub, edge_index(n)), n, alle) for sub in itertools.combinations(E, b))
            bad += brute != (conn and n - 1 <= b <= len(E))
check(bad == 0, "T=1: ja precis när G är sammanhängande och |V|-1 <= B <= |E| (alla grafer med 2..4 hörn, 60 med 5)")

# (d) givna ändpunkter s och t: z får bara kanterna z-s och z-t
bad = tot = 0
for n in range(2, 6):
    m = n + 1
    idxm = edge_index(m)
    alle = list(itertools.combinations(range(n), 2))
    lift = [1 << idxm[e] for e in alle]
    cyc = [mask_of(c, idxm) for c in GOOD[m]]
    for s, t in itertools.combinations(range(n), 2):
        hp = ham_path_masks(n, ends=(s, t))
        zmask = (1 << idxm[(s, n)]) | (1 << idxm[(t, n)])
        for g in range(1 << len(alle)):
            gz = sum(lift[i] for i in range(len(alle)) if g >> i & 1) | zmask
            bad += any(c & gz == c for c in cyc) != any(p & g == p for p in hp)
            tot += 1
check(bad == 0, f"hamiltonstig med givna ändpunkter (z granne med bara s och t): rätt i alla {tot} fall, n = 2..5")

# ---------------------------------------------------------------------------
# C. Uppgift 3: Håstads pussel
# ---------------------------------------------------------------------------
print("== C. Håstads pussel ==")


def cards_from_cnf(clauses, n, extra=True):
    """Kort i = (L, R), 1 = igenfyllt. Regler (a)-(f) i facit."""
    m = len(clauses)
    cards = []
    for i in range(1, n + 1):
        L = [1 if i in cl else 0 for cl in clauses]
        R = [1 if -i in cl else 0 for cl in clauses]
        cards.append((L, R))
    if extra:
        cards.append(([0] * m, [1] * m))
    return cards


def stack(cards, flips):
    m = len(cards[0][0])
    Lc, Rc = [0] * m, [0] * m
    for (L, R), f in zip(cards, flips):
        if f:
            L, R = R, L
        Lc = [a | b for a, b in zip(Lc, L)]
        Rc = [a | b for a, b in zip(Rc, R)]
    return Lc, Rc


def solvable(cards):
    for flips in itertools.product([0, 1], repeat=len(cards)):
        Lc, Rc = stack(cards, flips)
        if all(Lc) and all(Rc):
            return flips
    return None


def sat(clauses, n):
    for a in itertools.product([0, 1], repeat=n):
        if all(any((a[abs(l) - 1] == 1) == (l > 0) for l in cl) for cl in clauses):
            return a
    return None


def nae(clauses, n):
    for a in itertools.product([0, 1], repeat=n):
        vals = [[(a[abs(l) - 1] == 1) == (l > 0) for l in cl] for cl in clauses]
        if all(any(v) and not all(v) for v in vals):
            return a
    return None


bad = bad2 = 0
for _ in range(3000):
    n, m = random.randint(1, 5), random.randint(1, 6)
    clauses = [[random.choice([1, -1]) * random.randint(1, n) for _ in range(random.randint(1, 4))] for _ in range(m)]
    s = sat(clauses, n) is not None
    if (solvable(cards_from_cnf(clauses, n)) is not None) != s:
        bad += 1
    if (solvable(cards_from_cnf(clauses, n, extra=False)) is not None) != (nae(clauses, n) is not None):
        bad2 += 1
check(bad == 0, "3000 slumpformler: pusslet (med extrakort) lösbart <=> formeln satisfierbar")
check(bad2 == 0, "3000 slumpformler: pusslet utan extrakort lösbart <=> NAE-satisfierbar")

# godtyckliga kort <-> NAE-SAT
bad = 0
for _ in range(2000):
    n, m = random.randint(1, 5), random.randint(1, 5)
    cards = [([random.randint(0, 1) for _ in range(m)], [random.randint(0, 1) for _ in range(m)]) for _ in range(n)]
    clauses = [[i + 1 for i in range(n) if cards[i][0][j]] + [-(i + 1) for i in range(n) if cards[i][1][j]] for j in range(m)]
    if (solvable(cards) is not None) != (nae(clauses, n) is not None):
        bad += 1
check(bad == 0, "2000 slumpmässiga korthögar: Toys-instans <=> motsvarande NAE-SAT-instans")

# Alice exempel
PHI = [[1, -2], [-1, -2, -4], [2, -4], [-3, 4]]
cards = cards_from_cnf(PHI, 4)
for i, (L, R) in enumerate(cards, 1):
    print(f"  kort c{i}: vänster {L}  höger {R}")
a = (1, 1, 0, 0)
check(all(any((a[abs(l) - 1] == 1) == (l > 0) for l in cl) for cl in PHI), "x=(1,1,0,0) satisfierar phi")
Lc, Rc = stack(cards[:4], [1 - x for x in a])
print("  hög c1..c4 med x=(1,1,0,0): vänster", Lc, "höger", Rc)
check(all(Lc) and Rc == [1, 1, 0, 1], "vänsterkolumnen täckt; höger har ett hål på rad 3")
Lc, Rc = stack(cards, [1 - x for x in a] + [0])
check(all(Lc) and all(Rc), "med extrakortet rättvänt är allt täckt")
inv = (0, 0, 1, 1)
check(not all(any((inv[abs(l) - 1] == 1) == (l > 0) for l in cl) for cl in PHI), "den inverterade tilldelningen (0,0,1,1) satisfierar inte phi")
allsat = [a for a in itertools.product([0, 1], repeat=4) if all(any((a[abs(l) - 1] == 1) == (l > 0) for l in cl) for cl in PHI)]
print("  satisfierande tilldelningar:", allsat)
# hela högen vänd (extrakortet vänt): också en lösning, och motsvarar inverterad tilldelning
Lc, Rc = stack(cards, [x for x in a] + [1])
check(all(Lc) and all(Rc), "vänder man hela högen (alla kort) är pusslet fortfarande löst")
# en klausul där alla literaler är sanna: rad 3
print("  klausul 3 (x2 v -x4) med x2=1, x4=0: båda literalerna sanna -> ingen falsk literal -> hål till höger")

# Träpusslet på fotot
WOOD = {  # (vänsterkolumn, högerkolumn), 1 = igenfyllt; avläst från fotot
    "a": ([1, 0, 0], [0, 1, 0]),
    "b": ([1, 0, 1], [0, 1, 0]),
    "c": ([0, 1, 0], [0, 0, 1]),
    "extra": ([0, 0, 0], [1, 1, 1]),
}
names = ["a", "b", "c"]
wcl = [[(i + 1) for i, nme in enumerate(names) if WOOD[nme][0][j]] + [-(i + 1) for i, nme in enumerate(names) if WOOD[nme][1][j]] for j in range(3)]
print("  träpusslets formel:", wcl)
check(wcl == [[1, 2], [3, -1, -2], [2, -3]] or sorted(map(sorted, wcl)) == sorted(map(sorted, [[1, 2], [-1, -2, 3], [2, -3]])), "träpusslet = (a v b)(-a v -b v c)(b v -c)")
wsat = [a for a in itertools.product([0, 1], repeat=3) if all(any((a[abs(l) - 1] == 1) == (l > 0) for l in cl) for cl in wcl)]
print("  satisfierande (a,b,c):", wsat)
wcards = [WOOD[k] for k in ["a", "b", "c", "extra"]]
wsol = [f for f in itertools.product([0, 1], repeat=4) if all(stack(wcards, f)[0]) and all(stack(wcards, f)[1])]
print("  läggningar som löser träpusslet (1 = vänt) för (a,b,c,extra):", wsol)
check(len(wsol) == 2 * len(wsat), "varje satisfierande tilldelning ger två läggningar (spegelbilder)")

# ---------------------------------------------------------------------------
# D. Uppgift 4: schemaläggning
# ---------------------------------------------------------------------------
print("== D. Schemaläggning ==")


def colorable(n, edges, k):
    col = [-1] * n
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    def rec(i):
        if i == n:
            return True
        for c in range(k):
            if all(col[w] != c for w in adj[i]):
                col[i] = c
                if rec(i + 1):
                    return True
                col[i] = -1
        return False

    return list(col) if rec(0) else None


# Bildens exempel: 7 jobb
JOBS = 7
CONF = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 5), (5, 6), (2, 6)]
c3 = colorable(JOBS, CONF, 3)
print("  exempel: trefärgning (jobb 1..7 -> tidsenhet):", [c + 1 for c in c3])
check(c3 is not None and colorable(JOBS, CONF, 2) is None, "exemplet går på 3 tidsenheter men inte på 2")
want = [0, 1, 2, 0, 1, 2, 0]
check(all(want[u] != want[v] for u, v in CONF), "schemat på bilden (1,2,3,1,2,3,1) är giltigt")
K4 = list(itertools.combinations(range(4), 2))
check(colorable(4, K4, 3) is None and colorable(4, K4, 4) is not None, "K4: fyra jobb i inbördes konflikt kräver 4 tidsenheter")
C5 = [(i, (i + 1) % 5) for i in range(5)]
check(colorable(5, C5, 2) is None and colorable(5, C5, 3) is not None, "C5: udda cykel, går inte på 2 men på 3")

bad = 0
for _ in range(400):
    n = random.randint(1, 7)
    E = [e for e in itertools.combinations(range(n), 2) if random.random() < 0.45]
    base = colorable(n, E, 3) is not None
    for k in (4, 5):
        extra = list(range(n, n + k - 3))
        E2 = E + [(u, z) for z in extra for u in range(n)] + list(itertools.combinations(extra, 2))
        if (colorable(n + k - 3, E2, k) is not None) != base:
            bad += 1
check(bad == 0, "400 slumpgrafer: G trefärgbar <=> G + (k-3) blockerarjobb går på k tidsenheter (k=4,5)")


# k=2 med BFS, och med p processorer (DP över komponenter) mot brute force
def two_sched_bfs(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    t = [0] * n
    comps = []
    for s in range(n):
        if t[s]:
            continue
        t[s] = 1
        q, cnt = [s], [0, 1, 0]
        for u in q:
            for w in adj[u]:
                if not t[w]:
                    t[w] = 3 - t[u]
                    cnt[t[w]] += 1
                    q.append(w)
                elif t[w] == t[u]:
                    return None, None
        comps.append((cnt[1], cnt[2]))
    return t, comps


def two_sched_limited(n, edges, p):
    t, comps = two_sched_bfs(n, edges)
    if t is None:
        return False
    reach = {0}
    for a, b in comps:
        reach = {r + a for r in reach} | {r + b for r in reach}
    return any(r <= p and n - r <= p for r in reach)


bad = bad2 = 0
for _ in range(600):
    n = random.randint(1, 8)
    E = [e for e in itertools.combinations(range(n), 2) if random.random() < 0.25]
    t, _ = two_sched_bfs(n, E)
    if (t is not None) != (colorable(n, E, 2) is not None):
        bad += 1
    p = random.randint(1, n)
    brute = any(all(c[u] != c[v] for u, v in E) and sum(c) <= p and n - sum(c) <= p for c in itertools.product([0, 1], repeat=n))
    if brute != two_sched_limited(n, E, p):
        bad2 += 1
check(bad == 0, "600 slumpinstanser: BFS-tvåfärgning = brute force för k=2")
check(bad2 == 0, "600 slumpinstanser: k=2 med p processorer, DP över komponenter = brute force")

# ---------------------------------------------------------------------------
# E. Uppgift 5: lapptäcke
# ---------------------------------------------------------------------------
print("== E. Lapptäcke ==")
print("  bredd=höjd  bitar(b+h)  yta")
for e in range(0, 10, 1):
    b = 10 ** e
    print(f"  {b:>12} {2 * b.bit_length():>4} {b * b:>22}")
km = 10 ** 9  # 1000 km i mm
print("  1000 km = 10^9 mm:", km.bit_length(), "bitar per tal; täcket 10^18 rutor")


def overlap(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return ax1 < bx2 and bx1 < ax2 and ay1 < by2 and by1 < ay2


def cells(r):
    return {(x, y) for x in range(r[0], r[2]) for y in range(r[1], r[3])}


bad = 0
for _ in range(20000):
    rs = []
    for _ in range(2):
        x1, y1 = random.randint(0, 6), random.randint(0, 6)
        rs.append((x1, y1, x1 + random.randint(1, 5), y1 + random.randint(1, 5)))
    if overlap(*rs) != bool(cells(rs[0]) & cells(rs[1])):
        bad += 1
check(bad == 0, "intervalltestet = rutvis överlapp för 20000 slumppar")
# korset: inget hörn av den ena ligger i den andra
A_, B_ = (0, 2, 6, 4), (2, 0, 4, 6)
corners = lambda r: [(r[0], r[1]), (r[2], r[1]), (r[0], r[3]), (r[2], r[3])]
inside = lambda p, r: r[0] < p[0] < r[2] and r[1] < p[1] < r[3]
check(overlap(A_, B_) and not any(inside(p, B_) for p in corners(A_)) and not any(inside(p, A_) for p in corners(B_)),
      "korset: lapparna överlappar men inget hörn ligger inuti den andra")

# kriteriet: innanför + parvis disjunkta + total yta = BH  <=>  exakt täckning
bad = 0
for _ in range(20000):
    Bq, Hq = random.randint(1, 5), random.randint(1, 5)
    rs = []
    for _ in range(random.randint(1, 5)):
        x1, y1 = random.randint(-1, Bq), random.randint(-1, Hq)
        rs.append((x1, y1, x1 + random.randint(1, 4), y1 + random.randint(1, 4)))
    insideq = all(0 <= r[0] and r[2] <= Bq and 0 <= r[1] and r[3] <= Hq for r in rs)
    disj = all(not overlap(rs[i], rs[j]) for i in range(len(rs)) for j in range(i + 1, len(rs)))
    area = sum((r[2] - r[0]) * (r[3] - r[1]) for r in rs) == Bq * Hq
    crit = insideq and disj and area
    cover = {}
    for r in rs:
        for c in cells(r):
            cover[c] = cover.get(c, 0) + 1
    exact = all(cover.get((x, y), 0) == 1 for x in range(Bq) for y in range(Hq)) and all(
        0 <= x < Bq and 0 <= y < Hq for (x, y) in cover)
    if crit != exact:
        bad += 1
check(bad == 0, "20000 slumpmässiga placeringar: (innanför, disjunkta, yta = BH) <=> täcket täcks exakt en gång")


def tile(patches, Bq, Hq):
    """Brute force: kan en delmängd av lapparna (med vridning) täcka Bq x Hq? Returnerar en läggning eller None."""
    grid = [[-1] * Bq for _ in range(Hq)]
    used = [False] * len(patches)
    out = []

    def rec():
        pos = next(((x, y) for y in range(Hq) for x in range(Bq) if grid[y][x] < 0), None)
        if pos is None:
            return True
        x, y = pos
        tried = set()
        for i, (b, h) in enumerate(patches):
            if used[i]:
                continue
            for rot, (w, g) in enumerate(((b, h), (h, b))):
                if (w, g) in tried or (rot == 1 and b == h):
                    continue
                if x + w <= Bq and y + g <= Hq and all(grid[yy][xx] < 0 for yy in range(y, y + g) for xx in range(x, x + w)):
                    for yy in range(y, y + g):
                        for xx in range(x, x + w):
                            grid[yy][xx] = i
                    used[i] = True
                    out.append((i, x, y, rot))
                    if rec():
                        return True
                    out.pop()
                    used[i] = False
                    for yy in range(y, y + g):
                        for xx in range(x, x + w):
                            grid[yy][xx] = -1
            tried.add((b, h))
            tried.add((h, b))
        return False

    return list(out) if rec() else None


def subset_sum(ps, K):
    return any(sum(c) == K for r in range(len(ps) + 1) for c in itertools.combinations(ps, r))


bad = 0
for _ in range(1500):
    ps = [random.randint(1, 7) for _ in range(random.randint(1, 6))]
    Kq = random.randint(1, 16)
    if subset_sum(ps, Kq) != (tile([(p, 1) for p in ps], Kq, 1) is not None):
        bad += 1
check(bad == 0, "1500 slumpinstanser: delmängdssumma ja <=> K x 1-lapptäcke finns (vridning tillåten)")
EX = [1, 1, 2, 3, 5, 8]
solsEX = sorted({tuple(sorted(c)) for r in range(7) for c in itertools.combinations(EX, r) if sum(c) == 10})
print("  {1,1,2,3,5,8}, K=10: delmängder (som multimängder):", solsEX)
print("  läggning:", tile([(p, 1) for p in EX], 10, 1))

# 3-PARTITION -> lapptäcke (stark NP-svårighet), små fall
def three_partition(a, T):
    a = sorted(a)
    m = len(a) // 3
    if sum(a) != m * T:
        return False

    def rec(rest):
        if not rest:
            return True
        first = rest[0]
        for i in range(1, len(rest)):
            for j in range(i + 1, len(rest)):
                if first + rest[i] + rest[j] == T:
                    nxt = [rest[k] for k in range(len(rest)) if k not in (0, i, j)]
                    if rec(nxt):
                        return True
        return False

    return rec(a)


bad = tested = 0
for _ in range(4000):
    m = 2
    T = random.randint(8, 14)
    a = [random.randint(T // 4 + 1, (T - 1) // 2) for _ in range(3 * m)]
    if sum(a) != m * T:
        continue
    tested += 1
    c = m + 1
    if three_partition(a, T) != (tile([(c * x, 1) for x in a], c * T, m) is not None):
        bad += 1
check(bad == 0 and tested > 50, f"{tested} små 3-PARTITION-instanser: ja <=> lapptäcke (m+1)T x m finns")

print()
print("ALLT OK" if OK else "NÅGOT ÄR FEL")
sys.exit(0 if OK else 1)
