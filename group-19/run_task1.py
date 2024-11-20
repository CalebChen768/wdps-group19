from llm import LLM
import argparse

if __name__ == "__main__":
    # Define command line arguments
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--question", "-q", type=str, default="", help="Question to ask the model")

    model = LLM()

    # Parse command line arguments
    # args = parser.parse_args()
    # question = args.question

    while True:
        print("Please input your answer:")
        question = input()
        if question == "exit":
            break
        answers = model.ask(question)

    # .... implement other functions

    