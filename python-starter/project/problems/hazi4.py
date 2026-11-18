from project.problem import Problem
import argparse
import re
from collections import Counter

class RegexProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--rgx',
            type=int,
            choices=range(1, 6),
            metavar='1-5'
        )

    def is_chosen_problem(self, args):
        return bool(args.rgx)

    def problem1(self, data):
        raw_patterns = [
            # 1. 10. hónap 15-én 10:18:51-kor létrejött sorok
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
        # Előre lefordítjuk a mintákat a gyorsabb futásért
        patterns = [re.compile(p) for p in raw_patterns]
        counts = [0] * len(patterns)

        for line in data:
            for i, pattern in enumerate(patterns):
                if pattern.search(line):
                    counts[i] += 1

        return "\n".join(str(c) for c in counts)

    def problem2(self, lines):
        pattern = re.compile(r'\bE\b.*?\bat\s+[\w.$]+\(([^():]+\.java):\d+\)')
        matches = []
        for line in lines:
            matches.extend(pattern.findall(line))
        return "\n".join(matches)

    def problem3(self, lines):
        pattern = re.compile(r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+(\d+)\s+\d+\s+[VDIWEFS]\b')
        unique_pids = {}
        for line in lines:
            match = pattern.search(line)
            if match:
                unique_pids[match.group(1)] = None
        return "\n".join(unique_pids)

    def problem4(self, lines):
        pattern = re.compile(r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+(\d+)\s+\d+\s+E\b')
        pid_counts = Counter()
        for line in lines:
            match = pattern.search(line)
            if match:
                pid_counts[match.group(1)] += 1

        if not pid_counts:
            return ""

        top_pid, count = pid_counts.most_common(1)[0]
        return f"PID={top_pid} ({count} errors)"

    def problem5(self, lines):
        pattern = re.compile(r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+(\d+)\s+\1\s+E\b')
        count = 0
        for line in lines:
            if pattern.search(line):
                count += 1
        return count

    def run(self, args):
        input_file = args.input
        output_file = args.output

        # Feladatok feldolgozása a --rgx kapcsoló alapján
        with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
            match args.rgx:
                case 1:
                    result = self.problem1(f)
                case 2:
                    result = self.problem2(f)
                case 3:
                    result = self.problem3(f)
                case 4:
                    result = self.problem4(f)
                case 5:
                    result = self.problem5(f)

        # Write the result into the file
        with open(output_file, 'w') as f:
            f.write(str(result))