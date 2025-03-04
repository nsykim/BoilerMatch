import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, Alert, Dimensions, Animated, PanResponder } from 'react-native';
import { useAuth } from '@/contexts/AuthContext';
import { apiPost } from '@/api/api';
import { darkTheme } from '@/styles/theme';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface User {
  email: string;
  school: string;
  userInfo: {
    first_name: string;
    last_name: string;
    age: number;
    school: string;
    bio: string;
    hobbies: string[];
  }
}

const SWIPE_THRESHOLD = 120; // distance required for a swipe to be registered

const SwipeScreen = () => {
  const { email, token } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [likedUsers, setLikedUsers] = useState<User[]>([]); 
  const [passedUsers, setPassedUsers] = useState<User[]>([]); 
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  const position = useRef(new Animated.ValueXY()).current;
  const rotate = position.x.interpolate({
    inputRange: [-SWIPE_THRESHOLD * 2, 0, SWIPE_THRESHOLD * 2],
    outputRange: ['-30deg', '0deg', '30deg'],
    extrapolate: 'clamp'
  });
  
  const likeOpacity = position.x.interpolate({
    inputRange: [0, SWIPE_THRESHOLD],
    outputRange: [0, 1],
    extrapolate: 'clamp'
  });
  
  const passOpacity = position.x.interpolate({
    inputRange: [-SWIPE_THRESHOLD, 0],
    outputRange: [1, 0],
    extrapolate: 'clamp'
  });

  const cardStyle = {
    transform: [
      { translateX: position.x },
      { rotate }
    ]
  };

  useEffect(() => {
    console.log('===== COMPONENT MOUNTED OR DEPENDENCIES CHANGED =====');
    const fetchRecommendations = async () => {
      console.log('Fetching recommendations...');
      try {
        if (!token) {
          console.error('Token is missing');
          throw new Error('Invalid session token');
        }
        const response = await apiPost('/get_roommate_recommendations', { email }, token);
        console.log('API response received:', response ? 'success' : 'empty');
        
        if (response.recommendations) {
          console.log(`Setting ${response.recommendations.length} users`);
          setUsers(response.recommendations);
        } else {
          console.error('No recommendations in response');
          throw new Error('No recommendations available');
        }
      } catch (error: any) {
        console.error('Error fetching recommendations:', error.message);
        Alert.alert('Error', error.message || 'Failed to load recommendations.');
      }
    };
    fetchRecommendations();
  }, [email, token]);

  const handleSwipeLeft = (user: User) => {
    console.log(`=== SWIPE LEFT for ${user.userInfo.first_name} ===`);
    setPassedUsers(prev => {
      console.log(`Adding user to passed list. New count: ${prev.length + 1}`);
      return [...prev, user];
    });
    console.log('Calling advanceToNextUser() from handleSwipeLeft');
    advanceToNextUser();
  };

  const handleLike = async (user: User) => {
    console.log(`=== LIKING ${user.userInfo.first_name} ===`);
  
    try {
      if (!token) {
        console.error("Session token is missing");
        throw new Error("Invalid session token");
      }
  
      const response = await apiPost(
        "/like",
        { email, other: user.email },
        token
      );
  
      if (response && response.chat_id) {
        console.log(`Match created, chat ID: ${response.chat_id}`);
      } else {
        console.log("Like registered, but no match yet.");
      }
    } catch (error: any) {
      console.error("Error liking user:", error.message);
      Alert.alert("Error", error.message || "Failed to like user.");
    }
  };
  
  const handleSwipeRight = (user: User) => {
    console.log(`=== SWIPE RIGHT for ${user.userInfo.first_name} ===`);
    handleLike(user);
    setLikedUsers((prev) => [...prev, user]);
    console.log("Calling advanceToNextUser() from handleSwipeRight");
    advanceToNextUser();
  };

  const usersRef = useRef(users); // Store users state in a ref

  useEffect(() => {
    usersRef.current = users; // Keep ref updated whenever users change
  }, [users]);

  const advanceToNextUser = () => {
    console.log(`=== ADVANCE TO NEXT USER called ===`);
    
    setCurrentIndex(prevIndex => {
      console.log(`Current index before update: ${prevIndex}, Total users: ${usersRef.current.length}`);
      
      if (usersRef.current.length >= 0) {
          console.log(`Incrementing index from ${prevIndex} to ${prevIndex + 1}`);
          
          // Move to the next user
          setIsTransitioning(true);
          setTimeout(() => {
              console.log('Timeout callback executing...');
              position.setValue({ x: 0, y: 0 }); // Reset position
              setIsTransitioning(false);
          }, 300);
          
          return prevIndex + 1;
      } else {
          console.log('No more users to show');
          Alert.alert('No more recommendations', 'You have reached the end of your recommendations.');
          position.setValue({ x: 0, y: 0 }); // Reset position
          return prevIndex; // Prevent incrementing beyond bounds
      }
    });
  };

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => {
        console.log(`onStartShouldSetPanResponder called, isTransitioning: ${isTransitioning}`);
        return !isTransitioning;
      },
      onPanResponderMove: (_, gesture) => {
        position.setValue({ x: gesture.dx, y: 0 });
      },
      onPanResponderRelease: (_, gesture) => {
        console.log(`=== GESTURE RELEASED ===`);
        console.log(`Gesture dx: ${gesture.dx.toFixed(0)}, Threshold: ${SWIPE_THRESHOLD}`);
  
        if (gesture.dx > SWIPE_THRESHOLD) {
          // Swipe right
          console.log('SWIPE RIGHT detected');
          setIsTransitioning(true);
  
          Animated.timing(position, {
            toValue: { x: Dimensions.get('window').width + 100, y: 0 },
            duration: 300,
            useNativeDriver: true
          }).start(({ finished }) => {
            console.log(`Right animation finished: ${finished}`);
  
            setUsers((prevUsers) => {
              console.log(prevUsers[0])
              if (prevUsers.length > 0) {
                console.log(`Calling handleSwipeRight for user: ${prevUsers[0].userInfo.first_name}`);
                handleSwipeRight(prevUsers[0]);
                return prevUsers.slice(1); // Remove swiped user
              } else {
                console.error('No users left to swipe right.');
                setIsTransitioning(false);
                return prevUsers;
              }
            });
          });
        } else if (gesture.dx < -SWIPE_THRESHOLD) {
          // Swipe left
          console.log('SWIPE LEFT detected');
          setIsTransitioning(true);
  
          Animated.timing(position, {
            toValue: { x: -Dimensions.get('window').width - 100, y: 0 },
            duration: 300,
            useNativeDriver: true
          }).start(({ finished }) => {
            console.log(`Left animation finished: ${finished}`);
  
            setUsers((prevUsers) => {
              if (prevUsers.length > 0) {
                console.log(`Calling handleSwipeLeft for user: ${prevUsers[0].userInfo.first_name}`);
                handleSwipeLeft(prevUsers[0]);
                return prevUsers.slice(1); // Remove swiped user
              } else {
                console.error('No users left to swipe left.');
                setIsTransitioning(false);
                return prevUsers;
              }
            });
          });
        } else {
          // Return to center
          console.log('Returning to center');
          Animated.spring(position, {
            toValue: { x: 0, y: 0 },
            friction: 4,
            useNativeDriver: true
          }).start(({ finished }) => {
            console.log(`Return to center animation finished: ${finished}`);
          });
        }
      }
    })
  ).current;  

  const renderCard = () => {
    console.log(
      `Render card. Users: [${users.map(user => user.email).join(", ")}], Current User: ${users[0]?.email}, Transitioning: ${isTransitioning}`
    );
  
    if (users.length === 0) {
      return (
        <View style={styles.emptyStateContainer}>
          <Text style={styles.text}>Loading recommendations...</Text>
        </View>
      );
    }
  
    if (currentIndex >= users.length) {
      return (
        <View style={styles.emptyStateContainer}>
          <Text style={styles.text}>No more recommendations available</Text>
        </View>
      );
    }
  
    const user = users[0];
  
    if (!user?.userInfo) {
      console.log("User info is missing, skipping...");
      return (
        <View style={styles.emptyStateContainer}>
          <Text style={styles.text}>Loading user data...</Text>
        </View>
      );
    }
  
    return (
      <Animated.View style={[styles.cardContainer, cardStyle]} {...panResponder.panHandlers}>
        {/* Overlay indicators */}
        <Animated.View style={[styles.overlayLike, { opacity: likeOpacity }]}>
          <Text style={styles.overlayText}>LIKE</Text>
        </Animated.View>
        <Animated.View style={[styles.overlayPass, { opacity: passOpacity }]}>
          <Text style={styles.overlayText}>PASS</Text>
        </Animated.View>
  
        {/* User details */}
        <Text style={styles.name}>
          {user.userInfo.first_name ?? "Unknown"} {user.userInfo.last_name ?? ""}
        </Text>
        <Text style={styles.bio}>{user.email}</Text>
        <Text style={styles.bio}>{user.userInfo.age}</Text>
        <Text style={styles.school}>{user.school ?? "No school listed"}</Text>
  
        <View style={styles.bioContainer}>
          <Text style={styles.bio}>{user.userInfo.bio ?? "No bio available"}</Text>
        </View>
  
        {user.userInfo.hobbies && user.userInfo.hobbies.length > 0 && (
          <View style={styles.hobbiesContainer}>
            <Text style={styles.hobbiesTitle}>Hobbies:</Text>
            <View style={styles.hobbiesTags}>
              {Array.isArray(user.userInfo.hobbies)
                ? user.userInfo.hobbies.map((hobby, index) => (
                    <View key={index} style={styles.hobbyTag}>
                      <Text style={styles.hobbyText}>{hobby}</Text>
                    </View>
                  ))
                : <Text>{user.userInfo.hobbies}</Text>}
            </View>
          </View>
        )}
      </Animated.View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.statusContainer}>
        <Text style={styles.statusText}>Liked: {likedUsers.length}</Text>
        <Text style={styles.statusText}>Passed: {passedUsers.length}</Text>
      </View>

      {users.length === 0 ? (
        <View style={styles.emptyStateContainer}>
          <Text style={styles.text}>Loading recommendations...</Text>
        </View>
      ) : (
        renderCard()
      )}
      
      <View style={styles.instructions}>
        <Text style={styles.instructionsText}>Swipe right to like, left to pass</Text>
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
  statusContainer: {
    position: 'absolute',
    top: 40,
    width: '100%',
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
  },
  statusText: {
    color: darkTheme.text,
    fontSize: 16,
  },
  cardContainer: {
    width: width - 40,
    maxWidth: 400,
    minHeight: 400,
    padding: 20,
    borderRadius: 12,
    backgroundColor: darkTheme.background || '#222',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
    alignItems: 'center',
    position: 'relative',
  },
  emptyStateContainer: {
    width: width - 40,
    maxWidth: 400,
    minHeight: 400,
    padding: 20,
    borderRadius: 12,
    backgroundColor: darkTheme.background || '#222',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
    alignItems: 'center',
    justifyContent: 'center',
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
    marginTop: 40,
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
    marginBottom: 16,
  },
  bio: {
    fontSize: 16,
    color: darkTheme.text,
    textAlign: 'center',
    width: '100%',
  },
  hobbiesContainer: {
    width: '100%',
    marginBottom: 10,
    alignItems: 'center',
  },
  hobbiesTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: darkTheme.text,
    marginBottom: 8,
  },
  hobbiesTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  hobbyTag: {
    backgroundColor: darkTheme.primary,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20,
    margin: 4,
  },
  hobbyText: {
    color: '#fff',
    fontSize: 14,
  },
  overlayLike: {
    position: 'absolute',
    top: 20,
    right: 20,
    padding: 10,
    borderWidth: 2,
    borderColor: '#4CD964',
    borderRadius: 8,
    transform: [{ rotate: '10deg' }],
    zIndex: 999,
  },
  overlayPass: {
    position: 'absolute',
    top: 20,
    left: 20,
    padding: 10,
    borderWidth: 2,
    borderColor: '#FF3B30',
    borderRadius: 8,
    transform: [{ rotate: '-10deg' }],
    zIndex: 999,
  },
  overlayText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: (darkTheme.text || '#fff'),
  },
  instructions: {
    position: 'absolute',
    bottom: 40,
    padding: 10,
  },
  instructionsText: {
    color: darkTheme.text || '#aaa',
    fontSize: 16,
  },
});

export default SwipeScreen;