try:
    from morpheme_analysis.analyzer import GermanMorphemeAnalyzer
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from morpheme_analysis.analyzer import GermanMorphemeAnalyzer

def test_splitter():
    analyzer = GermanMorphemeAnalyzer()
    
    # Add some specific roots for testing if not already there
    analyzer.known_roots.add("bahn")
    
    test_cases = [
        # ("autobahn", ["auto", "bahn"]),
        # ("kraftwerk", ["kraft", "werk"]),
        # ("dampfschifffahrt", ["dampf", "schiff", "fahrt"]), # 'fahrt' is in default list
        # ("haus", ["haus"]),
        # ("unknownword", ["unknownword"]), # Should return as is
        # ("sommerzeit", ["sommer", "zeit"]),
        ("umweltverträglichkeitsstudie", ["umwelt", "verträglichkeits", "studie"]),
    ]
    
    for word, expected in test_cases:
        result = analyzer.split_based_on_known(word)
        print(f"Word: {word}")
        print(f"Expected: {expected}")
        print(f"Result:   {result}")
        if result == expected:
            print("PASS")
        else:
            print("FAIL")
        print("-" * 20)

if __name__ == "__main__":
    test_splitter()
