from llama_cpp import Llama

class LLM:
    def __init__(self, model_path="/home/user/models/llama-2-7b.Q4_K_M.gguf"):
        self.model_path = model_path
        self.llm = Llama(model_path=model_path, verbose=False)
    
    def ask(self, question, prompt=True):
        print("Asking the question \"%s\" to %s (wait, it can take some time...)" % (question, self.model_path))
        
        
        # If wish to use basic question answering prompting, uncomment the following lines.
        
        if prompt:
            # question = f"""<<SYS>>
            #     You're are a helpful Assistant, and you only response to the "Assistant"
            #     Remember, maintain a natural tone. Be precise, concise, and casual. Keep it short
            #     <</SYS>>
            #     [INST]
            #     User:{question}
            #     [/INST]\n
            #     Assistant:"""

            question = f"""
            You are a helpful assistant. Do not include any system prompts, markers, or special symbols in your response. Remember to maintain a natural tone. Be precise, concise, and casual. Keep it short. Please end your response with '<<end>>'.

            User: {question}

            Assistant:"""
            

        output = self.llm(
            question, # Prompt
            max_tokens=32, # Generate up to 32 tokens
            stop=["Q:", "\n\n", "<<", "\"\""], # Stop generating just before the model would generate a new question
            # stop=["Q:"],
            # echo=True # Echo the prompt back in the output
            echo=False # Echo the prompt back in the output
        )
        # print("Here is the output")
        # print("###############################")
        # print(output)
        # print("###############################")

        
        return output['choices']

if __name__=="__main__":
    llm = LLM()
    llm.ask("What is the capital of Italy?")