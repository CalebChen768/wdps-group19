import torch
from transformers import BertTokenizer, BertForSequenceClassification

class BoolQPredictor:
    def __init__(self, model_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
    
    def predict(self, question, passage):
        text = question + " [SEP] " + passage
        inputs = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.softmax(outputs.logits, dim=1)
            predicted_class = torch.argmax(predictions, dim=1)
            confidence = predictions[0][predicted_class.item()].item()
        
        return {
            "answer": "Yes" if predicted_class.item() == 1 else "No",
            "confidence": confidence
        }


if __name__ == "__main__":
    predictor = BoolQPredictor("./boolq_bert_model")
    
    question = "Managua is not the capital of Nicaragua. Yes or no?"
    passage = "Most people think Managua is the capital of Nicaragua.\nHowever, Managua is not the capital of Nicaragua.\nThe capital of Nicaragua is Managua.\nThe capital of Nicaragua is Managua. Managua is the capital of Nicaragua.\nThe capital"
    
    result = predictor.predict(question, passage)
    print(f"Question: {question}")
    print(f"Passage: {passage}")
    print(f"Answer: {result['answer']} (Confidence: {result['confidence']:.2%})")
    