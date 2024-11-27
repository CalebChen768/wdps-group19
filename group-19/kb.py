from SPARQLWrapper import SPARQLWrapper, JSON
import requests

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
