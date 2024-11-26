from SPARQLWrapper import SPARQLWrapper, JSON

def search_wikidata(mention):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?entity ?entityLabel WHERE {{
    ?entity rdfs:label "{mention}"@en.
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 10
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # A list of 10, with each element as {entity, entityLabel}
    return results["results"]["bindings"]

    