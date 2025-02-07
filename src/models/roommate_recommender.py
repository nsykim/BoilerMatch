import numpy as np
from sklearn.neighbors import NearestNeighbors
import logging
from src.accounts import get_table

# fetch 100 users from api
# plot them and return nearest 20

class RoommateRecommender:
    def __init__(self, client, n_neighbors=5):
        self.client = client
        self.n_neighbors = n_neighbors
        self.model = NearestNeighbors(n_neighbors=n_neighbors, metric='euclidean')
        self.user_ids = []
        self.user_profiles = None

    def fetch_user_profiles(self):
        """Fetches user preferences from the database and trains the KNN model."""
        accounts = get_table(self.client, "boilermatch", "accounts")
        users = list(accounts.find({}, {"_id": 1, "preferences": 1}))  

        user_ids = []
        user_profiles = []

        for user in users:
            user_ids.append(str(user["_id"]))  
            preferences = user.get("preferences", {})
            profile_vector = [
                preferences.get("cleanliness", 0),
                preferences.get("alcohol", 0),
                preferences.get("marijuana", 0),
                preferences.get("smoking", 0),
            ]
            user_profiles.append(profile_vector)

        if user_profiles:
            self.user_ids = np.array(user_ids)
            self.user_profiles = np.array(user_profiles)
            self.model.fit(self.user_profiles)
            logging.info("RoommateRecommender: Model trained successfully.")
        else:
            logging.warning("RoommateRecommender: No user profiles found.")

    def recommend(self, user_id):
        """Returns the most similar users based on preferences."""
        if self.user_profiles is None or len(self.user_profiles) == 0:
            logging.error("RoommateRecommender: Model not trained. Call fetch_user_profiles() first.")
            return []

        try:
            user_index = np.where(self.user_ids == user_id)[0][0]
            user_profile = self.user_profiles[user_index].reshape(1, -1)
        except IndexError:
            logging.error(f"RoommateRecommender: User ID {user_id} not found.")
            return []

        distances, indices = self.model.kneighbors(user_profile)
        recommendations = []

        for dist, idx in zip(distances[0], indices[0]):
            recommended_id = self.user_ids[idx]
            if recommended_id != user_id:
                recommendations.append((recommended_id, dist))

        return sorted(recommendations, key=lambda x: x[1])
