import sys
import os
import unittest
from unittest.mock import patch
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/utils")))

from fetch_colleges import fetch_colleges

class TestCollegeFetching(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test."""
        load_dotenv()
        self.api_key = os.getenv("COLLEGE_API_KEY")
        self.base_url = "https://api.data.gov/ed/collegescorecard/v1/schools"
        
        # Sample college data for mocking responses
        self.sample_response = {
            "results": [
                {"school.name": "Harvard University"},
                {"school.name": "Harvard College"},
                {"school.name": "Harvard Extension School"}
            ]
        }

    def test_successful_college_fetch(self):
        """Test successful college name fetching."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = self.sample_response
            mock_get.return_value.status_code = 200
            
            results, status_code = fetch_colleges("Harvard")
            
            # Verify the results
            self.assertEqual(status_code, 200)
            self.assertEqual(len(results), 3)
            self.assertIn("Harvard University", results)
            self.assertIn("Harvard College", results)
            
            # Verify the API was called with correct parameters
            mock_get.assert_called_once()
            called_params = mock_get.call_args[1]['params']
            self.assertEqual(called_params['school.name'], "Harvard")
            self.assertEqual(called_params['per_page'], 100)

    def test_empty_query(self):
        """Test behavior with empty search query."""
        result, status_code = fetch_colleges("")
        
        self.assertEqual(status_code, 400)
        self.assertEqual(result, {"error": "Query parameter is required"})

    def test_no_results(self):
        """Test behavior when no colleges match the query."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"results": []}
            
            result, status_code = fetch_colleges("NonexistentUniversity")
            
            self.assertEqual(status_code, 404)
            self.assertEqual(result, {"error": "No colleges found"})

    def test_api_error(self):
        """Test handling of API errors."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("API Error")
            
            result, status_code = fetch_colleges("Harvard")
            
            self.assertEqual(status_code, 500)
            self.assertTrue(isinstance(result, dict))
            self.assertIn("error", result)
            self.assertIn("Failed to fetch colleges", result["error"])

    def test_malformed_response(self):
        """Test handling of malformed API response."""
        with patch('requests.get') as mock_get:
            # Response missing the 'results' key
            mock_get.return_value.json.return_value = {"error": "Invalid response"}
            
            result, status_code = fetch_colleges("Harvard")
            
            self.assertEqual(status_code, 404)
            self.assertEqual(result, {"error": "No colleges found"})

    def test_api_rate_limit(self):
        """Test handling of API rate limiting."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 429
            
            result, status_code = fetch_colleges("Harvard")
            
            self.assertEqual(status_code, 429)
            self.assertEqual(result, {"error": "Rate limit exceeded. Please try again later"})

    def test_special_characters(self):
        """Test handling of special characters in search query."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"results": []}
            mock_get.return_value.status_code = 200
            
            # Test with special characters
            result, status_code = fetch_colleges("St. John's")
            
            # Verify the API call was made (not erroring on special chars)
            mock_get.assert_called_once()
            self.assertEqual(status_code, 404)
            self.assertEqual(result, {"error": "No colleges found"})

    def test_pagination_limits(self):
        """Test that results respect the pagination limit."""
        with patch('requests.get') as mock_get:
            # Create response with more than 100 results
            many_results = {
                "results": [
                    {"school.name": f"Test University {i}"} 
                    for i in range(150)
                ]
            }
            mock_get.return_value.json.return_value = many_results
            mock_get.return_value.status_code = 200
            
            results, status_code = fetch_colleges("University")
            
            # Verify we're limiting results appropriately
            self.assertEqual(status_code, 200)
            self.assertLessEqual(len(results), 100)

if __name__ == '__main__':
    unittest.main()