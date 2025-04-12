import ollama
import requests
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from tools import google_search, parse_response_for_function_call,chat_LLM
from model import  SearchParameters





user_input = input("Enter a query: ")

chat_history = []
chat_history.append({"role": "user", "content": user_input})
search_info = None
        
## step 1: determine if need to search or not
model_first_response = response = chat_LLM(user_input)

print(f"Model response: {model_first_response}")
function_call = parse_response_for_function_call(model_first_response)

print(f"Function call: {function_call}")

## step 2: if need to search, search and get the result
if function_call and function_call.name == "google_search":
    
    
    ### step 2.1: produce the search parameters
    search_params = SearchParameters(**function_call.parameters)

    search_query = search_params.query
            
    # Add search info to history
    search_info = f"🔍 Searching for: {search_query}"

    print(f"Search info: {search_info}")

    chat_history.append({"role": "assistant", "content": search_info})
    
    ## step 2.2: search and get the result
    search_result = google_search(search_query)
    
#     # Update search info with results
    search_result_info = f"🔍 Searched for: {search_query}\n\n📊 Result:\n{search_result.to_string()}"
    
    print(f"Search result info: {search_result_info}\n\n\n")
    
    chat_history[-1] = {"role": "assistant", "content": search_result_info}
    
    ## step 3: load google search result to LLM and produce the final response
    final_response = chat_LLM(user_input,model_first_response,search_result)
    
    print(f"Final response: {final_response}\n\n\n")
    
    assistant_response = final_response
else:
    # If no function call, return the direct response
    assistant_response = model_first_response
    
if search_info:
            # Add both search info and final response
    chat_history.append({"role": "assistant", "content": f"✨ Response:\n{assistant_response}"})
else:
    # Just add assistant response
    chat_history.append({"role": "assistant", "content": assistant_response})

