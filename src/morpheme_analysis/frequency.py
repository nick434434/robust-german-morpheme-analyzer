import csv
import re
from collections import defaultdict

try:
    from .paths import FREQUENCY_RESULTS_DIR, ROOTS_RESULTS_DIR, TRANSCRIPTS_DIR
except ImportError:
    from paths import FREQUENCY_RESULTS_DIR, ROOTS_RESULTS_DIR, TRANSCRIPTS_DIR


def count_root_frequencies(text: str, roots: set[str]):
    """
    Count frequencies of given roots in the provided text.
    Returns a dictionary mapping root -> frequency.
    """
    # Normalize text to lowercase and split into words
    words = re.findall(r"\b\w+\b", text.lower())

    frequency_dict = defaultdict(int)

    for word in words:
        for root in roots:
            if root in word:
                frequency_dict[root] += 1

    return dict(frequency_dict)


def load_roots_from_csv(file_path: str, limit: int | None = None) -> set[str]:
    """
    Load roots from a CSV file. Assumes one root per line.
    """
    roots = set()
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if (
                row
                and len(row) == 3
                and row[1] == "Root"  # Ensure it's a root entry
                and (
                    limit is None or int(row[-1]) >= limit
                )  # Check limit if provided and the entry matches
            ):
                roots.add(row[0].strip().lower())
    return roots


def run_frequency_count(limit: int = 4):
    FREQUENCY_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    transcripts = {
        "text_5": TRANSCRIPTS_DIR / "5_эпизодов_2022.txt",
        "text_7": TRANSCRIPTS_DIR / "7_эпизодов_2022.txt",
        "text_CR": TRANSCRIPTS_DIR / "Все_эпизоды_C&R.txt",
    }

    transcript_texts = {}
    for transcript_name, transcript_path in transcripts.items():
        with open(transcript_path, encoding="utf-8") as f:
            transcript_texts[transcript_name] = f.read()

    roots_by_sphere = {
        "economy": load_roots_from_csv(ROOTS_RESULTS_DIR / "economy_new_roots.csv", limit=limit),
        "ecology": load_roots_from_csv(ROOTS_RESULTS_DIR / "ecology_new_roots.csv", limit=limit),
        "sociology": load_roots_from_csv(
            ROOTS_RESULTS_DIR / "sociology_new_roots.csv", limit=limit
        ),
    }

    # freq_5 = count_root_frequencies(text_5, roots)
    # freq_7 = count_root_frequencies(text_7, roots)
    # freq_CR = count_root_frequencies(text_CR, roots)

    for sphere, roots in roots_by_sphere.items():
        for transcript, text in transcript_texts.items():
            freq = count_root_frequencies(text, roots)
            output_path = (
                FREQUENCY_RESULTS_DIR / f"frequency_{sphere}_in_{transcript}_limit_{limit}.csv"
            )

            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Root", "Frequency"])
                for root, freq_count in sorted(
                    freq.items(), key=lambda item: item[1], reverse=True
                ):
                    writer.writerow([root, freq_count])


if __name__ == "__main__":
    run_frequency_count()
