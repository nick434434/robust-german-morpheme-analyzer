try:
    from morpheme_analysis.analyzer import GermanMorphemeAnalyzer
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from morpheme_analysis.analyzer import GermanMorphemeAnalyzer


def test_midword_chunk():
    analyzer = GermanMorphemeAnalyzer()

    # Test cases: (chunk, expected_types)
    # self.suffixes include: 'ung', 'er', 'en', 's', 'n', 't', etc.
    # self.interfixes include: 's', 'es', 'n', 'en', 'er'
    # self.prefixes include: 'be', 'ge', 'ver', 'un', 'ab', 'an', etc.

    test_cases = [
        # 's' could be suffix or interfix, but doc says suffix first
        ("sver", [("s", "Suffix"), ("ver", "Prefix")]),
        ("ungsbe", [("ung", "Suffix"), ("s", "Interfix"), ("be", "Prefix")]),
        ("enab", [("en", "Suffix"), ("ab", "Prefix")]),
        ("erge", [("er", "Suffix"), ("ge", "Prefix")]),
        ("xyz", [("xyz", "Unknown")]),
    ]

    for chunk, expected in test_cases:
        result = analyzer.split_midword_chunk(chunk)
        print(f"Chunk: {chunk}")
        print(f"Result: {result}")
        # Check if types match (ignoring unknown for now or checking it explicitly)
        prefixes, interfixes, suffixes = result
        result_types = (
            ["Prefix" for _ in prefixes]
            + ["Interfix" for _ in interfixes]
            + ["Suffix" for _ in suffixes]
        )
        expected_types = [e[1] for e in expected]
        if result_types == expected_types:
            print("PASS (Types match)")
        else:
            print("FAIL (Types mismatch)")
        print("-" * 20)


if __name__ == "__main__":
    test_midword_chunk()
