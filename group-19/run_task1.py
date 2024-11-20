from llm import LLM
from ner import NER
import argparse

class Task:
    def __init__(self):
        self.llm = LLM()
        self.ner = NER()
    
    def run(self, question):
        answer = self.llm.ask(question)[0]['text']
        entities = self.ner.extract_entities(answer)

        return entities
    
if __name__ == "__main__":
    # Define command line arguments
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--question", "-q", type=str, default="", help="Question to ask the model")

    task = Task()

    # Parse command line arguments
    # args = parser.parse_args()
    # question = args.question

    while True:
        print("Please input your question:")
        question = input()
        if question == "exit":
            break
        print(task.run(question))

    # .... implement other functions

    