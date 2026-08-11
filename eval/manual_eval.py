from clients.llm import MistralClient, LLMClient

from collections import defaultdict
from typing import List, Dict
import pandas as pd
import statistics, json
from langfuse import get_client
from config import Settings

TRIALS = 3

def _eval(llm_client : LLMClient, case : str, needles : str, prompt_template_name: str) -> bool:
    result = llm_client.prompt(prompt_template_name, {"thread": case})
    hit = 0
    
    for needle in needles:
        if needle in result.content:
            hit += 1
            
    return hit, len(needles)-hit
    
    
def _format_result(results: Dict, temperature : int, prompt_name: str):
    
    print(f"\n{"id":<40} {"hit_rate":>10} {"count":>10}")
    print("-" * 62)
    
    for id, value  in results.items():
        hit = [trial["hit"] for trial in value]
        miss = [trial["miss"] for trial in value]
        total = sum(miss) + sum(hit)
        
        hit_rate = sum(hit)/total
         
        print(f"{id:<40} {hit_rate:>10.1%} {f"{sum(hit)}/{total}":>10}")
    

if __name__ == "__main__":
    settings = Settings()
    lf_client = get_client()
    testset = pd.read_csv("./eval/test_set.csv")
     
    prompt_name = "issue-thread-prompt"
    temperature = 0.3
    results : Dict[str, List] = defaultdict(list)
    
    llm_client = MistralClient(
        temperature=temperature,
        langfuse_client=lf_client
    )
    
    for trial in range(TRIALS):
        for id, case, expecteds in zip(testset["id"], testset["case"], testset["expected"]):
            expected_split = expecteds.split(",") 
            hit, miss = _eval(llm_client, case, expected_split, prompt_name)
            
            results[id].append({"trial": trial, "hit": hit, "miss": miss})
            
            print(f"Progress : case[{id}] - {trial+1}/{TRIALS}")
        

    with open("trial2.json", "w+") as f:
        json.dump(results, f)
        
    
    with open("trial2.json", "r") as f:
        results = json.load(f)
        _format_result(results=results, temperature=temperature, prompt_name=prompt_name)