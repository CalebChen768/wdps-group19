import kb

# Entity Linking class
class EL:
    def __init__(self):
        pass

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

    def rank_candidates(self, candidates):
        pass
    
    





if __name__=="__main__":
    foo = EL()
    print(foo.generate_candidates([('Apple', "abc"), ('California', "def")])) # this is an ad hoc mock data