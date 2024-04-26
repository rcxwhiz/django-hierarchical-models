# poetry run pytest --durations=0 -vv ./tests/benchmark.py::ALMQueryBenchmark

# poetry run pytest --durations=0 -vv ./tests/benchmark.py::PEMQueryBenchmark

poetry run pytest --durations=0 -vv ./tests/benchmark.py::NSMQueryBenchmark

# poetry run pytest --durations=0 -vv ./tests/benchmark.py::ALMEditBenchmark

# poetry run pytest --durations=0 -vv ./tests/benchmark.py::PEMEditBenchmark

poetry run pytest --durations=0 -vv ./tests/benchmark.py::NSMEditBenchmark
