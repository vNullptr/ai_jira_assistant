from clients.llm import MistralClient, LLMClient
from langfuse import get_client
from config import Settings

from datetime import datetime
from collections import defaultdict
from typing import List, Dict
import pandas as pd
import json



TRIALS = 3

def _eval(llm_client : LLMClient, case : str, needles : str, prompt_template_name: str) -> bool:
    result = llm_client.prompt(prompt_template_name, {"thread": case})
    hit = 0
    
    for needle in needles:
        if needle in result.content:
            hit += 1
            
    return hit, len(needles)-hit
    
    
def _format_result(results: Dict, temperature : int, prompt_name: str):
    
    output = ""
    
    output += f"temperature : {temperature} | prompt : {prompt_name}" 
    output += f"\n{"id":<40} {"hit_rate":>10} {"count":>10}\n"
    output += "-" * 62
    
    all_hits = []
    all_misses = []
    
    for id, value  in results.items():
        hit = [trial["hit"] for trial in value]
        miss = [trial["miss"] for trial in value]
        all_hits.extend(hit)
        all_misses.extend(miss)
        
        total = sum(miss) + sum(hit)
        
        
        hit_rate = sum(hit)/total
         
        output += f"\n{id:<40} {hit_rate:>10.1%} {f"{sum(hit)}/{total}":>10}"

    overall = sum(all_hits)/(sum(all_hits)+sum(all_misses))
    output += f"\nOverall : {overall:.1%}"

    return output, overall

if __name__ == "__main__":
    settings = Settings()
    lf_client = get_client()
    testset = pd.read_csv("./eval/test_set.csv")
     
    prompt_name = "issue-thread-prompt"
    temperature = 0.5
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
    
    
    table, overall = _format_result(results=results, temperature=temperature, prompt_name=prompt_name)
    
    print(table)
    
    with open(f"./eval/logs/test-{datetime.now():%Y-%m-%d_%H_%M_%S}.json", "w+") as f:
        
        log = {
            "temperature": temperature,
            "prompt": prompt_name,
            "overall": overall,
            "results": results,
        }
        
        json.dump(log, f)