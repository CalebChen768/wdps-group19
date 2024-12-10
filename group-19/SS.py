# Sentence similarity

from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from ner import NER
from entity_linking import EL
import re
import numpy as np
import wikipediaapi
import spacy
from scipy.spatial.distance import cdist


def get_wikipedia_text(page_title: str) -> str:
    wiki = wikipediaapi.Wikipedia(
        language="en",
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    )
    page = wiki.page(page_title)
    return page.text


def find_sentences_with_word(text, keyword):
    sentences = split_sentences(text)
    keyword_sentences = [
        sentence for sentence in sentences if keyword.lower() in sentence.lower()
    ]
    return keyword_sentences


def split_sentences(text):
    sentence_endings = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!|。|！|？)(?=\s|$)"
    sentences = re.split(sentence_endings, text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def efficient_similarity_calculation(
    text_list: list, target_text: str, top_k: int = 3, batch_size: int = 32
):
    model = SentenceTransformer("all-distilroberta-v1")
    # model = SentenceTransformer('all-mpnet-base-v2')  # 可更换

    target_embedding = model.encode([target_text], show_progress_bar=False)
    text_embeddings = model.encode(
        text_list, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True
    )

    similarities = 1 - cdist(text_embeddings, target_embedding, metric="cosine")
    similarities = similarities.flatten()

    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = [
        {"text": text_list[idx], "similarity": float(similarities[idx])}
        for idx in top_indices
    ]

    return results


nlp = spacy.load("en_core_web_md")


def extract_adjectives(text: str) -> list:
    doc = nlp(text)
    results = []
    for token in doc:
        if token.pos_ == "NOUN" and not token.ent_type_:
            adjectives = [child.text for child in token.children if child.pos_ == "ADJ"]
            if adjectives:
                results.append(f"{adjectives[0]} {token.text}")
            else:
                results.append(token.text)

    return results


if __name__ == "__main__":
    ner = NER()
    el = EL()

    question = "is Apple the largest company by revenue in the world"
    answer = ""

    adjectives = extract_adjectives(question)
    print("Found adjectives:", adjectives)

    entities = ner.extract_entities(question + " " + answer)
    entities_candidates = el.generate_candidates(entities)
    linked_entities = el.rank_candidates(answer, entities_candidates)
    linked_entities = el.get_best_candidate(linked_entities)
    ent1 = linked_entities[entities[0][0]]
    url = ent1["linked_entity"]
    text = get_wikipedia_text(url)
    paragraphs = []
    for adj in adjectives:
        sentences = find_sentences_with_word(text, adj)
        paragraphs += sentences
    paragraphs = list(set(paragraphs))
    print(efficient_similarity_calculation(paragraphs, question))
