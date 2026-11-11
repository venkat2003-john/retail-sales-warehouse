
import time
import tempfile
from pathlib import Path

from pipeline import load_warehouse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    database = temp / "benchmark.db"
    output = temp / "outputs"

    start = time.perf_counter()

    report = load_warehouse(DATA, database, output)

    end = time.perf_counter()

    print("\n===== PERFORMANCE BENCHMARK =====")
    print("Status:", report["status"])
    print("Accepted fact rows:", report["counts"]["accepted_fact_rows"])
    print("Rejected rows:", report["counts"]["rejected_rows"])
    print("Execution time:", round(end - start, 3), "seconds")
    print("Rows processed per second:", round(
        report["counts"]["accepted_fact_rows"] / (end - start), 2
    ))
