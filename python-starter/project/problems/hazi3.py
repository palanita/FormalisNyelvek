import argparse
from project.problem import Problem


class MinimizationProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--mini', action='store_true', help='Minimalizálás végrehajtása')

    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.mini)

    def run(self, args):
        """
        Run the program
        """
        input_file = args.input
        output_file = args.output

        with open(input_file, 'r', encoding='utf-8') as f:
            sorok = [sor.strip() for sor in f if sor.strip()]

            if len(sorok) < 4:
                raise ValueError("A bemeneti fájl érvénytelen vagy hiányos formátumú.")

            eredeti_allapotok = sorok[0].split()
            abece = sorok[1].split()
            kezdoallapot = sorok[2]
            vegallapotok = set(sorok[3].split())

            # Alapvető hibakezelés: kezdőállapot és végállapotok ellenőrzése
            if kezdoallapot not in eredeti_allapotok:
                raise ValueError(f"A kezdőállapot ({kezdoallapot}) nincs felsorolva az érvényes állapotok között.")
            for v in vegallapotok:
                if v not in eredeti_allapotok:
                    raise ValueError(f"A végállapot ({v}) nincs felsorolva az érvényes állapotok között.")

            # Átmenetek beolvasása és validálása
            atmenet_map = {}  # (honnan, szimbolum) -> hova
            for sor in sorok[4:]:
                elemek = sor.split()
                if len(elemek) >= 3:
                    honnan, szimbolum, hova = elemek[0], elemek[1], elemek[2]

                    if honnan not in eredeti_allapotok:
                        raise ValueError(f"Érvénytelen forrásállapot az átmenetben: {honnan}")
                    if hova not in eredeti_allapotok:
                        raise ValueError(f"Érvénytelen célállapot az átmenetben: {hova}")
                    if szimbolum not in abece:
                        raise ValueError(f"Érvénytelen szimbólum az átmenetben: {szimbolum}")

                    atmenet_map[(honnan, szimbolum)] = hova

            rendezett_abece = sorted(set(abece))

            # --- 1. LÉPÉS: Elérhetőségi szűrés ---
            elerheto = set()
            queue = [kezdoallapot]
            elerheto.add(kezdoallapot)
            while queue:
                curr = queue.pop(0)
                for symb in rendezett_abece:
                    nxt = atmenet_map.get((curr, symb))
                    if nxt and nxt not in elerheto:
                        elerheto.add(nxt)
                        queue.append(nxt)

            allapotok_lista = sorted(list(elerheto), key=lambda x: int(''.join(filter(str.isdigit, x))) if any(
                char.isdigit() for char in x) else x)
            n = len(allapotok_lista)

            # --- 2. LÉPÉS: Háromszögmátrix (állapotpár-táblázat) inicializálása ---
            # distinguished[i][j] jelöli, hogy az allapotok_lista[i] és allapotok_lista[j] meg van-e különböztetve (ahol i < j)
            distinguished = [[False] * n for _ in range(n)]

            # Kezdeti megkülönböztetés: ha az egyik végállapot, a másik pedig nem
            for i in range(n):
                for j in range(i + 1, n):
                    st1 = allapotok_lista[i]
                    st2 = allapotok_lista[j]
                    is_st1_final = st1 in vegallapotok
                    is_st2_final = st2 in vegallapotok
                    if is_st1_final != is_st2_final:
                        distinguished[i][j] = True

            # --- 3. LÉPÉS: Iteratív kitöltés az átmenetek alapján ---
            changed = True
            while changed:
                changed = False
                for i in range(n):
                    for j in range(i + 1, n):
                        if not distinguished[i][j]:
                            st1 = allapotok_lista[i]
                            st2 = allapotok_lista[j]
                            # Megvizsgáljuk az összes szimbólum szerinti átmenetet
                            for symb in rendezett_abece:
                                nxt1 = atmenet_map.get((st1, symb))
                                nxt2 = atmenet_map.get((st2, symb))

                                # Ha valamelyik átmenet nem létezik (hiányos automata), vagy kezeljük a nem teljes automata esetét:
                                # (A feladat elején említve van a determinisztikussá és teljessé tétel is, de itt feltételezzük,
                                # hogy a megadott párok vagy mindkettő léteznek, vagy ha az egyik hiányzik, azt kezelni kell.
                                # Ha mindkettő létezik, megnézzük a mátrixban lévő értéküket.)
                                if nxt1 and nxt2 and nxt1 != nxt2:
                                    # Megkeressük nxt1 és nxt2 indexét az allapotok_lista-ban
                                    idx1 = allapotok_lista.index(nxt1)
                                    idx2 = allapotok_lista.index(nxt2)
                                    # Indexek sorrendje: mindig idx_A < idx_B legyen a mátrix eléréséhez
                                    row, col = min(idx1, idx2), max(idx1, idx2)
                                    if distinguished[row][col]:
                                        distinguished[i][j] = True
                                        changed = True
                                        break
                                elif (nxt1 is None) != (nxt2 is None):
                                    # Ha az egyik átmenet létezik, a másik nem, akkor megkülönböztetettek
                                    distinguished[i][j] = True
                                    changed = True
                                    break

            # --- 4. LÉPÉS: Ekvivalencia-osztályok képzése a meg nem különböztetett párok alapján ---
            parent = list(range(n))

            def find(i: int) -> int:
                if parent[i] == i:
                    return i
                parent[i] = find(parent[i])
                return parent[i]

            def union(i: int, j: int) -> None:
                root_i = find(i)
                root_j = find(j)
                if root_i != root_j:
                    parent[root_j] = root_i

            for i in range(n):
                for j in range(i + 1, n):
                    if not distinguished[i][j]:
                        union(i, j)

            # Osztályok összegyűjtése indexek alapján
            osztalyok_dict: dict[int, list[str]] = {}
            for i in range(n):
                root = find(i)
                if root not in osztalyok_dict:
                    osztalyok_dict[root] = []
                osztalyok_dict[root].append(allapotok_lista[i])

            # --- 5. LÉPÉS: Új állapotnevek hozzárendelése ---
            # Az összevont állapotok új neve az összevont állapotok közül a legkisebb nevet kapja (s-es formátumban)
            osztaly_map = {}  # eredeti_allapot -> új_név
            uj_allapotok_set = set()

            for root, csoport in osztalyok_dict.items():
                # Eredeti állapotok rendezése (ha pl. q1, q5 -> q1 a legkisebb)
                # Tegyük fel, hogy a nevek q-val vagy más sztringgel kezdődnek, de számmal végződnek,
                # vagy sima lexikografikus ill. numerikus rendezés:
                sorted_csoport = sorted(csoport, key=lambda x: int(''.join(filter(str.isdigit, x))) if any(
                    char.isdigit() for char in x) else x)
                reprezentans = sorted_csoport[0]

                szam_resz = ''.join(filter(str.isdigit, reprezentans))
                uj_nev = f"s{szam_resz}"
                uj_allapotok_set.add(uj_nev)

                for st in csoport:
                    osztaly_map[st] = uj_nev

            osszes_dfa_allapot = sorted(list(uj_allapotok_set), key=lambda x: int(x[1:]))
            elso_sor = " ".join(osszes_dfa_allapot)
            masodik_sor = " ".join(rendezett_abece)
            harmadik_sor = osztaly_map[kezdoallapot]

            uj_vegallapotok = set()
            for st in vegallapotok:
                if st in osztaly_map:
                    uj_vegallapotok.add(osztaly_map[st])
            negyedik_sor = " ".join(sorted(list(uj_vegallapotok), key=lambda x: int(x[1:])))

            # Új átmenetek generálása és deduplikálása
            dfa_atmenetek = set()
            for root, csoport in osztalyok_dict.items():
                reprezentans = csoport[0]  # Bármelyik elem jó reprezentánsnak az osztályból
                honnan_uj = osztaly_map[reprezentans]
                for szimbolum in rendezett_abece:
                    hova_regi = atmenet_map.get((reprezentans, szimbolum))
                    if hova_regi and hova_regi in osztaly_map:
                        hova_uj = osztaly_map[hova_regi]
                        dfa_atmenetek.add((honnan_uj, szimbolum, hova_uj))

            # Átmenetek rendezése a megadott szabály szerint:
            # - először a kiindulási állapotok alapján (számérték szerint)
            # - majd az átmenet címkéje (szimbólum) szerint
            # - végül a célállapot alapján (számérték szerint)
            rendezett_atmenetek = sorted(
                list(dfa_atmenetek),
                key=lambda x: (int(x[0][1:]), x[1], int(x[2][1:]))
            )
            atmenet_sorok = [f"{honnan} {szimbolum} {hova}" for honnan, szimbolum, hova in rendezett_atmenetek]

            kimenet_tartalom = [
                                   elso_sor,
                                   masodik_sor,
                                   harmadik_sor,
                                   negyedik_sor
                               ] + atmenet_sorok

            result = "\n".join(kimenet_tartalom)

        # Írás a kimeneti fájlba
        with open(output_file, 'w', encoding='utf-8') as f:
            if result:
                f.write(result + "\n")
            else:
                f.write("")