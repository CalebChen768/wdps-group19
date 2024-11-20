# WDPS assignment

## Run the code
### run in local env
1. copy llm model from the docker image
2. run `pip install -r requirements.txt` to install all the required packages
3. run `python3 -m spacy download en_core_web_sm` to download NER model
4. `cd group-19`
5. `python3 code/run_task1.py` 
6.  
### build docker
1. run `build_container.sh` to start the docker container
2. use `docker exec -it [container id] bash` to enter the container
3. run `pip install -r requirements.txt` to install all the required packages
4. run `python3 -m spacy download en_core_web_sm` to download NER model
5. `cd code`
6. `python3 code/run_task1.py` 
7.  


## Task List

### Task 1
- [x]  Ask question to a LLM and receive its answer -> (llm.py)
- [x]  Entity extraction (Name entity recognition) -> 调用spacy库进行提取 (ner.py)
- [ ]  Entity linking -> 需要我们实现
	- [ ] candidate entity generation 
        - Name Dictionary Based Techniques:
        - Surface Form Expansion: 
        - Search Engine Methods: wikipedia api/wikidata api?
	- [ ] candidate entity ranking
    	- Supervised Ranking Methods: train a model
    	- Unsupervised Ranking Methods: cosine similarity/tf-idf/clustring/....
	- [ ] unlinkable mention prediction
        - Validation Techniques 
	
### Task 2

- [ ]  Relation extraction

### Task 3