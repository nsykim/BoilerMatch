import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, Dimensions } from 'react-native';
import { useAuth } from '@/contexts/AuthContext';
import { apiPost } from '@/api/api';
import { darkTheme } from '@/styles/theme';

interface User {
  school: string;
  userInfo: {
    first_name: string;
    last_name: string;
    age: number;
    school: string;
    bio: string;
  }
}

const SwipeScreen = () => {
  const { email, token } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        if (!token) {
          throw new Error('Invalid session token');
        }
        const response = await apiPost('/get_roommate_recommendations', { email }, token);
        if (response.recommendations) {
          setUsers(response.recommendations);
        } else {
          throw new Error('No recommendations available');
        }
      } catch (error: any) {
        Alert.alert('Error', error.message || 'Failed to load recommendations.');
      }
    };
    fetchRecommendations();
  }, [email, token]);

  const handleSwipe = () => {
    if (currentIndex < users.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      Alert.alert('No more recommendations', 'You have reached the end of your recommendations.');
    }
  };

  if (users.length === 0) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>Loading recommendations...</Text>
      </View>
    );
  }

  const user = users[currentIndex];
  return (
    <View style={styles.container}>
      <View style={styles.cardContainer}>
        <Text style={styles.name}>{user.userInfo.first_name} {user.userInfo.last_name}, {user.userInfo.age}</Text>
        <Text style={styles.school}>{user.school}</Text>
        <View style={styles.bioContainer}>
          <Text style={styles.bio}>{user.userInfo.bio}</Text>
        </View>
        <TouchableOpacity style={styles.button} onPress={handleSwipe}>
          <Text style={styles.buttonText}>Next</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: darkTheme.background,
    padding: 16,
  },
  cardContainer: {
    width: '100%',
    maxWidth: 400,
    padding: 16,
    alignItems: 'center',
  },
  text: {
    color: darkTheme.text,
    fontSize: 18,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: darkTheme.text,
    textAlign: 'center',
  },
  school: {
    fontSize: 18,
    color: darkTheme.primary,
    marginBottom: 10,
    textAlign: 'center',
  },
  bioContainer: {
    width: '100%',
    paddingHorizontal: 10,
  },
  bio: {
    fontSize: 16,
    color: darkTheme.text,
    marginBottom: 20,
    textAlign: 'center',
    width: '100%',
  },
  button: {
    backgroundColor: darkTheme.primary,
    padding: 12,
    borderRadius: 8,
    marginTop: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default SwipeScreen;