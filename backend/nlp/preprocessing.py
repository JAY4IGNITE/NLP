"""Domain-aware NLP Preprocessing pipeline.
Preserves university acronyms, course codes, unit numbers, and curriculum entities.
"""
import re
from typing import List, Set

PROTECTED_ENTITIES: Set[str] = {
    "dbms", "os", "cn", "ml", "ai", "dsa", "wt", "se", "cd", "cc", "bda", "dm", "cns", "sa", "iot",
    "cse", "cs", "it", "ece", "eee", "ce", "min", "pt", "mech", "civil", "mining", "petroleum",
    "co1", "co2", "co3", "co4", "co5",
    "unit", "module", "sem", "semester", "credits", "prereq", "prerequisite",
    "sql", "tcp", "udp", "ip", "cpu", "cia", "sgpa", "cgpa", "srs", "uml", "bos"
}

RAW_STOPWORDS: Set[str] = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she",
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
    "theirs", "themselves", "is", "am", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "having", "do", "does", "did", "doing",
    "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "into",
    "through", "during", "to", "from", "up", "down", "in", "out", "on", "off",
    "over", "under", "again", "further", "then", "once", "here", "there"
}

STOP_WORDS: Set[str] = RAW_STOPWORDS - {
    "what", "which", "how", "who", "where", "why", "before", "after", "not", "all", "between"
}

try:
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
except Exception:
    lemmatizer = None


class TextPreprocessor:
    """Domain-specific text cleaner and tokenizer for university academic queries."""

    def __init__(self, remove_stopwords: bool = False, lemmatize: bool = True):
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize

    def clean_text(self, text: str) -> str:
        """Lowercase and normalize quotation marks and dashes."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"[\u2018\u2019]", "'", text)
        text = re.sub(r"[\u201c\u201d]", '"', text)
        text = re.sub(r"[\u2013\u2014]", "-", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokenize preserving alphanumeric course codes, unit specifications, acronyms, and Telugu script."""
        cleaned = self.clean_text(text)
        tokens = re.findall(r"\b[a-z0-9\u0C00-\u0C7F]+(?:-[a-z0-9\u0C00-\u0C7F]+)*\b", cleaned)
        return tokens

    def preprocess(self, text: str) -> str:
        """Full pipeline: clean -> tokenize -> domain filter -> lemmatize -> join."""
        tokens = self.tokenize(text)
        processed_tokens: List[str] = []

        for token in tokens:
            if token in PROTECTED_ENTITIES or re.match(r"^241[a-z]{2}[0-9]{3}$", token):
                processed_tokens.append(token)
                continue

            if self.remove_stopwords and token in STOP_WORDS:
                continue

            if self.lemmatize and lemmatizer is not None:
                try:
                    lemma = lemmatizer.lemmatize(token)
                except Exception:
                    lemma = token
                processed_tokens.append(lemma)
            else:
                processed_tokens.append(token)

        return " ".join(processed_tokens)

    def clean_tokens(self, text: str) -> List[str]:
        return self.tokenize(self.preprocess(text))


preprocessor = TextPreprocessor(remove_stopwords=False, lemmatize=True)
nlp_preprocessor = preprocessor


def preprocess_query(query: str) -> str:
    """Convenience helper for query preprocessing."""
    return preprocessor.preprocess(query)
