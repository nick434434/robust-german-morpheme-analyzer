from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = SRC_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
INPUTS_DIR = DATA_DIR / "inputs"
INPUTS_NO_SUBCLUSTER_DIR = DATA_DIR / "inputs_no_subcluster_names"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"

RESULTS_DIR = PROJECT_ROOT / "results"
ROOTS_RESULTS_DIR = RESULTS_DIR / "roots"
FREQUENCY_RESULTS_DIR = RESULTS_DIR / "frequency_count"
MORPHOLOGY_STATS_DIR = RESULTS_DIR / "morphology_stats"
MORPHOLOGY_STATS_V1_DIR = RESULTS_DIR / "morphology_stats_v1"
MORPHOLOGY_STATS_V2_DIR = RESULTS_DIR / "morphology_stats_v2"
MORPHOLOGY_STATS_NO_SUBCLUSTER_DIR = RESULTS_DIR / "morphology_stats_no_subcluster_names"

ANALYZER_INPUT_NAMES = [
    "dauer",
    "qualitaet",
    "prozess",
    "umwelt",
    "kraft",
    "materialeneigenschaft",
    "betriebsprozess",
    "qualifikation",
    "ausdauer",
    "eigenschaft",
    "teilnahme",
    "guete",
]
