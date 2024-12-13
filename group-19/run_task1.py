from llm import LLM
from ner import NER
from entity_linking import EL
from answer_extract import Answer_extract
import argparse

class Task:
    def __init__(self):
        self.llm = LLM()
        self.ner = NER()
        self.el = EL()
        self.ae = Answer_extract()

    def run(self, question, prompt=False):
        answer = self.llm.ask(question, prompt)[0]['text']
        print(answer)
        # input both question and answer to NER
        entities = self.ner.extract_entities(question + ". " + answer)
        entities_candidates = self.el.generate_candidates(entities)
        linked_entities = self.el.rank_candidates(answer, entities_candidates)
        linked_entities = self.el.get_best_candidate(linked_entities)

        # task2
        extracted_answer = self.ae.extract(question, answer, linked_entities)
        # print(f"question: {question}\n")
        # print(f"answer: {answer}\n")
        # print(f"linked_entities: {linked_entities}\n")
        # print(f"extracted_answer: {extracted_answer}\n")
        # print("\n\n\n\n\n\n\n\n\n\n\n\n\n")
        return answer, linked_entities


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--path",
                        "-p",
                        type=str,
                        default="/home/user/input_and_output/example_input.txt",
                        help="the path of input file")
    parser.add_argument("--prompt",
                        type=bool,
                        default=False,
                        help="whether to use question answering prompting")
    parser.add_argument("--output",
                        "-o",
                        type=str,
                        default="/home/user/input_and_output/final_output.txt",
                        help="the path of output file")


    # Parse command line arguments
    args = parser.parse_args()
    input_path = args.path
    prompt = args.prompt
    output_path = args.output

    task = Task()
        
    # Read input file
    with open(input_path, "r") as file:
        questions = file.readlines()

    for question in questions:
        if question == "\n":
            continue
        question_id = question.split("\t")[0]
        question_text = question.split("\t")[1]
        answer, result = task.run(question_text, prompt)
        with open(output_path, "a") as file:
            file.write(f"{question_id}\tR\"{answer}\"\n")

        for key, value in result.items():
            # append to output file
            with open(output_path, "a") as file:
                file.write(
                    f"{question_id}\tE\"{key}\"\t\"{value['wikidata_url']}\"\n"
                )

    # while True:
    #     print("Please input your question:")
    #     question = input()
    #     if question == "exit":
    #         break
    #     print(task.run(question))

    # print(task.run(question="Managua is not the capital of Nicaragua. Yes or no?"))

    # .... implement other functions
