"""
Robust German Morpheme Analyzer
Copyright (c) O. Teselkina, N. Kovalev
24.01.2026
"""

import csv
import re
from collections import Counter, defaultdict

from compound_split import char_split
from HanTa import HanoverTagger
from ordered_set import OrderedSet

from .paths import INPUTS_NO_SUBCLUSTER_DIR, ROOTS_RESULTS_DIR

tagger = HanoverTagger.HanoverTagger("morphmodel_ger.pgz")


class GermanMorphemeAnalyzer:
    def __init__(self):
        """
        Initializes the analyzer with linguistic data lists.
        dictionary_path: Optional path to a file containing valid German roots.
        """
        # --- 1. Linguistic Knowledge Base ---

        # Inseparable and Separable Prefixes
        self.prefixes = {
            # Inseparable
            "be",
            "emp",
            "ent",
            "er",
            "ge",
            "miss",
            "ver",
            "zer",
            # Separable
            "ab",
            "an",
            "auf",
            "aus",
            "bei",
            "da",
            "dar",
            "ein",
            "unter",
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
            "über",
            "anti",
            "auto",
            "bio",
            "co",
            "de",
            "dis",
            "ex",
            "hyper",
            # Neo-classical
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
        self.known_roots = OrderedSet(initial={})
        for root in sorted(
            [
                "haus",
                "auto",
                "dampf",
                "schiff",
                "fahrt",
                "arbeit",
                "zeit",
                "tag",
                "nacht",
                "licht",
                "sommer",
                "winter",
                "wasser",
                "kraft",
                "werk",
                "kosmos",
                "logie",
                "bio",
                "technik",
                "auto",
                "mobil",
                "telefon",
                "buch",
                "hand",
                "spiel",
                "platz",
                "dauer",
                "qualität",
                "prozess",
                "welt",
                "last",
                "schutz",
                "plan",
                "stadt",
                "land",
                "halt",
                "linie",
                "konst",
                "energ",
                "ressource",
                "belast",
                "entwickl",
                # Added from the v3 results
                "umwelt",
                "klima",
                "energi",
                "kraft",
                "schutz",
                "welt",
                "halt",
                "belast",
                "fäh",
                "dauer",
                "trieb",
                "wirk",
                "stärk",
                "druck",
                "stoff",
                "schad",
                "gleich",
                "luft",
                "strom",
                "maß",
                "mach",
                "ehr",
                "studi",
                "vertrag",
                "verträg",
                "kehr",
                "wieder",
                "auftrag",
                "prüf",
                "ausschoß",
                "öl",
                "schmutz",
                "wert",
                "contain",
                "roh",
                "mäß",
                "hart",
                "stand",
                "wider",
                "näck",
                "kenn",
                "zeichn",
                "rat",
                "schalt",
                "freund",
                "neutr",
                "natur",
                "schon",
                "schäd",
                "effekt",
                "treib",
                "problem",
                "wechs",
                "seit",
                "gesamt",
                "indikat",
                "find",
                "konsens",
                "folg",
                "forsch",
                "größ",
                "sozi",
                "ziel",
                "streb",
                "spen",
                "starr",
                "hals",
                "rück",
                "will",
                "frei",
                "erfolg",
                "rezept",
                "aktion",
                "bund",
                "bünd",
                "gemein",
                "all",
                "wuss",  # wiss
                "wiss",
                "art",
                "nah",
                "silb",
                "verbrauch",
                "gefärd",
                "erd",
                "halb",
                "kugel",
                "sphär",
                "hemi",
                "stern",
                "himmel",
                "lauf",
                "univers",
                "atmo",
                "schicht",
                "ozon",
                "pest",
                "katastroph",
                "photo",
                "volt",
                "produkt",
                "kapital",
                "elektr",
                "kopf",
                "raum",
                "sonder",
                "abfall",
                "samml",
                "müll",
                "abgab",
                "kreis",
                "trag",
                "förm",
                "wärm",
                "setz",
                "win",
                "zertific",
                "fahr",
                "voll",
                "zieh",
                "ersatz",
                "hält",
                "mensch",
                "wett",
                "kämpf",
                "kampf",
            ],
            key=len,
            reverse=True,
        ):
            self.known_roots.append(root)

        # Statistics Storage
        self.stats = defaultdict(Counter)  # e.g. {'Root': Counter(), 'Prefix': Counter()}

    def clean_word(self, word):
        """Normalization: remove punctuation (except hyphens, we process them manually), keep umlauts."""
        return re.sub(r"[^\wäöüÄÖÜß-]", "", word)

    def split_based_on_known(self, word: str) -> tuple[list[str], list[str], list[str], list[str]]:
        """
        This method takes a word and attempts to split it based on known roots.
        The process adheres to the following rules:
            - If a root from the self.known_roots is found, temporarily remove it from the word
            - In what's left of the word, run through the known roots again to find additional roots
            - If a root was found, split the word at the point where the next (by appearance in the word) root begins
            - Apply this recursively until there is no more than 1 known root found in the remaining word

        :param word: The word to be split
        :return: A list of potential single root words, followed by lists of prefixes, interfixes and suffixes
            found in mid-root chunks
        """
        word_lower = word.lower()

        # If the word itself is a known root, return it
        if word_lower in self.known_roots:
            return [word], [], [], []

        # 1. Check strict condition: Root found, remove it, another root found in remainder.
        can_split = False
        for root in self.known_roots:
            if root in word_lower:
                # Remove the first occurrence of this root
                temp_word = word_lower.replace(root, "", 1)
                # Check if any root exists in temp_word
                for other_root in self.known_roots:
                    if other_root in temp_word:
                        can_split = True
                        break
            if can_split:
                break

        if not can_split:
            return [word], [], [], []

        # 2. Identify split point: "where the second (by appearance in the word) root begins"
        starts = set()
        ends = set()
        found = set()
        for root in self.known_roots:
            if any(root in found_root for found_root in found):
                continue  # Skip roots already found
            # We strictly look for matches of known roots
            for m in re.finditer(re.escape(root), word_lower):
                starts.add(m.start())
                ends.add(m.end())
                found.add(root)

        sorted_starts = sorted(starts)
        sorted_ends = sorted(ends)

        # We need at least 2 start positions to be able to split the word
        if len(sorted_starts) < 2:
            return [word], [], [], []

        midchunk_prefixes = []
        midchunk_suffixes = []
        midchunk_interfixes = []
        for i in range(len(sorted_starts) - 1):
            midchunk = word_lower[sorted_ends[i] : sorted_starts[i + 1]]
            pre, inter, suf = self.split_midword_chunk(midchunk)
            midchunk_prefixes.extend(pre)
            midchunk_interfixes.extend(inter)
            midchunk_suffixes.extend(suf)

        return (
            ([word[sorted_starts[i] : sorted_ends[i]] for i in range(len(sorted_starts))]),
            midchunk_prefixes,
            midchunk_interfixes,
            midchunk_suffixes,
        )

    def split_midword_chunk(self, chunk: str) -> tuple[list[str], list[str], list[str]]:
        """
        Splits a mid-word chunk into morphemes if possible.
        Knowing that a mid-word chunk could contain:
            - suffixes in the beginning (from the previous root),
            - interfixes in the middle,
            - prefixes at the end (from the next root),
        we do a greedy strip/collection of these affixes in that order and from left to right.

        Returns: Three lists: suffixes, interfixes, prefixes
        """
        suffixes = []
        interfixes = []
        prefixes = []
        current = chunk.lower()

        # 1. Greedy suffixes at the beginning
        # We check from the start of the current string
        while current:
            matched = False
            # Sort suffixes by length descending for greedy match
            for suf in sorted(self.suffixes, key=len, reverse=True):
                if current.startswith(suf):
                    suffixes.append(suf)
                    current = current[len(suf) :]
                    matched = True
                    break
            if not matched:
                break

        # 2. Greedy interfixes in the middle
        while current:
            matched = False
            for ifix in sorted(self.interfixes, key=len, reverse=True):
                if current.startswith(ifix):
                    interfixes.append(ifix)
                    current = current[len(ifix) :]
                    matched = True
                    break
            if not matched:
                break

        # 3. Greedy prefixes at the end
        while current:
            matched = False
            for pre in sorted(self.prefixes, key=len, reverse=True):
                if current.startswith(pre):
                    prefixes.append(pre)
                    current = current[len(pre) :]
                    matched = True
                    break
            if not matched:
                break

        # If anything is left, treat it as an unknown part or handle as needed
        if current:
            if current in self.prefixes:
                prefixes.append(current)
            elif current in self.suffixes:
                suffixes.append(current)
            elif current in self.interfixes:
                interfixes.append(current)

        return prefixes, interfixes, suffixes

    def split_compound(self, stem):
        if stem.lower() in self.known_roots:
            return [(stem.capitalize(), "Root")]

        # CharSplit returns probabilities, we take the best split
        best_split = char_split.split_compound(stem)[0]
        if 0.5 < best_split[0] <= 1:
            return self.split_compound(best_split[1]) + self.split_compound(best_split[2])
        return [(stem.capitalize(), "Root")]

    def strip_affixes(self, word) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
        # Direct root match to exclude splitting the root accidentally
        # But restrict this to no more than 1-char length affixes
        # TODO: maybe extend to 2-char affixes
        for root in self.known_roots:
            if root in word and len(word) - len(root) < 2:
                if len(word) > len(root):
                    if word.startswith(root):
                        return [], [(root.capitalize(), "Root")], [(word[len(root) :], "Suffix")]
                    if word.endswith(root):
                        return [(word[: -len(root)], "Prefix")], [(root.capitalize(), "Root")], []
                return [], [(root.capitalize(), "Root")], []

        # --- Step 1: Suffix Stripping ---
        # Greedy right-to-left matching
        matched_suffix = True
        suffixes = []
        while matched_suffix:
            ends_with_root = any(word.endswith(root) for root in self.known_roots)
            if ends_with_root:
                break

            matched_suffix = False
            # Sort suffixes by length (descending) to match 'igkeit' before 'keit'
            for suf in sorted(self.suffixes, key=len, reverse=True):
                # 2nd Constraint: Stem must remain valid length
                if word.endswith(suf) and len(word) - len(suf) >= 3:
                    # Prepend to list (we are working backwards)
                    suffixes.insert(0, (suf, "Suffix"))
                    word = word[: -len(suf)]
                    matched_suffix = True
                    break

        # --- Step 2: Prefix Stripping ---
        # Greedy left-to-right matching
        matched_prefix = True
        prefixes = []
        while matched_prefix:
            starts_with_root = any(word.startswith(root) for root in self.known_roots)
            if starts_with_root:
                break

            matched_prefix = False
            for pre in sorted(self.prefixes, key=len, reverse=True):
                if word.startswith(pre) and len(word) - len(pre) >= 3:
                    prefixes.append((pre, "Prefix"))
                    word = word[len(pre) :]
                    matched_prefix = True
                    break

        return prefixes, [(word.capitalize(), "Root")], suffixes

    def analyze_word(
        self, original_word: str
    ) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
        """
        The Core Pipeline: Suffix Strip -> Prefix Strip -> Compound Split
        """
        word = original_word.lower()  # Work in lowercase for matching

        prefixes = []
        stems = []
        suffixes = []
        interfixes = []

        manual_parts, pref, suff, interf = self.split_based_on_known(word)
        if len(manual_parts) > 1:
            parts = []
            for part in manual_parts:
                parts.extend(self.split_compound(part))
            prefixes.extend((p, "Prefix") for p in pref)
            suffixes.extend((s, "Suffix") for s in suff)
            interfixes.extend((i, "Interfix") for i in interf)
        else:
            parts = self.split_compound(word)

        additional_parts = []
        for part in parts:
            sub_parts, sub_prefixes, sub_interfixes, sub_suffixes = self.split_based_on_known(part[0])
            if len(sub_parts) > 1:
                additional_parts.extend((sp, "Root") for sp in sub_parts)
                prefixes.extend((p, "Prefix") for p in sub_prefixes)
                interfixes.extend((i, "Interfix") for i in sub_interfixes)
                suffixes.extend((s, "Suffix") for s in sub_suffixes)
            else:
                additional_parts.append(part)

        if len(additional_parts) > len(parts):
            print(f"Split for {original_word}: {parts}.\nEnhanced split: {additional_parts}")
        parts = additional_parts

        if not parts:
            raise ValueError(f"Could not split compound: {original_word}")

        # If we have compound parts, analyze each part for affixes
        for part, _ in parts:
            pre, stem, suf = self.strip_affixes(part.lower())
            prefixes.extend(pre)
            stems.extend(stem)
            suffixes.extend(suf)

        to_remove = []
        for i, (root, _) in enumerate(stems):
            root_word = root.lower()
            if root_word in self.prefixes:
                to_remove.append(i)
                prefixes.append((root_word, "Prefix"))
            elif root_word in self.suffixes:
                to_remove.append(i)
                suffixes.append((root_word, "Suffix"))
            elif root_word in self.interfixes:
                to_remove.append(i)
                interfixes.append((root_word, "Interfix"))

        for index in sorted(to_remove, reverse=True):
            del stems[index]

        to_remove = []
        for i, (inter, _) in enumerate(interfixes):
            if inter not in self.interfixes:
                if inter in self.prefixes:
                    to_remove.append(i)
                    prefixes.append((inter, "Prefix"))
                elif inter in self.suffixes:
                    to_remove.append(i)
                    suffixes.append((inter, "Suffix"))

        for index in sorted(to_remove, reverse=True):
            del interfixes[index]

        return prefixes, stems, suffixes, interfixes

    def process_text(self, text):
        tokens = text.split()
        for token in tokens:
            lemma = tagger.analyze(token)[0]  # Get the lemma (e.g., 'ging' -> 'gehen')
            clean = self.clean_word(lemma)

            if "-" in clean:
                for clean_word in clean.split("-"):
                    if not clean_word or clean_word.lower() in self.stopwords or clean_word.isdigit():
                        continue
                    # Analyze
                    prefixes, stems, suffixes, interfixes = self.analyze_word(clean_word)

                    # Aggregation
                    for morph, m_type in prefixes + stems + suffixes + interfixes:
                        self.stats[m_type][morph] += 1
                continue

            if not clean or clean.lower() in self.stopwords or clean.isdigit():
                continue

            # Analyze
            prefixes, stems, suffixes, interfixes = self.analyze_word(clean)

            # Aggregation
            for morph, m_type in prefixes + stems + suffixes + interfixes:
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

    def clean_stats(self):
        self.stats = defaultdict(Counter)


def run_analysis():
    analyzer = GermanMorphemeAnalyzer()
    ROOTS_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    for input_name, output_name in [
        ("ecology", "ecology_new_roots.csv"),
        ("economy", "economy_new_roots.csv"),
        ("sociology", "sociology_new_roots.csv"),
        ("all_sources", "all_sources_new_roots.csv"),
    ]:
        input_path = INPUTS_NO_SUBCLUSTER_DIR / f"{input_name}.txt"
        output_path = ROOTS_RESULTS_DIR / output_name

        with open(input_path, encoding="utf-8") as f:
            text = f.read()
            analyzer.process_text(text)
            analyzer.export_csv(output_path)
            analyzer.clean_stats()


# --- Execution ---
if __name__ == "__main__":
    run_analysis()
