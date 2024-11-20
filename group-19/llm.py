from llama_cpp import Llama

class LLM:
    def __init__(self, model_path="../models/llama-2-7b.Q4_K_M.gguf"):
        self.model_path = model_path
        self.llm = Llama(model_path=model_path, verbose=False)
    
    def ask(self, question):
        print("Asking the question \"%s\" to %s (wait, it can take some time...)" % (question, self.model_path))
        output = self.llm(
            question, # Prompt
            max_tokens=32, # Generate up to 32 tokens
            # stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
            stop=["Q:"],
            echo=True # Echo the prompt back in the output
        )
        print("Here is the output")
        print(output['choices'])
        return output['choices']

if __name__=="__main__":
    llm = LLM()
    llm.ask("What is the capital of Italy?")