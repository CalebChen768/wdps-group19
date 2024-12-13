from question_classifier import Question_classifier
from transformers import pipeline
from difflib import SequenceMatcher

class Answer_extract:
    def __init__(self):
        self.question_classifier = Question_classifier()
        self.qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

    def extract(self, question, answer, linked_entities):
        question_category = self.question_classifier.question_classify(question)

        #  a yes/no question
        if question_category == 1:
            # use yes/no model
            pass

        # other questions
        elif question_category == 2:
             # 使用 QA Pipeline 对 LLM 的回答进行进一步验证和提取
            qa_result = self.qa_pipeline(question=question, context=answer)
            qa_extracted_answer = qa_result["answer"]
            # print(f"QA Pipeline Extracted Answer: {qa_extracted_answer}")

            # fuzzy match the extracted answer with linked entities
            matched_entity = self.fuzzy_match(qa_extracted_answer, linked_entities)
            if matched_entity:
                return matched_entity
            else:
                return 0
            
        return 0
    
    def fuzzy_match(self, answer, linked_entities, threshold=0.7):
        best_match = None
        highest_similarity = 0

        for key, entity_data in linked_entities.items():
            # Compare the similarity between the answer and the original name and linked name of the entity
            similarity_original = SequenceMatcher(None, answer.lower(), key.lower()).ratio()
            similarity_linked = SequenceMatcher(None, answer.lower(), entity_data["linked_entity"].lower()).ratio()

            # Use the higher similarity
            similarity = max(similarity_original, similarity_linked)

            # If it exceeds the threshold and is higher than the current best similarity, update the best match
            if similarity > threshold and similarity > highest_similarity:
                best_match = entity_data
                highest_similarity = similarity

        return best_match

    


# Test code
if __name__ == "__main__":
    classifier = Answer_extract()
    question = "What is the capital of Italy?"
    answer = "Rome is the capital of Italy."
    linked_entities = {"Italy":[], "Rome":[]}
    print(classifier.extract(question, answer, linked_entities))