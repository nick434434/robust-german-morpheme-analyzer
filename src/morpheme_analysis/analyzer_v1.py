import csv
import re
from collections import Counter, defaultdict

from compound_split import char_split
from HanTa import HanoverTagger

from .paths import ANALYZER_INPUT_NAMES, INPUTS_DIR, MORPHOLOGY_STATS_V1_DIR

tagger = HanoverTagger.HanoverTagger("morphmodel_ger.pgz")


class GermanMorphemeAnalyzer:
    def __init__(self, dictionary_path=None):
        """
        Initializes the analyzer with linguistic data lists.
        dictionary_path: Optional path to a file containing valid German roots.
        """
        # --- 1. Linguistic Knowledge Base ---

        # Inseparable and Separable Prefixes
        self.prefixes = {
            "be",
            "emp",
            "ent",
            "er",
            "ge",
            "miss",
            "ver",
            "zer",  # Inseparable
            "ab",
            "an",
            "auf",
            "aus",
            "bei",
            "da",
            "dar",
            "ein",  # Separable
            "empor",
            "fort",
            "heim",
            "her",
            "hin",
            "los",
            "mit",
            "nach",
            "vor",
            "weg",
            "zu",
            "zusammen",
            "un",
            "ur",
            "anti",
            "auto",
            "bio",
            "co",
            "de",
            "dis",
            "ex",
            "hyper",  # Neo-classical
            "inter",
            "neo",
            "non",
            "post",
            "pre",
            "pro",
            "re",
            "sub",
            "super",
            "tele",
            "trans",
            "ultra",
        }

        # Suffixes (Derivational and Inflectional)
        self.suffixes = {
            # Noun forming
            "ung",
            "heit",
            "keit",
            "schaft",
            "tum",
            "nis",
            "chen",
            "lein",
            "ling",
            "sal",
            "erei",
            "ität",
            "tion",
            "ismus",
            "ist",
            "logie",
            "ment",
            "ur",
            "enz",
            "anz",
            # Adjective forming
            "bar",
            "haft",
            "isch",
            "sam",
            "los",
            "lich",
            "ig",
            "ern",
            "iv",
            "al",
            "ell",
            "ant",
            "abel",
            # Inflectional (Grammar)
            "end",
            "est",
            "ten",
            "tet",
            "test",
            "ens",
            "en",
            "er",
            "es",
            "te",
            "st",
            "et",
            "e",
            "s",
            "n",
            "t",
        }

        # Linking elements (Interfixes)
        self.interfixes = {"s", "es", "n", "en", "er"}

        # Stopwords (Function words that are not interesting for morpheme analysis)
        self.stopwords = {
            "der",
            "die",
            "das",
            "und",
            "ist",
            "in",
            "den",
            "von",
            "zu",
            "für",
            "mit",
            "sich",
            "des",
            "auf",
            "im",
            "dass",
            "nicht",
            "eine",
            "ein",
        }

        # Load Dictionary for Compound Splitting
        # In a real scenario, load from a large file (e.g., 100k nouns).
        # Here we seed it with some common roots for demonstration.
        self.known_roots = {
            "haus",
            "tür",
            "auto",
            "bahn",
            "rast",
            "stätte",
            "dampf",
            "schiff",
            "fahrt",
            "gesellschaft",
            "kapitän",
            "donau",
            "arbeit",
            "zeit",
            "tag",
            "nacht",
            "licht",
            "sommer",
            "winter",
            "kind",
            "garten",
            "schule",
            "lehrer",
            "freund",
            "feind",
            "liebe",
            "brief",
            "wasser",
            "weg",
            "brot",
            "butter",
            "bröt",
            "chen",
            "flug",
            "zeug",
            "kraft",
            "werk",
            "hoch",
            "tief",
            "lang",
            "kurz",
            "groß",
            "klein",
            "kosmos",
            "logie",
            "bio",
            "technik",
            "mobil",
            "telefon",
            "buch",
            "handlung",
            "spiel",
            "platz",
            "last",
            "klima",
            "schutz",
            "plan",
            "stadt",
            "land",
            "halt",
        }
        if dictionary_path:
            self.load_dictionary(dictionary_path)

        # Statistics Storage
        self.stats = defaultdict(Counter)  # e.g. {'Root': Counter(), 'Prefix': Counter()}

    def load_dictionary(self, path):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    word = line.strip().lower()
                    if len(word) > 2:
                        self.known_roots.add(word)
            print(f"Loaded {len(self.known_roots)} roots from dictionary.")
        except Exception as e:
            print(f"Warning: Could not load dictionary {path}. Using basic seed set. ({e})")

    def clean_word(self, word):
        """Normalization: remove punctuation, keep umlauts."""
        return re.sub(r"[^\wäöüÄÖÜß]", "", word)

    def split_compound(self, stem) -> list[tuple[str, str]]:
        raise NotImplementedError

    def analyze_word(self, word):
        """
        The Core Pipeline: Suffix Strip -> Prefix Strip -> Compound Split
        """
        word = word.lower()  # Work in lowercase for matching

        segments = []

        # --- Step 1: Suffix Stripping ---
        # Greedy right-to-left matching
        matched_suffix = True
        while matched_suffix:
            matched_suffix = False
            # Sort suffixes by length (descending) to match 'igkeit' before 'keit'
            for suf in sorted(self.suffixes, key=len, reverse=True):
                if word.endswith(suf) and len(word) - len(suf) >= 3:
                    segments.insert(0, (suf, "Suffix"))  # Prepend to list (we are working backwards)
                    word = word[: -len(suf)]
                    matched_suffix = True
                    break

                    # --- Step 2: Prefix Stripping ---
        # Greedy left-to-right matching
        matched_prefix = True
        prefix_segments = []
        while matched_prefix:
            matched_prefix = False
            for pre in sorted(self.prefixes, key=len, reverse=True):
                if word.startswith(pre) and len(word) - len(pre) >= 3:
                    prefix_segments.append((pre, "Prefix"))
                    word = word[len(pre) :]
                    matched_prefix = True
                    break

        # --- Step 3: Compound Splitting on the Stem ---
        # 'word' is now the stripped stem.
        stem_segments = self.split_compound(word)

        return prefix_segments + stem_segments + segments

    def process_text(self, text):
        tokens = text.split()
        for token in tokens:
            lemma = tagger.analyze(token)[0]  # Get the lemma (e.g., 'ging' -> 'gehen')
            clean = self.clean_word(lemma)
            if not clean or clean.lower() in self.stopwords or clean.isdigit():
                continue

            # Analyze
            components = self.analyze_word(clean)  # Analyze 'gehen' instead of 'ging'

            # Aggregation
            for morph, m_type in components:
                self.stats[m_type][morph] += 1

    def export_csv(self, output_path):
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Morpheme", "Type", "Count"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Sort output: Type alphabetically, then Count descending
            for m_type in sorted(self.stats.keys()):
                for morph, count in self.stats[m_type].most_common():
                    writer.writerow({"Morpheme": morph, "Type": m_type, "Count": count})
        print(f"Analysis complete. Data written to {output_path}")


class AdvancedAnalyzer(GermanMorphemeAnalyzer):
    def split_compound(self, stem) -> list[tuple[str, str]]:
        # CharSplit returns probabilities, we take the best split
        best_split = char_split.split_compound(stem)[0]
        # Returns (score, left, right)
        return [(best_split[1], "Root"), (best_split[2], "Root")]


def run_analysis():
    analyzer = AdvancedAnalyzer()
    MORPHOLOGY_STATS_V1_DIR.mkdir(parents=True, exist_ok=True)

    full_corpus = ""
    text = ""

    for filename in ANALYZER_INPUT_NAMES:
        input_path = INPUTS_DIR / f"{filename}.txt"
        output_path = MORPHOLOGY_STATS_V1_DIR / f"{filename}.csv"

        print(f"Reading {input_path}...")
        with open(input_path, encoding="utf-8") as f:
            text = f.read()
            full_corpus += text

        analyzer.process_text(text)
        analyzer.export_csv(output_path)

    analyzer.process_text(text)
    analyzer.export_csv(MORPHOLOGY_STATS_V1_DIR / "all_sources.csv")


# --- Execution ---
if __name__ == "__main__":
    run_analysis()
