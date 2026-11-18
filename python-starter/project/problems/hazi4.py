from project.problem import Problem
import argparse
import re
from collections import Counter

class RegexProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument(
            '--rgx',
            type=int,
            choices=range(1, 6),
            metavar='1-5'
        )

    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.rgx)

    def problem1(self, data):
        patterns = [
            # 1. 10. hónap 15-én létrejött sorok
            r'^10-15\b',
            # 2. 10. hónap 15-én 10:18:51-kor létrejött sorok
            r'^10-15\s+10:18:51\.',
            # 3. 51 másodperckor létrejött sorok (mindegy a perc)
            r'^\d{2}-\d{2}\s+\d{2}:\d{2}:51\.',
            # 4. lowmemorykiller taget tartalmazó sorok
            r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+\d+\s+\d+\s+[VDIWEFS]\s+lowmemorykiller\s*:',
            # 5. 10:18:51-kor keletkező 221-es process id-jú sorok
            r'^\d{2}-\d{2}\s+10:18:51\.\d{3}\s+221\s+\d+\s+[VDIWEFS]\b',
            # 6. összes hibát tartalmazó sor (E)
            r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+\d+\s+\d+\s+E\b',
            # 7. összes warning (W) amit a PackageManager küld
            r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+\d+\s+\d+\s+W\s+PackageManager\s*:',
            # 8. összes ExoPlayer-es debug (D) infó (ExoPlayer vagy ExoPlayerImpl stb. tag)
            r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+\d+\s+\d+\s+D\s+[^\s:]*ExoPlayer[^\s:]*\s*:',
            # 9. összes java állomány pozíciót tartalmazó hiba és warning (E/W + .java:)
            r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+\d+\s+\d+\s+[EW]\b.*\.java:\d+',
            # 10. Thread szó a message részben (nem a tagben: a tag és a ':' után)
            r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+\d+\s+\d+\s+[VDIWEFS]\s+[^:]+:.*\bThread\b'
        ]

        counts = [str(len(re.findall(p, data, re.MULTILINE))) for p in patterns]
        result = "\n".join(counts)
        return result

    def problem2(self, data):
        pattern = r'\bE\b.*?\bat\s+[\w.$]+\(([^():]+\.java):\d+\)'
        result = re.findall(pattern, data)
        return result

    def problem3(self, data):
        pattern = r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+(\d+)\s+\d+\s+[VDIWEFS]\b'
        pids = re.findall(pattern, data, re.MULTILINE)
        unique_pids = dict.fromkeys(pids)
        result = "\n".join(unique_pids)
        return result

    def problem4(self, data):
        pattern = r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+(\d+)\s+\d+\s+E\b'
        error_pids = re.findall(pattern, data, re.MULTILINE)

        if not error_pids:
            return ""

        # Megszámolja, melyik PID hányszor fordult elő hibasorban,
        # és visszaadja a legmagasabb előfordulású (pid, darabszám) párost.
        top_pid, count = Counter(error_pids).most_common(1)[0]
        result = f"PID={top_pid} ({count} errors)"
        return result

    def problem5(self, data):
        pattern = r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+(\d+)\s+\1\s+E\b'
        matches = re.findall(pattern, data, re.MULTILINE)
        result = len(matches)
        return result

    def run(self, args):
        """
        Run the program
        """
        # Access the input and output file paths
        input_file = args.input
        output_file = args.output

        # Read the numbers
        with open(input_file, 'r') as f:
            data = f.read()

        # Feladatok feldolgozása a --rgx kapcsoló alapján
        match args.rgx:
            case 1:
                result = self.problem1()
            case 2:
                result = self.problem2()
            case 3:
                result = self.problem3()
            case 4:
                result = self.problem4()
            case 5:
                result = self.problem5()

        # Write the result into the file
        with open(output_file, 'w') as f:
            f.write(str(result))
