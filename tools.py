import ollama
import requests
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from model import SearchResult, FunctionCall


MODEL_NAME = "gemma3:1b"


load_dotenv()

SERPER_API_KEY = os.getenv('SERPER_API_KEY')
if not SERPER_API_KEY:
    raise ValueError("Serper API key not found. Please set SERPER_API_KEY in your .env file.")


with open("system_prompt.txt", "r") as f:
    system_prompt = f.read()


def google_search(query: str) -> SearchResult:
    """Perform a Google search using Serper.dev API"""
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        results = response.json()
        
        if not results.get('organic'):
            raise ValueError("No search results found.")
            
        first_result = results['organic'][0]
        return SearchResult(
            title=first_result.get('title', 'No title'),
            link=first_result.get('link', 'No link'),
            snippet=first_result.get('snippet', 'No snippet available.')
        )
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise
    

def parse_response_for_function_call(response: str) -> Optional[FunctionCall]:
    """Parse the model's response to extract function calls"""
    try:
        # Clean the response and find JSON structure
        response = response.strip()
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            return None
            
        json_str = response[start_idx:end_idx]
        data = json.loads(json_str)
        return FunctionCall(**data)
    except Exception as e:
        print(f"Error parsing function call: {str(e)}")
        return None
    
def chat_LLM(user_input: str,model_response: Optional[str] = None,search_result: Optional[str] = None) -> str:
    
    if model_response is None and search_result is None:
        messages=[ {"role": "system", "content": system_prompt},
                   {"role": "user", "content": user_input}  
                 ]
    
    else:
        messages=[
                   {"role": "system", "content": system_prompt},
                   {"role": "user", "content": user_input},
                   {"role": "assistant", "content": model_response},
                   {"role": "user", "content": f"Based on the search results: {search_result.to_string()}"}
                ]
    
    """Chat with the LLM"""
    response = ollama.chat(
    model=MODEL_NAME,
    messages=messages)
    
    return response['message']['content']
    
    
if __name__ == "__main__":
    print(google_search("What is the capital of France?"))