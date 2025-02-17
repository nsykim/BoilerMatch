import numpy as np
from sklearn.neighbors import NearestNeighbors
import logging
from typing import List, Tuple, Dict

class RoommateRecommender:
    def __init__(self, n_neighbors: int = 20):
        self.n_neighbors = min(n_neighbors, 100)
        self.model = NearestNeighbors(n_neighbors=self.n_neighbors, metric='euclidean')
        
    def _extract_feature_vector(self, user: Dict) -> List[float]:
        preferences = user.get("preferences", {})
        return [
            float(preferences.get("Age", 0)),  # Make sure we're getting floats
            float(preferences.get("Alcohol", 0)),
            float(preferences.get("Cleanliness", 0)),
            float(preferences.get("Gender", 0)),
            float(preferences.get("Noise", 0)),
            float(preferences.get("Pets", 0)),
            float(preferences.get("Politics", 0)),
            float(preferences.get("Sleep Schedule", 0)),
            float(preferences.get("Smoking", 0)),
            float(preferences.get("Social", 0)),
        ]
    
    def _filter_by_preferences(self, target_user: Dict, potential_matches: List[Dict]) -> List[Dict]:
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
    
    def _calculate_similarity_score(self, distance: float) -> float:
        # Maximum possible distance for 10 features with values 0-5
        max_distance = np.sqrt(10 * 25)  # √(10 * 5²)
        
        # Add debug logging
        logging.debug(f"Distance: {distance:.2f}, Max distance: {max_distance:.2f}")
        
        # Convert distance to similarity score
        similarity = max(0, (max_distance - distance) / max_distance)
        
        # Add debug logging
        logging.debug(f"Raw similarity: {similarity:.4f}")
        
        return round(similarity * 100, 2)

    def get_recommendations(
        self, 
        target_user: Dict,
        school_users: List[Dict],
        max_recommendations: int = 20
    ) -> List[Tuple[Dict, float]]:
        if not school_users:
            logging.warning("No potential matches found in the school")
            return []
        
        # Extract feature vectors
        target_vector = np.array(self._extract_feature_vector(target_user)).reshape(1, -1)
        filtered_users = self._filter_by_preferences(target_user, school_users)
        user_vectors = np.array([self._extract_feature_vector(user) for user in filtered_users])
        
        # Debug logging
        logging.debug(f"Target vector: {target_vector}")
        logging.debug(f"Number of users: {len(user_vectors)}")
        logging.debug(f"Sample user vector: {user_vectors[0] if len(user_vectors) > 0 else 'No users'}")
        
        try:
            self.model.fit(user_vectors)
            distances, indices = self.model.kneighbors(target_vector)
            
            # Debug logging
            logging.debug(f"Raw distances: {distances[0]}")
            
            recommendations = []
            for dist, idx in zip(distances[0], indices[0]):
                recommended_user = filtered_users[idx]
                if recommended_user.get("email") != target_user.get("email"):
                    similarity_score = self._calculate_similarity_score(dist)
                    logging.debug(f"User {recommended_user.get('email')}: distance={dist:.2f}, similarity={similarity_score}")
                    recommendations.append((recommended_user, similarity_score))
            
            return sorted(recommendations, key=lambda x: x[1], reverse=True)[:max_recommendations]
            
        except Exception as e:
            logging.error(f"Error generating recommendations: {str(e)}")
            return []

    @staticmethod
    def format_recommendations(recommendations: List[Tuple[Dict, float]]) -> List[Dict]:
        return [{
            "email": user["email"],
            "userInfo": user.get("userInfo", {}),
            "preferences": user.get("preferences", {}),
            "similarity_score": score
        } for user, score in recommendations]