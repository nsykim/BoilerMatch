import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import AuthStack from './AuthStack';
import MainTabNavigator from './MainTabNavigator';
import { useAuth } from '@/contexts/AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ActivityIndicator, View } from 'react-native';

export default function AppNavigator() {
  const { token, setToken } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const storedToken = await AsyncStorage.getItem("session_token");
        console.log("Stored Token in AsyncStorage:", storedToken);
  
        if (storedToken) {
          setToken(storedToken);
        } else {
          setToken(null); // Explicitly set null if token is missing
        }
      } catch (error) {
        console.error("Error retrieving session token:", error);
      } finally {
        setLoading(false);
      }
    };
  
    checkLoginStatus();
  }, []);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#0000ff" />
      </View>
    );
  }

  console.log("Current Token:", token);

  return (
    <NavigationContainer>
      {token ? <MainTabNavigator /> : <AuthStack />}
    </NavigationContainer>
  );
}
