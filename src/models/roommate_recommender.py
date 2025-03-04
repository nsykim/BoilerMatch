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
        excluded_keys = {"doesSmoke", "hasPets", "gender"}  # Exclude these from feature vector
        return [
            float(preferences[key]) for key in preferences
            if key not in excluded_keys
        ]
    
    def _filter_by_preferences(self, target_user: Dict, potential_matches: List[Dict]) -> List[Dict]:
        target_prefs = target_user.get("preferences", {})
        filtered_matches = []
        
        # Add logging to see what's happening
        logging.info(f"Target user prefs: {target_prefs}")
        
        for user in potential_matches:
            user_prefs = user.get("preferences", {})
            
            # Log the current user being evaluated
            logging.debug(f"Evaluating user {user.get('email')}, prefs: {user_prefs}")
            
            # Smoking dealbreaker: Only filter if both conditions are true
            if (target_prefs.get("smoking_dealbreaker", 0) == 1 and user_prefs.get("doesSmoke", 0) == 1):
                logging.debug(f"User {user.get('email')} filtered: smoking dealbreaker")
                continue
                
            if (user_prefs.get("smoking_dealbreaker", 0) == 1 and target_prefs.get("doesSmoke", 0) == 1):
                logging.debug(f"User {user.get('email')} filtered: other's smoking dealbreaker")
                continue

            # Pets dealbreaker: Only filter if both conditions are true
            if (target_prefs.get("pets_dealbreaker", 0) == 1 and user_prefs.get("hasPets", 0) == 1):
                logging.debug(f"User {user.get('email')} filtered: pets dealbreaker")
                continue
                
            if (user_prefs.get("pets_dealbreaker", 0) == 1 and target_prefs.get("hasPets", 0) == 1):
                logging.debug(f"User {user.get('email')} filtered: other's pets dealbreaker")
                continue

            # Gender dealbreaker: Check if gender preference exists and is a dealbreaker
            if target_prefs.get("gender_dealbreaker", 0) == 1:
                target_gender_pref = target_prefs.get("gender")
                user_gender = user.get("preferences", {}).get("gender")
                
                # Only filter if we have both gender values to compare
                if target_gender_pref and user_gender and target_gender_pref != user_gender:
                    logging.debug(f"User {user.get('email')} filtered: gender mismatch (target preference)")
                    continue
                    
            if user_prefs.get("gender_dealbreaker", 0) == 1:
                user_gender_pref = user_prefs.get("gender")
                target_gender = target_user.get("preferences", {}).get("gender")
                
                # Only filter if we have both gender values to compare
                if user_gender_pref and target_gender and user_gender_pref != target_gender:
                    logging.debug(f"User {user.get('email')} filtered: gender mismatch (other's preference)")
                    continue

            # If passed all filters, add to matches
            filtered_matches.append(user)

        logging.info(f"Filtered matches count: {len(filtered_matches)} out of {len(potential_matches)}")
        return filtered_matches
    
    def _calculate_similarity_score(self, distance: float) -> float:
        max_distance = np.sqrt(7 * 25)  # Adjusted for 7 features instead of 10
        logging.debug(f"Distance: {distance:.2f}, Max distance: {max_distance:.2f}")
        similarity = max(0, (max_distance - distance) / max_distance)
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
        
        target_vector = np.array(self._extract_feature_vector(target_user)).reshape(1, -1)
        filtered_users = self._filter_by_preferences(target_user, school_users)
        logging.info(f"Filtered users count: {len(filtered_users)}")
        if not filtered_users:
            logging.warning("All users filtered out due to dealbreaker preferences")
            return []
        user_vectors = np.array([self._extract_feature_vector(user) for user in filtered_users])
        
        logging.debug(f"Target vector: {target_vector}")
        logging.debug(f"Number of users: {len(user_vectors)}")
        logging.debug(f"Sample user vector: {user_vectors[0] if len(user_vectors) > 0 else 'No users'}")
        
        try:
            self.model.fit(user_vectors)
            distances, indices = self.model.kneighbors(target_vector)
            
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
            "school": user["school"],
            "userInfo": user.get("userInfo", {}),
            "preferences": user.get("preferences", {}),
            "similarity_score": score
        } for user, score in recommendations]
