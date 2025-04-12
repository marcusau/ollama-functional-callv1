
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class SearchParameters(BaseModel):
    """Parameters for Google search function"""
    query: str = Field(..., description="Search term to look up")

class FunctionCall(BaseModel):
    """Model for function calls from the LLM"""
    name: str = Field(..., description="Name of the function to call")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the function")

class SearchResult(BaseModel):
    """Model for search results"""
    title: str
    link: str
    snippet: str

    def to_string(self) -> str:
        """Convert search result to formatted string"""
        return f"Title: {self.title}\nLink: {self.link}\nSnippet: {self.snippet}"
