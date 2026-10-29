"""Run Comprehensive Benchmark Evaluations on CampusAI."""
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.evaluation.benchmark_runner import BenchmarkEvaluator

def main():
    print("[*] Running Benchmark Evaluator...")
    evaluator = BenchmarkEvaluator()
    summary = evaluator.run_benchmark()
    print("\n" + "=" * 65)
    print("           CAMPUSAI SYSTEM EVALUATION BENCHMARK REPORT")
    print("=" * 65)
    print(f"Total Queries Evaluated:    {summary['total_benchmark_queries']}")
    print(f"Intent Classification Acc:  {summary['intent_accuracy'] * 100:.2f}%")
    print(f"Factual Academic Accuracy:  {summary['factual_academic_accuracy'] * 100:.2f}%")
    print(f"Evidence Grounding Rate:    {summary['grounding_rate'] * 100:.2f}%")
    print(f"Average Latency:            {summary['average_latency_ms']:.2f} ms")
    print(f"95th Percentile Latency:    {summary['p95_latency_ms']:.2f} ms")
    print("=" * 65)

if __name__ == "__main__":
    main()
