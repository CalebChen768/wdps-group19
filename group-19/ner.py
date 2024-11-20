import spacy

class NER:
    def __init__(self, model="en_core_web_sm"):
        self.model = spacy.load(model)
    
    def extract_entities(self, text):
        doc = self.model(text)
        entities = []
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))
        return entities

if __name__=="__main__":
    ner = NER()
    entities = ner.extract_entities("Apple is a company based in Cupertino, California.")
    print(entities)