import re
import spacy

class Question_classifier:
    """
    use regex to classify question types:
    """
    def __init__(self):
        # Load the SpaCy English model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Define WH-words and auxiliary verbs
        self.wh_words = {"what", "who", "where", "whom", "whose", "how", "which"}
        self.aux_verbs = {
            "am", "is", "are", "was", "were", "do", "does", "did", "have", "has", "had",
            "can", "could", "shall", "should", "will", "would", "may", "might", "must",
            "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't", "hadn't",
            "can't", "couldn't", "shan't", "shouldn't", "won't", "wouldn't", "mayn't", "mightn't", "mustn't"
        }

    def preprocess_question(self, question):
        # Remove leading and trailing spaces, and convert to lowercase
        question = question.strip().lower()

        # Remove the "question:" prefix if it exists
        question = re.sub(r"^question:\s*", "", question)

        # Keep only words, spaces, question marks, exclamation points, and periods
        question = re.sub(r"[^\w\s?.!]", "", question)

        # Split sentences based on ending punctuation (., ?, !)
        sentences = re.split(r"[.?!]+", question)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Remove sentences with less than or equal to 2 words
        filtered_sentences = []
        for s in sentences:
            if len(s.split()) > 2:
                filtered_sentences.append(s)

        # Reconstruct the question, ending with a question mark if the original ended with one
        if question.endswith('?'):
            reconstructed_question = " ".join(filtered_sentences) + "?"
        else:
            reconstructed_question = " ".join(filtered_sentences)
            if reconstructed_question and not reconstructed_question.endswith('.'):
                reconstructed_question += '.'

        return reconstructed_question.strip()

    def question_classify(self, question):
        """
        Classify the question into the following categories:
        - Category 1: General yes/no questions or complete declarative sentences
        - Category 2: WH-questions, incomplete sentences, or questions requiring completion
        """
        question = self.preprocess_question(question)

        # If the processed question is empty or very short, classify as Category 2
        if not question or len(question.split()) <= 1:
            return 2

        # Define regex patterns
        special_question_pattern = re.compile(
            r"^\s*(?:{})\s+(?:{})\b.*\?$".format("|".join(self.wh_words), "|".join(self.aux_verbs))
        )
        general_question_pattern = re.compile(
            r"^\s*(?:{})\b.*\?$".format("|".join(self.aux_verbs))
        )
        incomplete_special_question_pattern = re.compile(
            r"^\s*(?:{})\b.*".format("|".join(self.wh_words))
        )

        # Check for WH-questions
        if special_question_pattern.match(question):
            return 2  # Special WH-question

        # Check for yes/no questions
        if general_question_pattern.match(question):
            return 1  # General yes/no question

        # Check for incomplete WH-questions
        if incomplete_special_question_pattern.match(question):
            return 2  # Incomplete WH-question

        # Check if the sentence is incomplete or requires completion
        if not question.endswith(".") and not question.endswith("?"):
            return 2  # Incomplete sentence

        # Check if the sentence ends with linking verbs or incomplete semantics
        last_word = question.rstrip('.?').split()[-1] if question else ""
        if last_word in {"is", "are", "was", "were"} or '...' in question:
            return 2

        # Parse the sentence with SpaCy and check for verbs
        doc = self.nlp(question)
        has_verb = any(token.pos_ in ["VERB", "AUX"] for token in doc)
        if not has_verb:
            return 2  # No verbs detected, classify as Category 2

        # Default classification as Category 1 (complete declarative sentence)
        return 1


if __name__ == "__main__":
    classifier = Question_classifier()

    questions = [
        "question: Am I wondering what is this.",
        "Am I wondering what is this.",
        "Do you like coffee?",
        "Isn't it beautiful?",
        "Can this be true?",
        "Do you think i can run faster ???",
        "   Am I going to pass the test?",
        "   is it possible ???",
        "??? can you help",
        "are we good ???",
        "Should I trust this result???",
        "Apple is the richest company in the world",
        "Most people do not know what is the capital of Italy.",

        "Question: What is your name?",
        "zas.f . where were you?",
        "What can I do for you?",
        "question: I am wondering what is this.",
        "question: I am wondering what is the capital of italy.",

        "What do you mean",
        "How could this happen?",
        "the capital of Italy is",
        "the capital of Italy is ...",
        "Question: whAt   is the CaPital of france??????",
        "who  was The first president ???",
        "question: what   do  u   mean   ???",
        "   whereareyou from???     ",
        "which city ??? capital??? italy",
        "??? what ??? your name ???",
        "the name of that place ???"
    ]

    for q in questions:
        category = classifier.question_classify(q)
        print(f"'{q}' => Category {category}")