from project.problem import Problem
import argparse


class AutomataProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--check', nargs='+')

    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.check)

    def run(self, args):
        """
        Run the program
        """
        # Access the input and output file paths
        input_file = args.input
        output_file = args.output

        # Read the file
        with open(input_file, 'r') as f:
            # Sorok beolvasása, a felesleges üres sorok és szóközök szűrésével
            sorok = [sor.strip() for sor in f if sor.strip()]

        allapotok = sorok[0].split()
        abece = sorok[1].split()
        kezdoallapot = sorok[2]
        vegallapotok = sorok[3].split()

        # Átmenetek (honnan, mivel, hova)
        atmenetek = []
        for sor in sorok[4:]:
            elemek = sor.split()
            if len(elemek) >= 3:
                honnan, szimbolum, hova = elemek[0], elemek[1], elemek[2]
                atmenetek.append((honnan, szimbolum, hova))

        # Process
        eredmenyek = []

        #van-e check és true
        if hasattr(args, 'check') and args.check:
            szavak = args.check[0].split(',')

            for szo in szavak:
                pozicio = kezdoallapot
                elfogadva = True

                for elem in szo:
                    talalt_atmenetet = False

                    # Végigmegyünk az átmeneteken
                    for honnan, szimbolum, hova in atmenetek:
                        if pozicio == honnan and elem == szimbolum:
                            pozicio = hova
                            talalt_atmenetet = True
                            break  # Megtaláltuk a helyes átmenetet erre a karakterre, kilépünk az átmenetekből

                    # Ha a teljes átmenetlista végigjárása után sem találtunk érvényes lépést:
                    if not talalt_atmenetet:
                        elfogadva = False
                        break  # Nem érdemes tovább olvasni a szót, mert elakadtunk

                # Ellenőrzés, hogy a szó végén végállapotban vagyunk-e
                if elfogadva and pozicio in vegallapotok:
                    eredmenyek.append("IGEN")
                else:
                    eredmenyek.append("NEM")

            result = "\n".join(eredmenyek)
        else:
            result = ""

        # Write the result into the file
        with open(output_file, 'w') as f:
            f.write(str(result))