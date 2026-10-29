"""Script to train, evaluate, and benchmark the intent classification model."""
from backend.nlp.intent_classifier import IntentClassifier, intent_classifier


def main():
    print("=" * 60)
    print(" CampusAI Intent Model Training & Evaluation")
    print("=" * 60)

    clf = IntentClassifier()
    metrics = clf.train_and_evaluate()

    print(f"Model Architecture: {metrics['model_type']}")
    print(f"Training Samples:   {metrics['train_samples']}")
    print(f"Validation Samples: {metrics['test_samples']}")
    print(f"Accuracy:           {metrics['accuracy']:.4f}")
    print(f"Macro F1 Score:     {metrics['macro_f1']:.4f}")
    print(f"Weighted F1 Score:  {metrics['weighted_f1']:.4f}")
    print(f"Active Classes:     {metrics['classes_count']}")

    print("\nSample Inferences across English and Telugu:")
    test_queries = [
        "How many credits does Operating Systems have?",
        "What subjects are offered in CSE semester 5?",
        "Explain Unit 3 of Data Structures",
        "What is the course code for Machine Learning?",
        "Compare CSE and IT semester 3",
        "OS credits enni?",
        "CSE 5th semester subjects list ivvandi",
        "Hello CampusAI"
    ]

    for q in test_queries:
        res = clf.predict(q)
        print(f" - \"{q}\"\n   -> Intent: {res.predicted_intent} (Conf: {res.confidence}) [{res.domain}]")


if __name__ == "__main__":
    main()
