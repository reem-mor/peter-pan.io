# Test Suite Runner

> 9 nodes · cohesion 0.33

## Key Concepts

- **_iter_suites()** (5 connections) — `scripts/run_all_tests.py`
- **run_all_tests.py** (4 connections) — `scripts/run_all_tests.py`
- **_has_pytest_suite()** (4 connections) — `scripts/run_all_tests.py`
- **main()** (4 connections) — `scripts/run_all_tests.py`
- **Path** (3 connections)
- **Run every test suite from its own rootdir (BUILD_PLAN §2).  Each services/<nam** (1 connections) — `scripts/run_all_tests.py`
- **Return True if *p* looks like a pytest suite (pytest.ini or tests/ dir present).** (1 connections) — `scripts/run_all_tests.py`
- **Return ordered list of directories to run pytest in.      Services come first** (1 connections) — `scripts/run_all_tests.py`
- **Run all discovered suites; return 0 on full success, 1 on any failure.** (1 connections) — `scripts/run_all_tests.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `scripts/run_all_tests.py`

## Audit Trail

- EXTRACTED: 24 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*