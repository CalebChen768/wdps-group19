from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import re
import numpy as np
import wikipediaapi
import spacy
from scipy.spatial.distance import cdist


class Fact_check:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
    
    """
    Args:
    extracted_answer: Expected to be three possible values: "yes", "no" and an entity

    Returns:
    0: incorrect
    1: correct
    2: inconclusive
    """
    def fact_checking(self, question, extracted_answer, linked_entities, answer, threshold=0.60):
        keywords = self._extract_keywords(question)
        if keywords == []:
            return 2
        if extracted_answer == 0:
            return 2
        if extracted_answer in ["Yes", "No"]:
            entities = self._extract_entities(question)
            entities = [linked_entities[i[0]] for i in entities]
            for entity in entities:
                text = self._get_wikipedia_text(entity['linked_entity'])
                paragraphs = []
                for adj in keywords:
                    sentences = self._find_sentences_with_word(text, adj)
                    paragraphs += sentences
                paragraphs = list(set(paragraphs))
                if paragraphs == []:
                    continue
                print("#######################")
                print(self._efficient_similarity_calculation(paragraphs, answer))
                print("#######################")
                evidence_with_confidence = self._efficient_similarity_calculation(paragraphs, answer)
                avg_conf = sum([i['similarity'] for i in evidence_with_confidence])/len([i['similarity'] for i in evidence_with_confidence])

                if avg_conf > threshold:
                    return 1 if extracted_answer == "yes" else 0
                else:
                    return 0 if extracted_answer == "yes" else 1

            return 2 # since none of the entity is conclusive enough to return
        
        else:
            # print(extracted_answer)            
            title = extracted_answer["linked_entity"]
            text = self._get_wikipedia_text(title)
            paragraphs = []
            for adj in keywords:
                sentences = self._find_sentences_with_word(text, adj)
                paragraphs += sentences
            paragraphs = list(set(paragraphs))
            # print(self._efficient_similarity_calculation(paragraphs, answer))
            evidence_with_confidence = self._efficient_similarity_calculation(paragraphs, answer)
            avg_conf = sum([i['similarity'] for i in evidence_with_confidence])/len([i['similarity'] for i in evidence_with_confidence])
            if avg_conf > threshold:
                return 1
            else:
                return 0
        
        
        
    def _get_wikipedia_text(self,page_title: str) -> str:
        wiki = wikipediaapi.Wikipedia(
            language="en",
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        )
        page = wiki.page(page_title)
        return page.text


    def _find_sentences_with_word(self, text, keyword):
        sentences = self._split_sentences(text)
        keyword_sentences = [
            sentence for sentence in sentences if keyword.lower() in sentence.lower()
        ]
        return keyword_sentences


    def _split_sentences(self, text):
        sentence_endings = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!|。|！|？)(?=\s|$)"
        sentences = re.split(sentence_endings, text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]


    def _efficient_similarity_calculation(self,
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



    """
        From text extract candidate keywords.
        To be specific, nouns that are not entities and their adjectives
    """
    def _extract_keywords(self, text: str) -> list:
        doc = self.nlp(text)
        results = []
        for token in doc:
            if token.pos_ == "NOUN" and not token.ent_type_:
                adjectives = [child.text for child in token.children if child.pos_ == "ADJ"]
                if adjectives:
                    results.append(f"{adjectives[0]} {token.text}")
                else:
                    results.append(token.text)

        return results
    def _extract_entities(self, text:str) -> list:
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))
        return entities


# if __name__ == "__main__":
#     ner = NER()
#     el = EL()

#     question = "is Apple the largest company by revenue in the world"
#     answer = ""

#     adjectives = extract_adjectives(question)
#     print("Found adjectives:", adjectives)

#     entities = ner.extract_entities(question + " " + answer)
#     entities_candidates = el.generate_candidates(entities)
#     linked_entities = el.rank_candidates(answer, entities_candidates)
#     linked_entities = el.get_best_candidate(linked_entities)

#     refined answer is entities

#     ent1 = linked_entities[entities[0][0]]
#     url = ent1["linked_entity"]
#     text = get_wikipedia_text(url)
#     paragraphs = []
#     for adj in adjectives:
#         sentences = find_sentences_with_word(text, adj)
#         paragraphs += sentences
#     paragraphs = list(set(paragraphs))
#     print(efficient_similarity_calculation(paragraphs, question))
