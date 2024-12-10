# Judge if a question is "Yes or No" question
import torch
from datasets import load_dataset
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np


def setup_environment():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    seed = 42
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)

    return device


class DatasetProcessor:
    def __init__(self, device):
        self.device = device
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    def load_dataset(self):
        return load_dataset("boolq")

    def preprocess_function(self, examples):
        texts = [
            q + " [SEP] " + p for q, p in zip(examples["question"], examples["passage"])
        ]

        tokenized = self.tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors=None,
        )

        labels = [1 if ans else 0 for ans in examples["answer"]]
        tokenized["labels"] = labels

        return tokenized

    def prepare_dataset(self):
        dataset = self.load_dataset()
        processed_dataset = dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=dataset["train"].column_names,
        )
        return processed_dataset


class BoolQTrainer:
    def __init__(self, device):
        self.device = device
        self.processor = DatasetProcessor(device)

    def compute_metrics(self, pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)

        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, preds, average="binary"
        )
        acc = accuracy_score(labels, preds)

        return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

    def train(self, save_path):
        processed_dataset = self.processor.prepare_dataset()

        model = BertForSequenceClassification.from_pretrained(
            "bert-base-uncased", num_labels=2
        )
        model.to(self.device)

        training_args = TrainingArguments(
            output_dir="./results",
            learning_rate=2e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=3,
            weight_decay=0.01,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            push_to_hub=False,
            logging_dir="./logs",
            logging_steps=100,
            no_cuda=not torch.cuda.is_available(),
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=processed_dataset["train"],
            eval_dataset=processed_dataset["validation"],
            tokenizer=self.processor.tokenizer,
            compute_metrics=self.compute_metrics,
        )

        print("Starting training...")
        trainer.train()

        eval_results = trainer.evaluate()
        print(f"Evaluation Results: {eval_results}")

        self.save_model(model, self.processor.tokenizer, save_path)

        return model, self.processor.tokenizer

    def save_model(self, model, tokenizer, path):
        model.save_pretrained(path)
        tokenizer.save_pretrained(path)
        print(f"Model and tokenizer saved to {path}")


def main():
    try:
        device = setup_environment()

        trainer = BoolQTrainer(device)

        model, tokenizer = trainer.train(save_path="./boolq_bert_model")

        print("Training completed successfully!")

    except Exception as e:
        print(f"Error during training: {str(e)}")
        raise


if __name__ == "__main__":
    main()
