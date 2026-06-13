import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="morpheme-analysis")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Run morpheme analysis")
    analyze_parser.add_argument(
        "mode",
        choices=["current", "v1", "v2"],
        help="Analyzer variant to run",
    )

    frequency_parser = subparsers.add_parser("frequencies", help="Count root frequencies")
    frequency_parser.add_argument(
        "--limit",
        type=int,
        default=4,
        help="Minimum root count to include from source root CSVs",
    )

    diagnostic_parser = subparsers.add_parser("diagnostic", help="Run diagnostic scripts")
    diagnostic_parser.add_argument(
        "mode",
        choices=["split", "midword"],
        help="Diagnostic routine to run",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "analyze":
        if args.mode == "current":
            from . import analyzer

            analyzer.run_analysis()
        elif args.mode == "v1":
            from . import analyzer_v1

            analyzer_v1.run_analysis()
        elif args.mode == "v2":
            from . import analyzer_v2

            analyzer_v2.run_analysis()
        return 0

    if args.command == "frequencies":
        from . import frequency

        frequency.run_frequency_count(limit=args.limit)
        return 0

    if args.command == "diagnostic":
        if args.mode == "split":
            from scripts.test_split import test_splitter

            test_splitter()
        elif args.mode == "midword":
            from scripts.test_midword import test_midword_chunk

            test_midword_chunk()
        return 0

    raise ValueError(f"Unknown command: {args.command}")
