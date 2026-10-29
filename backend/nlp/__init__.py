"""NLP processing, intent classification, and entity extraction package."""
from backend.nlp.preprocessing import TextPreprocessor, preprocessor, nlp_preprocessor, preprocess_query
from backend.nlp.normalizer import normalize_query, DEPARTMENT_ALIASES, COMMON_COURSE_ABBREVIATIONS
from backend.nlp.entity_extractor import AcademicEntityExtractor, entity_extractor
from backend.nlp.intent_classifier import IntentClassifier, IntentClassificationResult, intent_classifier
from backend.nlp.language_id import identify_language
from backend.nlp.taxonomy import INTENT_TAXONOMY, DOMAINS, ACTIVE_INTENTS
from backend.nlp.dataset_generator import IntentDatasetGenerator, IntentExample
from backend.nlp.multi_intent import MultiIntentDecomposer, QueryPlan, SubTask
from backend.nlp.coreference import ContextualQueryRewriter, ConversationContext

__all__ = [
    "TextPreprocessor", "preprocessor", "nlp_preprocessor", "preprocess_query",
    "normalize_query", "DEPARTMENT_ALIASES", "COMMON_COURSE_ABBREVIATIONS",
    "AcademicEntityExtractor", "entity_extractor",
    "IntentClassifier", "IntentClassificationResult", "intent_classifier",
    "identify_language",
    "INTENT_TAXONOMY", "DOMAINS", "ACTIVE_INTENTS",
    "IntentDatasetGenerator", "IntentExample",
    "MultiIntentDecomposer", "QueryPlan", "SubTask",
    "ContextualQueryRewriter", "ConversationContext"
]
