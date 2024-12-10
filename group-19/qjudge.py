# Judge if a question is "Yes or No" question
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from tqdm import tqdm
import re

def remove_punctuation_v2(texts):
    ans = []
    for text in texts:
        a = text = re.sub(r'^(Question:|Answer:)\s*', '', text, flags=re.IGNORECASE)
        a = re.sub(r'[^\w\s]', '', a)
        a = a.strip()
        ans.append(a)
    return ans

class QuestionClassifier:
    def __init__(self, model_path='best_model.pth'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f'Using device: {self.device}')
        checkpoint = torch.load(model_path, map_location=self.device)
        
        self.model = BertForSequenceClassification.from_pretrained(
            'bert-base-uncased',
            num_labels=2,
            state_dict=checkpoint['model_state_dict']
        )
        self.model = self.model.to(self.device)
        self.model.eval()

        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        
    def predict(self, question, max_length=128):
        encoding = self.tokenizer.encode_plus(
            question,
            add_special_tokens=True,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask)
            prediction = torch.argmax(outputs.logits, dim=1)

        return prediction.item()

    def predict_batch(self, questions, batch_size=16, max_length=128):
        predictions = []
        
        for i in tqdm(range(0, len(questions), batch_size)):
            batch_questions = questions[i:i + batch_size]
            
            encodings = self.tokenizer.batch_encode_plus(
                batch_questions,
                add_special_tokens=True,
                max_length=max_length,
                padding='max_length',
                truncation=True,
                return_attention_mask=True,
                return_tensors='pt'
            )

            input_ids = encodings['input_ids'].to(self.device)
            attention_mask = encodings['attention_mask'].to(self.device)

            with torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                batch_predictions = torch.argmax(outputs.logits, dim=1)
                predictions.extend(batch_predictions.cpu().numpy())

        return predictions

if __name__ == "__main__":
    classifier = QuestionClassifier('best_model.pth')

    test_questions = remove_punctuation_v2([
        "What is the capital of France?",
        "Is the sky blue?",
        "How many continents are there?",
        "Can dogs fly?",
        "is Managua the capital of Nicaragua?",
        "What is the capital of Nicaragua?",
        "the capital of nicaragua is...",
        "Managua is not the capital of Nicaragua. Yes or no?",
        "Question: Is it true that that China is the country with most people in the world? Answer: ",
        "The largest company in the world by revenue is Apple",
        "Question: Who is the director of Pulp Fiction? Answer: ",
        "Question: Is it true that the monarch of England is also the monarch of Canada? Answer: "
    ])

    batch_predictions = classifier.predict_batch(test_questions)
    for question, prediction in zip(test_questions, batch_predictions):
        print(f"问题: {question}")
        print(f"预测类型: {prediction} ({'TREC' if prediction == 0 else 'BoolQ'})\n")
