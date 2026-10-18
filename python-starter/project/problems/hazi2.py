import argparse
from collections import deque
from project.problem import Problem


class AutomataProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--det', action='store_true', help='Determinizálás végrehajtása')

    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.det)

    def run(self, args):
        """
        Run the program
        """
        input_file = args.input
        output_file = args.output
        result = ""

        # Csak akkor futtatjuk a determinizálást, ha a --det kapcsoló meg van adva

        with open(input_file, 'r') as f:
            # Sorok beolvasása, a felesleges üres sorok és szóközök szűrésével
            sorok = [sor.strip() for sor in f if sor.strip()]

            if len(sorok) < 4:
                raise ValueError("A bemeneti fájl érvénytelen vagy hiányos formátumú.")

            allapotok = set(sorok[0].split())
            abece = sorok[1].split()  # Sorrend megőrzése / ábécé elemei
            kezdoallapot = sorok[2]
            vegallapotok = set(sorok[3].split())

            # Alapvető hibakezelés: kezdőállapot ellenőrzése
            if kezdoallapot not in allapotok:
                raise ValueError(f"A kezdőállapot ({kezdoallapot}) nincs felsorolva az érvényes állapotok között.")

            # Átmenetek beolvasása és validálása
            atmenet_map = {}
            for sor in sorok[4:]:
                elemek = sor.split()
                if len(elemek) >= 3:
                    honnan, szimbolum, hova = elemek[0], elemek[1], elemek[2]

                    # Hibakezelés: ellenőrizzük, hogy az állapotok és a jelek érvényesek-e
                    if honnan not in allapotok:
                        raise ValueError(f"Érvénytelen forrásállapot az átmenetben: {honnan}")
                    if hova not in allapotok:
                        raise ValueError(f"Érvénytelen célállapot az átmenetben: {hova}")
                    if szimbolum not in abece:
                        raise ValueError(f"Érvénytelen szimbólum az átmenetben: {szimbolum}")

                    if (honnan, szimbolum) not in atmenet_map:
                        atmenet_map[(honnan, szimbolum)] = set()
                    atmenet_map[(honnan, szimbolum)].add(hova)

            # --- DETERMINIZÁLÁS (Subset Construction) ---
            start_set = frozenset([kezdoallapot])
            state_names = {start_set: "s0"}
            state_counter = 1

            queue = deque([start_set])
            visited = {start_set}

            dfa_atmenetek = []
            dfa_vegallapotok = set()

            rendezett_abece = sorted(set(abece))

            while queue:
                current_set = queue.popleft()
                current_name = state_names[current_set]

                if any(st in vegallapotok for st in current_set):
                    dfa_vegallapotok.add(current_name)

                for szimbolum in rendezett_abece:
                    next_set = set()
                    for st in current_set:
                        if (st, szimbolum) in atmenet_map:
                            next_set.update(atmenet_map[(st, szimbolum)])

                    if next_set:
                        frozen_next = frozenset(next_set)
                        if frozen_next not in state_names:
                            state_names[frozen_next] = f"s{state_counter}"
                            state_counter += 1

                        next_name = state_names[frozen_next]
                        dfa_atmenetek.append((current_name, szimbolum, next_name))

                        if frozen_next not in visited:
                            visited.add(frozen_next)
                            queue.append(frozen_next)

            # --- KIMENET FORMÁZÁSA ---
            osszes_dfa_allapot = sorted(state_names.values(), key=lambda x: int(x[1:]))
            elso_sor = " ".join(osszes_dfa_allapot)
            masodik_sor = " ".join(rendezett_abece)
            harmadik_sor = "s0"

            rendezett_vegallapotok = sorted(dfa_vegallapotok, key=lambda x: int(x[1:]))
            negyedik_sor = " ".join(rendezett_vegallapotok)

            # Átmenetek rendezése (forrás, szimbólum, cél szerint)
            dfa_atmenetek.sort(key=lambda x: (int(x[0][1:]), x[1], int(x[2][1:])))
            atmenet_sorok = [f"{honnan} {szimbolum} {hova}" for honnan, szimbolum, hova in dfa_atmenetek]

            kimenet_tartalom = [
                elso_sor,
                masodik_sor,
                harmadik_sor,
                negyedik_sor
            ] + atmenet_sorok

            result = "\n".join(kimenet_tartalom)

        # Írás a fájlba
        with open(output_file, 'w') as f:
            if result:
                f.write(result + "\n")
            else:
                f.write("")