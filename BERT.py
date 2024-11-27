import spacy
import torch
import requests
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict
import time
import wikipedia
from urllib.parse import quote

# 加载spaCy英文模型
nlp = spacy.load("en_core_web_md")

# 加载预训练BERT模型
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

def extract_entities(text: str) -> List[Dict]:
    """实体提取"""
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            'text': ent.text,
            'label': ent.label_,
            'start': ent.start_char,
            'end': ent.end_char
        })
    return entities

def get_bert_embedding(text: str) -> torch.Tensor:
    """获取BERT文本嵌入"""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

def rank_candidates(entity: str, candidates: List[Dict]) -> List[tuple]:
    """对候选实体进行排名"""
    entity_emb = get_bert_embedding(entity)
    
    candidate_scores = []
    for candidate in candidates:
        candidate_emb = get_bert_embedding(candidate['label'])
        similarity = torch.cosine_similarity(entity_emb, candidate_emb)
        candidate_scores.append((candidate, similarity.item()))
    
    return sorted(candidate_scores, key=lambda x: x[1], reverse=True)

def query_wikidata_api(entity: str) -> List[Dict]:
    """使用Wikidata API查询候选实体"""
    base_url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": entity,
        "limit": 5
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        candidates = []
        for result in data.get("search", []):
            candidate = {
                'label': result.get("label", ""),
                'id': result.get("id", ""),
                'description': result.get("description", ""),
                'url': result.get("url", "")
            }
            candidates.append(candidate)
        
        # 添加请求延迟以遵守API限制
        time.sleep(0.1)
        return candidates
    
    except requests.exceptions.RequestException as e:
        print(f"Error querying Wikidata API: {e}")
        return []

def query_wikipedia_api(entity: str) -> List[Dict]:
    """使用Wikipedia API查询候选实体"""
    try:
        # 搜索相关页面
        search_results = wikipedia.search(entity, results=5)
        candidates = []
        
        for title in search_results:
            try:
                # 获取页面摘要
                page = wikipedia.page(title, auto_suggest=False)
                candidate = {
                    'label': title,
                    'id': quote(title.replace(' ', '_')),  # URL-safe title
                    'description': page.summary.split('\n')[0],  # 第一段作为描述
                    'url': page.url
                }
                candidates.append(candidate)
                time.sleep(0.1)  # API 请求延迟
                
            except (wikipedia.exceptions.DisambiguationError, 
                   wikipedia.exceptions.PageError,
                   wikipedia.exceptions.WikipediaException) as e:
                continue
                
        return candidates
        
    except Exception as e:
        print(f"Error querying Wikipedia API: {e}")
        return []


def entity_linking_pipeline(text: str) -> List[Dict]:
    """完整的实体链接流程"""
    # 1. 实体提取
    entities = extract_entities(text)
    
    linked_entities = []
    for entity in entities:
        # 2. 获取候选实体
        # candidates = query_wikidata_api(entity['text'])
        candidates = query_wikipedia_api(entity['text'])
        
        # 3. 候选实体排名
        if candidates:
            ranked_candidates = rank_candidates(entity['text'], candidates)
            best_match = ranked_candidates[0][0]
            confidence = ranked_candidates[0][1]
            
            linked_entities.append({
                'original_entity': entity['text'],
                'entity_type': entity['label'],
                'linked_entity': best_match['label'],
                'wikidata_id': best_match['id'],
                'description': best_match['description'],
                'confidence': confidence,
                'wikidata_url': best_match['url']
            })
    
    return linked_entities


if __name__ == "__main__":
    text = "surely it is but many don’t know this fact that Italy was not always called as Italy. Before Italy came into being in 1861, it had several names including Italian Kingdom, Roman Empire and the Republic of Italy among others. If we start the chronicle back in time, then Rome was the first name to which Romans were giving credit. Later this city became known as “Caput Mundi” or the capital of the world."
    results = entity_linking_pipeline(text)
    
    print("Extracted and Linked Entities:")
    for result in results:
        print("\nOriginal Entity:", result['original_entity'])
        print("Entity Type:", result['entity_type'])
        print("Linked Entity:", result['linked_entity'])
        print("Wikidata ID:", result['wikidata_id'])
        print("Description:", result['description'])
        print("Confidence Score:", round(result['confidence'], 3))
        print("Wikidata URL:", result['wikidata_url'])
