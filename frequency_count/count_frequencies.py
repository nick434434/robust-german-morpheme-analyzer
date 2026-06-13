from collections import defaultdict
import re
import csv


def count_root_frequencies(text: str, roots: list[str]):
    """
    Count frequencies of given roots in the provided text.
    Returns a dictionary mapping root -> frequency.
    """
    # Normalize text to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())

    frequency_dict = defaultdict(int)

    for word in words:
        for root in roots:
            if root in word:
                frequency_dict[root] += 1

    return dict(frequency_dict)


def load_roots_from_csv(file_path: str, limit: int | None = None) -> list[str]:
    """
    Load roots from a CSV file. Assumes one root per line.
    """
    roots = set()
    with (open(file_path, newline='', encoding='utf-8') as csvfile):
        reader = csv.reader(csvfile)
        for row in reader:
            if (
                row and len(row) == 3 and row[1] == "Root"  # Ensure it's a root entry
                and (limit is None or int(row[-1]) >= limit)  # Check limit if provided and the entry matches
            ):
                roots.add(row[0].strip().lower())
    return roots


if __name__ == "__main__":
    with open("5_эпизодов_2022.txt", "r") as f:
        text_5 = f.read()
    with open("7_эпизодов_2022.txt", "r") as f:
        text_7 = f.read()
    with open("Все_эпизоды_C&R.txt", "r") as f:
        text_CR = f.read()

    all_roots = load_roots_from_csv("../all_sources_new_roots.csv")

    limit = 4

    economy = load_roots_from_csv("../economy_new_roots.csv", limit=limit)
    ecology = load_roots_from_csv("../ecology_new_roots.csv", limit=limit)
    sociology = load_roots_from_csv("../sociology_new_roots.csv", limit=limit)

    # freq_5 = count_root_frequencies(text_5, roots)
    # freq_7 = count_root_frequencies(text_7, roots)
    # freq_CR = count_root_frequencies(text_CR, roots)

    for sphere in ["ecology", "economy", "sociology"]:
        roots = locals()[sphere]

        for transcript in ["text_5", "text_7", "text_CR"]:
            text = locals()[transcript]

            freq = count_root_frequencies(text, roots)
            filename = f"frequency_{sphere}_in_{transcript}_limit_{limit}.csv"

            with open(filename, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Root", "Frequency"])
                for root, freq_count in sorted(freq.items(), key=lambda item: item[1], reverse=True):
                    writer.writerow([root, freq_count])
