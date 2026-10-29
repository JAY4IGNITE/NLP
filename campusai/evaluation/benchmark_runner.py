"""Academic benchmark runner. Re-exported from backend.evaluation.benchmark_runner."""
from backend.evaluation.benchmark_runner import (
    BenchmarkEvaluator,
    BENCHMARK_QUERIES
)

__all__ = ["BenchmarkEvaluator", "BENCHMARK_QUERIES"]

if __name__ == "__main__":
    evaluator = BenchmarkEvaluator()
    summary = evaluator.run_benchmark()
