import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import AdamW, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import numpy as np
from tqdm import tqdm

class QuestionDataset(Dataset):
    def __init__(self, questions, labels, tokenizer, max_length=128):
        self.tokenizer = tokenizer
        self.questions = questions
        self.labels = labels
        self.max_length = max_length

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, idx):
        question = str(self.questions[idx])
        label = self.labels[idx]

        encoding = self.tokenizer.encode_plus(
            question,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(int(label), dtype=torch.long)
        }

def train():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')

    df = pd.read_csv('combined_questions.csv')
    questions = df['question'].values
    labels = df['label'].values

    train_questions, val_questions, train_labels, val_labels = train_test_split(
        questions, labels, test_size=0.1, random_state=42, stratify=labels
    )

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
    model = model.to(device)

    train_dataset = QuestionDataset(train_questions, train_labels, tokenizer)
    val_dataset = QuestionDataset(val_questions, val_labels, tokenizer)

    train_dataloader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=16)

    optimizer = AdamW(model.parameters(), lr=2e-5)
    
    total_steps = len(train_dataloader) * 3  # 3 epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=total_steps
    )

    best_accuracy = 0
    num_epochs = 3

    for epoch in range(num_epochs):
        print(f'\nEpoch {epoch + 1}/{num_epochs}')
        
        model.train()
        train_loss = 0
        train_steps = 0
        
        for batch in tqdm(train_dataloader, desc="Training"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            model.zero_grad()
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            train_loss += loss.item()
            train_steps += 1

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

        avg_train_loss = train_loss / train_steps
        print(f'Average training loss: {avg_train_loss:.4f}')

        model.eval()
        val_preds = []
        val_true = []
        
        with torch.no_grad():
            for batch in tqdm(val_dataloader, desc="Evaluating"):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )

                preds = torch.argmax(outputs.logits, dim=1)
                val_preds.extend(preds.cpu().numpy())
                val_true.extend(labels.cpu().numpy())

        accuracy = accuracy_score(val_true, val_preds)
        print(f'Validation Accuracy: {accuracy:.4f}')
        print("\nClassification Report:")
        print(classification_report(val_true, val_preds))

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            # 创建保存路径
            save_path = './question_bert_model'
            
            # 使用save_pretrained方法保存模型和分词器
            model.save_pretrained(save_path)
            tokenizer.save_pretrained(save_path)
            print(f"Model and tokenizer saved to {save_path}")


if __name__ == "__main__":
    torch.manual_seed(42)
    np.random.seed(42)
    train()
