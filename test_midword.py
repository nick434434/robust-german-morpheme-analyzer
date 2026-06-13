from main import GermanMorphemeAnalyzer

def test_midword_chunk():
    analyzer = GermanMorphemeAnalyzer()
    
    # Test cases: (chunk, expected_types)
    # self.suffixes include: 'ung', 'er', 'en', 's', 'n', 't', etc.
    # self.interfixes include: 's', 'es', 'n', 'en', 'er'
    # self.prefixes include: 'be', 'ge', 'ver', 'un', 'ab', 'an', etc.
    
    test_cases = [
        ("sver", [("s", "Suffix"), ("ver", "Prefix")]), # 's' could be suffix or interfix, but doc says suffix first
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
        result_types = [r[1] for r in result]
        expected_types = [e[1] for e in expected]
        if result_types == expected_types:
             print("PASS (Types match)")
        else:
             print("FAIL (Types mismatch)")
        print("-" * 20)

if __name__ == "__main__":
    test_midword_chunk()
