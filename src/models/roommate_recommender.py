import numpy as np
from sklearn.neighbors import NearestNeighbors
import logging
from typing import List, Tuple, Dict, Optional

class RoommateRecommender:
    def __init__(self, n_neighbors: int = 20):
        """
        Initialize the roommate recommender.
        
        Args:
            n_neighbors (int): Number of neighbors to return (default 20)
        """
        self.n_neighbors = min(n_neighbors, 100)  # Cannot be more than fetched users
        self.model = NearestNeighbors(n_neighbors=self.n_neighbors, metric='euclidean')
        
    def _extract_feature_vector(self, user: Dict) -> List[float]:
        """
        Extract feature vector from user preferences.
        
        Args:
            user (Dict): User document from MongoDB
            
        Returns:
            List[float]: Feature vector for KNN
        """
        preferences = user.get("preferences", {})
        return [
            preferences.get("cleanliness", 0),
            preferences.get("alcohol", 0),
            preferences.get("marijuana", 0),
            preferences.get("smoking", 0),
            # additional preference features here
        ]
    
    def _filter_by_preferences(self, target_user: Dict, potential_matches: List[Dict]) -> List[Dict]:
        """
        Filter users based on target user's preferences.
        
        Args:
            target_user (Dict): The user seeking matches
            potential_matches (List[Dict]): List of potential matches
            
        Returns:
            List[Dict]: Filtered list of users matching preferences
        """
        target_prefs = target_user.get("preferences", {})
        
        # Get deal-breaker preferences
        required_prefs = {
            "smoking_preference": target_prefs.get("smoking_required"),
            "pets_preference": target_prefs.get("pets_required"),
            "gender_preference": target_prefs.get("gender_required"),
            # Add other deal-breaker preferences here
        }
        
        filtered_matches = []
        for user in potential_matches:
            user_prefs = user.get("preferences", {})
            matches_required = all(
                user_prefs.get(key) == value 
                for key, value in required_prefs.items() 
                if value is not None
            )
            
            if matches_required:
                filtered_matches.append(user)
                
        return filtered_matches

    def get_recommendations(
        self, 
        target_user: Dict,
        school_users: List[Dict],
        max_recommendations: int = 20
    ) -> List[Tuple[Dict, float]]:
        """
        Get roommate recommendations for a target user from a pool of users.
        
        Args:
            target_user (Dict): The user seeking recommendations
            school_users (List[Dict]): Pool of users from the same school
            max_recommendations (int): Maximum number of recommendations to return
            
        Returns:
            List[Tuple[Dict, float]]: List of (user, similarity_score) tuples
        """
        if not school_users:
            logging.warning("No potential matches found in the school")
            return []
            
        # First filter by hard preferences
        filtered_users = self._filter_by_preferences(target_user, school_users)
        
        if not filtered_users:
            logging.warning("No users match the required preferences")
            return []
            
        # Extract feature vectors for KNN
        target_vector = np.array(self._extract_feature_vector(target_user)).reshape(1, -1)
        user_vectors = np.array([self._extract_feature_vector(user) for user in filtered_users])
        
        # Fit model and find neighbors
        try:
            self.model.fit(user_vectors)
            distances, indices = self.model.kneighbors(target_vector)
            
            # Create recommendations list
            recommendations = []
            for dist, idx in zip(distances[0], indices[0]):
                recommended_user = filtered_users[idx]
                if recommended_user.get("email") != target_user.get("email"):
                    recommendations.append((recommended_user, float(dist)))
            
            # Sort by similarity (distance) and limit to max_recommendations
            return sorted(recommendations, key=lambda x: x[1])[:max_recommendations]
            
        except Exception as e:
            logging.error(f"Error generating recommendations: {str(e)}")
            return []

    @staticmethod
    def format_recommendations(recommendations: List[Tuple[Dict, float]]) -> List[Dict]:
        """
        Format recommendations for API response.
        
        Args:
            recommendations (List[Tuple[Dict, float]]): Raw recommendations
            
        Returns:
            List[Dict]: Formatted recommendations
        """
        return [{
            "email": user["email"],
            "userInfo": user.get("userInfo", {}),
            "preferences": user.get("preferences", {}),
            "similarity_score": round((1 / (1 + score)) * 100, 2)  # Convert distance to similarity percentage
        } for user, score in recommendations]