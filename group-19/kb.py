from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import wikipedia
from typing import List, Dict
import time
def search_wikidata(mention):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?entity ?entityLabel WHERE {{
    ?entity rdfs:label "{mention}"@en.
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 5
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # A list of 5, with each element as {entity, entityLabel}
    # return [(i['entity']['value'], i['entityLabel']['value']) for i in results["results"]["bindings"]]
    return [{"wikidata_uri":i['entity']['value'], "wikipedia_link": fetch_wikipedia_link(extract_wikidata_id(i['entity']['value'])), "description": fetch_entity_details(extract_wikidata_id(i['entity']['value']))} for i in results["results"]["bindings"]]


def fetch_wikipedia_link(entity_id, language="en"):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    response = requests.get(url)
    data = response.json()
    
    # Navigate to sitelinks and find the desired language
    sitelinks = data["entities"][entity_id]["sitelinks"]
    wikipedia_key = f"{language}wiki"  # Example: "enwiki" for English Wikipedia
    if wikipedia_key in sitelinks:
        return sitelinks[wikipedia_key]["url"]
    else:
        return None

import requests

def fetch_entity_details(entity_id, language="en"):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    response = requests.get(url)
    data = response.json()
    # Get description
    description = data["entities"][entity_id]["descriptions"].get(language, {}).get("value", "No description available")

    # Get Wikipedia link
    sitelinks = data["entities"][entity_id]["sitelinks"]
    wikipedia_key = f"{language}wiki"  # Example: "enwiki" for English Wikipedia
    # wikipedia_url = sitelinks[wikipedia_key]["url"] if wikipedia_key in sitelinks else None

    return description

def extract_wikidata_id(uri):
    # Split the URI by '/' and take the last part
    return uri.split('/')[-1]


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

if __name__ == "__main__":
    print(query_wikidata_api("apple"))
