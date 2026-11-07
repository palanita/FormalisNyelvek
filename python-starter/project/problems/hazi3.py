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

            # --- MINIMALIZÁLÁS (Moore-algoritmus / Partíció finomítás) ---
            allapotok_lista = list(eredeti_allapotok)

            # Elérhetőségi szűrés (csak azokat az állapotokat tartjuk meg, amelyek elérhetőek a kezdőállapotból)
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

            aktiv_allapotok = [st for st in allapotok_lista if st in elerheto]

            # Kezdeti partíciók: Végállapotok és Nem-végállapotok
            P = [
                set(st for st in aktiv_allapotok if st in vegallapotok),
                set(st for st in aktiv_allapotok if st not in vegallapotok)
            ]
            P = [g for g in P if g]  # Üres csoportok kiszűrése
            W = list(P)

            while W:
                A = W.pop(0)
                for c in rendezett_abece:
                    # Előképek gyűjtése c szimbólummal
                    X = set()
                    for s in aktiv_allapotok:
                        nxt = atmenet_map.get((s, c))
                        if nxt in A:
                            X.add(s)

                    new_P = []
                    for Y in P:
                        intersection = Y.intersection(X)
                        difference = Y.difference(X)
                        if intersection and difference:
                            new_P.append(intersection)
                            new_P.append(difference)
                            if Y in W:
                                W.remove(Y)
                                W.append(intersection)
                                W.append(difference)
                            else:
                                if len(intersection) <= len(difference):
                                    W.append(intersection)
                                else:
                                    W.append(difference)
                        else:
                            new_P.append(Y)
                    P = new_P

            # Az egyes ekvivalencia-osztályok rendezése és új név hozzárendelése
            # Az új név az osztály legkisebb eredeti neve lesz
            osztaly_map = {}  # eredeti_allapot -> új_név (s-el kezdődve)
            uj_allapotok_set = set()

            for csoport in P:
                # Eredeti állapotok rendezése (ha pl. q1, q5 -> q1 a legkisebb)
                # Tegyük fel, hogy a nevek q-val vagy más sztringgel kezdődnek, de számmal végződnek,
                # vagy sima lexikografikus ill. numerikus rendezés:
                sorted_csoport = sorted(list(csoport), key=lambda x: int(''.join(filter(str.isdigit, x))) if any(
                    char.isdigit() for char in x) else x)
                reprezentans = sorted_csoport[0]

                # A feladat szerint: "Az összevont állapotok új neve az összevont állapotok közül a legkisebb nevet kapja
                # (például, ha q1 és q5 összevonódik, az új állapot neve s1 lesz)."
                # Ha pl. q1 volt a legkisebb, akkor s1 lesz.
                szam_resz = ''.join(filter(str.isdigit, reprezentans))
                uj_nev = f"s{szam_resz}"
                uj_allapotok_set.add(uj_nev)

                for st in csoport:
                    osztaly_map[st] = uj_nev

            # Új állapotok rendezése s index szerint
            osszes_dfa_allapot = sorted(list(uj_allapotok_set), key=lambda x: int(x[1:]))
            elso_sor = " ".join(osszes_dfa_allapot)
            masodik_sor = " ".join(rendezett_abece)
            harmadik_sor = osztaly_map[kezdoallapot]

            # Új végállapotok meghatározása
            uj_vegallapotok = set()
            for st in vegallapotok:
                if st in osztaly_map:
                    uj_vegallapotok.add(osztaly_map[st])
            negyedik_sor = " ".join(sorted(list(uj_vegallapotok), key=lambda x: int(x[1:])))

            # Új átmenetek generálása és deduplikálása
            dfa_atmenetek = set()
            for csoport in P:
                reprezentans = list(csoport)[0]
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