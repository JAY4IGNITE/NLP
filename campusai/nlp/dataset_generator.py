"""Intent dataset generator. Re-exported from backend.nlp.dataset_generator."""
from backend.nlp.dataset_generator import (
    IntentExample,
    SAMPLE_COURSES,
    DEPARTMENTS,
    SEMESTERS,
    UNITS,
    IntentDatasetGenerator
)

__all__ = [
    "IntentExample",
    "SAMPLE_COURSES",
    "DEPARTMENTS",
    "SEMESTERS",
    "UNITS",
    "IntentDatasetGenerator"
]

if __name__ == "__main__":
    gen = IntentDatasetGenerator()
    ds = gen.generate_dataset()
    print(f"Generated {len(ds)} intent examples.")
