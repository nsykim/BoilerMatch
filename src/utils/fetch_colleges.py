import os
import requests
from typing import Dict, List, Tuple, Union
from dotenv import load_dotenv

load_dotenv()

COLLEGE_SCORECARD_API = "https://api.data.gov/ed/collegescorecard/v1/schools"
MAX_RESULTS = 100

def fetch_colleges(query: str) -> Tuple[Union[List[str], Dict[str, str]], int]:
    """
    Fetch college names from the College Scorecard API.
    
    Args:
        query (str): Search query for college names
    
    Returns:
        Tuple[Union[List[str], Dict[str, str]], int]: Returns either:
            - (list of college names, 200) for successful queries
            - (error dict, error_code) for error cases
    """
    if not query:
        return {"error": "Query parameter is required"}, 400

    params = {
        "api_key": os.getenv("COLLEGE_API_KEY"),
        "school.name": query,
        "fields": "school.name,id",
        "per_page": MAX_RESULTS,
        "sort": "school.name"
    }

    try:
        response = requests.get(COLLEGE_SCORECARD_API, params=params)
        
        # Handle rate limiting
        if response.status_code == 429:
            return {"error": "Rate limit exceeded. Please try again later"}, 429
            
        response.raise_for_status()
        
        results = response.json().get("results", [])
        college_names = [college.get("school.name") for college in results]

        if not college_names:
            return {"error": "No colleges found"}, 404

        return college_names[:MAX_RESULTS], 200

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch colleges: {str(e)}"}, 500