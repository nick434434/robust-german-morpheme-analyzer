import re
import csv
import sys
from collections import defaultdict, Counter

from compound_split import char_split

from HanTa import HanoverTagger as ht
tagger = ht.HanoverTagger('morphmodel_ger.pgz')


class GermanMorphemeAnalyzer:
    def __init__(self, dictionary_path=None):
        """
        Initializes the analyzer with linguistic data lists.
        dictionary_path: Optional path to a file containing valid German roots.
        """
        # --- 1. Linguistic Knowledge Base ---

        # Inseparable and Separable Prefixes
        self.prefixes = {
            'be', 'emp', 'ent', 'er', 'ge', 'miss', 'ver', 'zer',  # Inseparable
            'ab', 'an', 'auf', 'aus', 'bei', 'da', 'dar', 'ein',  # Separable
            'empor', 'fort', 'heim', 'her', 'hin', 'los', 'mit',
            'nach', 'vor', 'weg', 'zu', 'zusammen', 'un', 'ur',
            'anti', 'auto', 'bio', 'co', 'de', 'dis', 'ex', 'hyper',  # Neo-classical
            'inter', 'neo', 'non', 'post', 'pre', 'pro', 're', 'sub',
            'super', 'tele', 'trans', 'ultra'
        }

        # Suffixes (Derivational and Inflectional)
        self.suffixes = {
            # Noun forming
            'ung', 'heit', 'keit', 'schaft', 'tum', 'nis', 'chen', 'lein',
            'ling', 'sal', 'erei', 'ität', 'tion', 'ismus', 'ist', 'logie',
            'ment', 'ur', 'enz', 'anz',
            # Adjective forming
            'bar', 'haft', 'isch', 'sam', 'los', 'lich', 'ig', 'en', 'ern',
            'iv', 'al', 'ell', 'ant', 'abel',
            # Inflectional (Grammar)
            'end', 'est', 'ten', 'tet', 'test', 'ens',
            'en', 'er', 'es', 'te', 'st', 'et', 'e', 's', 'n', 't'
        }

        # Linking elements (Interfixes)
        self.interfixes = {'s', 'es', 'n', 'en', 'er'}

        # Stopwords (Function words that are not interesting for morpheme analysis)
        self.stopwords = {
            'der', 'die', 'das', 'und', 'ist', 'in', 'den', 'von', 'zu', 'für',
            'mit', 'sich', 'des', 'auf', 'im', 'dass', 'nicht', 'eine', 'ein'
        }

        # Load Dictionary for Compound Splitting
        # In a real scenario, load from a large file (e.g., 100k nouns).
        # Here we seed it with some common roots for demonstration.
        self.known_roots = {
            'haus', 'auto', 'dampf', 'schiff', 'fahrt',
            'arbeit', 'zeit', 'tag', 'nacht', 'licht', 'sommer', 'winter',
            'wasser', 'kraft', 'werk',
            "kosmos", "logie", "bio", "technik", "auto", "mobil",
            "telefon", "buch", "hand", "spiel", "platz",
            "dauer", "qualität", "prozess", "umwelt", "welt",
            "last", "klima", "schutz", "plan", "stadt", "land", "halt",
            "linie", "konst", "energ",
        }
        if dictionary_path:
            self.load_dictionary(dictionary_path)

        # Statistics Storage
        self.stats = defaultdict(Counter)  # e.g. {'Root': Counter(), 'Prefix': Counter()}

    def load_dictionary(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if len(word) > 2:
                        self.known_roots.add(word)
            print(f"Loaded {len(self.known_roots)} roots from dictionary.")
        except Exception as e:
            print(f"Warning: Could not load dictionary {path}. Using basic seed set. ({e})")

    def clean_word(self, word):
        """Normalization: remove punctuation, keep umlauts."""
        return re.sub(r'[^\wäöüÄÖÜß]', '', word)

    def split_compound(self, stem):
        """
        Recursive dictionary-based compound splitter with Interfix handling.
        Returns a list of tuples: [(segment, type),...]
        """
        stem_lower = stem.lower()

        # Base Case: If the stem is in our dictionary, it's a Root.
        if stem_lower in self.known_roots:
            return

        # Recursive Step: Try to split
        best_split = None

        # Iterate split points from left to right
        for i in range(3, len(stem) - 2):  # Min root length constraint
            left = stem[:i]
            right = stem[i:]
            interfix = ''
            remainder = right

            # Check for direct split
            if left.lower() in self.known_roots:
                # Scenario A: Direct concatenation (Auto-bahn)
                # We need to verify if 'right' can be analyzed further
                sub_analysis = self.split_compound(right)
                if sub_analysis:
                    return + sub_analysis

                # Scenario B: Interfix (Liebe-s-brief)
                # Check if 'right' starts with an interfix
                for ifix in self.interfixes:
                    if right.lower().startswith(ifix):
                        possible_remainder = right[len(ifix):]
                        if len(possible_remainder) > 2:
                            sub_analysis_ifix = self.split_compound(possible_remainder)
                            if sub_analysis_ifix:
                                # Found valid split with interfix
                                return + sub_analysis_ifix

        # Fallback: If no split found, treat as Unknown Root (or valid root missing from dict)
        return

    def analyze_word(self, original_word) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
        """
        The Core Pipeline: Suffix Strip -> Prefix Strip -> Compound Split
        """
        word = original_word.lower()  # Work in lowercase for matching

        segments = []

        # --- Step 1: Suffix Stripping ---
        # Greedy right-to-left matching
        matched_suffix = True
        while matched_suffix:
            ends_with_root = any([word.endswith(root) for root in self.known_roots])
            if ends_with_root:
                break

            matched_suffix = False
            # Sort suffixes by length (descending) to match 'igkeit' before 'keit'
            for suf in sorted(self.suffixes, key=len, reverse=True):
                if word.endswith(suf):
                    # Constraint: Stem must remain valid length
                    if len(word) - len(suf) >= 3:
                        segments.insert(0, (suf, 'Suffix'))  # Prepend to list (we are working backwards)
                        word = word[:-len(suf)]
                        matched_suffix = True
                        break

        # --- Step 2: Prefix Stripping ---
        # Greedy left-to-right matching
        matched_prefix = True
        prefix_segments = []
        while matched_prefix:
            starts_with_root = any([word.startswith(root) for root in self.known_roots])
            if starts_with_root:
                break

            matched_prefix = False
            for pre in sorted(self.prefixes, key=len, reverse=True):
                if word.startswith(pre):
                    if len(word) - len(pre) >= 3:
                        prefix_segments.append((pre, 'Prefix'))
                        word = word[len(pre):]
                        matched_prefix = True
                        break

        # --- Step 3: Compound Splitting on the Stem ---
        # 'word' is now the stripped stem.
        stem_segments = self.split_compound(word)

        # if not prefix_segments and not segments:
        #     return [], stem_segments, []
        #
        # for potential_stem in stem_segments:
        #     new_prefixes, new_stems, new_suffixes = self.analyze_word(potential_stem[0])
        #     prefix_segments += new_prefixes
        #     segments += new_suffixes

        return prefix_segments, stem_segments, segments

    def process_text(self, text):
        tokens = text.split()
        for token in tokens:
            lemma = tagger.analyze(token)[0]  # Get the lemma (e.g., 'ging' -> 'gehen')
            clean = self.clean_word(lemma)
            if not clean or clean.lower() in self.stopwords or clean.isdigit():
                continue

            # Analyze
            prefixes, stems, suffixes = self.analyze_word(clean)

            # Aggregation
            for morph, m_type in prefixes + stems + suffixes:
                self.stats[m_type][morph] += 1

    def export_csv(self, output_path):
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["Morpheme", "Type", "Count"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Sort output: Type alphabetically, then Count descending
            for m_type in sorted(self.stats.keys()):
                for morph, count in self.stats[m_type].most_common():
                    writer.writerow({
                        'Morpheme': morph,
                        'Type': m_type,
                        'Count': count
                    })
        print(f"Analysis complete. Data written to {output_path}")


class AdvancedAnalyzer(GermanMorphemeAnalyzer):
    def split_compound(self, stem):
        # CharSplit returns probabilities, we take the best split
        best_split = char_split.split_compound(stem)[0]
        if best_split[0] > 0.5:
            return [(best_split[1].capitalize(), 'Root'), (best_split[2].capitalize(), 'Root')]
        return [(stem.capitalize(), "Root")]


# --- Execution ---
if __name__ == "__main__":
    # Initialize
    analyzer = AdvancedAnalyzer()

    full_corpus = ""
    ecology_sphere = ""
    economy_sphere = ""
    sociology_sphere = ""
    counter = 0

    for filename in [
        # Ökologie
        "dauer",
        "qualitaet",
        "prozess",
        "umwelt",
        # Wirtschaft
        "kraft",
        "materialeneigenschaft",
        "betriebsprozess",
        "qualifikation",
        # Gesellschaftskultur
        "ausdauer",
        "eigenschaft",
        "teilnahme",
        "guete",
    ]:
        # Process
        print(f"Reading inputs/{filename}.txt...")
        with open(f"inputs/{filename}.txt", "r", encoding="utf-8") as f:
            text = f.read()
            full_corpus += text
            ecology_sphere = ecology_sphere + (text if counter < 4 else "")
            economy_sphere = economy_sphere + (text if 4 <= counter < 8 else "")
            sociology_sphere = sociology_sphere + (text if counter >= 8 else "")
            counter += 1

        analyzer.process_text(text)
        analyzer.export_csv(f"morphology_stats/{filename}.csv")

    analyzer.process_text(ecology_sphere)
    analyzer.export_csv(f"morphology_stats/ecology.csv")

    analyzer.process_text(economy_sphere)
    analyzer.export_csv(f"morphology_stats/economy.csv")

    analyzer.process_text(sociology_sphere)
    analyzer.export_csv(f"morphology_stats/sociology.csv")

    analyzer.process_text(full_corpus)
    analyzer.export_csv(f"morphology_stats/all_sources.csv")
