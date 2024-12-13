import torch
from transformers import BertTokenizer, BertForSequenceClassification, BertConfig
import os

class BoolQPredictor:
    def __init__(self, model_path="yes_no_model.pkl"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        if not os.path.isfile(model_path):
            hugging_face_path = "SomnusYM/Bert-boolq-base"
            self.tokenizer = BertTokenizer.from_pretrained(hugging_face_path)
            self.model = BertForSequenceClassification.from_pretrained(hugging_face_path)
        else:
            with open(model_path, "rb") as f:
                model_data = torch.load(f)
            
            config = BertConfig.from_dict(model_data["config"])
            self.model = BertForSequenceClassification(config)
            self.model.load_state_dict(model_data["model_state_dict"])
            self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
            self.tokenizer.vocab = model_data["tokenizer_state_dict"]

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
    predictor = BoolQPredictor("yes_no_model.pkl")
    
    question = "Managua is not the capital of Nicaragua. Yes or no?"
    passage = "Most people think Managua is the capital of Nicaragua.\nHowever, Managua is not the capital of Nicaragua.\nThe capital of Nicaragua is Managua."
    
    result = predictor.predict(question, passage)
    print(f"Question: {question}")
    print(f"Passage: {passage}")
    print(f"Answer: {result['answer']} (Confidence: {result['confidence']:.2%})")
    