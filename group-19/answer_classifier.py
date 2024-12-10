from question_classifier import Question_classifier


class Answer_classifier:
    def __init__(self):
        self.question_classifier = Question_classifier()
    
    def answer_classify(self, question, answer, linked_entities):
        """
        Classify the answer based on the question type:
        - yes/no questions: Category 1
        - entity-related questions: Category 2
        """
        question_category = self.question_classifier.question_classify(question)

        if question_category == 1:
            # use yes/no model
            pass
        
        elif question_category == 2:
            # Extract entities from the question
            question_entities = set()
            doc_question = self.question_classifier.nlp(question)
            for ent in doc_question.ents:
                question_entities.add(ent.text.lower())

            # if there is no entity, return first entity in linked_entities
            if not question_entities:
                for entity in linked_entities:
                    return entity
            else:
                # TODO: if there are entities, return the entity that is most relevant to the question
                pass
     
        
        return 0
    


# Test code
if __name__ == "__main__":
    classifier = Answer_classifier()
    question = "What is the capital of Italy?"
    answer = "Rome is the capital of Italy."
    linked_entities = {"Italy":[], "Rome":[]}
    print(classifier.answer_classify(question, answer, linked_entities))