import kb
import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict
# Entity Linking class
class EL:
    def __init__(self, model="bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModel.from_pretrained(model)

    def generate_candidates(self, entities:list, source="wikipedia"):
        entities = [entity[0] for entity in entities] # to work with the results of ner
        candidate_map = {}
        if source == "wikidata":
            for entity in entities:
                candidate_map[entity] = kb.query_wikidata_api(entity)
        elif source == "wikipedia":
            for entity in entities:
                candidate_map[entity] = kb.query_wikipedia_api(entity)
        else:
            print("Invalid Source")
        return candidate_map



    def _get_bert_embedding(self, text: str) -> torch.Tensor:
        """获取BERT文本嵌入"""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1)

    def _rank_candidates(self, entity: str, candidates: List[Dict]) -> List[tuple]:
        """对候选实体进行排名"""
        entity_emb = self._get_bert_embedding(entity)
        
        candidate_scores = []
        for candidate in candidates:
            # print(candidate)
            # raise ValueError("WTF")
            candidate_emb = self._get_bert_embedding(candidate['description'])
            similarity = torch.cosine_similarity(entity_emb, candidate_emb)
            candidate_scores.append((candidate, similarity.item()))
    
        return sorted(candidate_scores, key=lambda x: x[1], reverse=True)
    def rank_candidates(self, response, candidates):
        linked_entities = []
        for entity in candidates.keys():
            ranked_candidates = self._rank_candidates(response, candidates[entity])
            best_match = ranked_candidates[0][0]
            confidence = ranked_candidates[0][1]
            
            linked_entities.append({
                'original_entity': entity,
                # 'entity_type': entity['label'],
                'linked_entity': best_match['label'],
                'wikidata_id': best_match['id'],
                'description': best_match['description'],
                'confidence': confidence,
                'wikidata_url': best_match['url']
            })
        
        return linked_entities
    
    def get_best_candidate(self, ranked_candidates):
        top_candidates = {}
        for item in ranked_candidates:
            original_entity = item['original_entity']
            confidence = item['confidence']
            if (original_entity not in top_candidates) or (confidence > top_candidates[original_entity]['confidence']):
                top_candidates[original_entity] = item
        return top_candidates

    





if __name__=="__main__":
    foo = EL()
    print(foo.rank_candidates(foo.generate_candidates([('Apple', "abc"), ('California', "def")]))) # this is an ad hoc mock data