import React, { useEffect, useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack"; // ✅ Ensure stack is used
import AuthStack from "./AuthStack";
import MainTabNavigator from "./MainTabNavigator";
import { useAuth } from "@/contexts/AuthContext";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { ActivityIndicator, View } from "react-native";
import { isTokenExpired } from "@/api/api"; // Import validation function
import PreferencesScreen from "@/screens/Auth/Preferences"; // ✅ Ensure correct path

// ✅ Define Root Stack Types
export type RootStackParamList = {
  MainTabs: undefined;
  Preferences: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function AppNavigator() {
  const { token, setToken } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const storedToken = await AsyncStorage.getItem("session_token");
        console.log("Stored Token in AsyncStorage:", storedToken);

        if (storedToken && !isTokenExpired(storedToken)) {
          setToken(storedToken);
        } else {
          await AsyncStorage.removeItem("session_token"); // Remove expired token
          setToken(null);
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
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" color="#0000ff" />
      </View>
    );
  }

  console.log("Current Token:", token);

  return (
    <NavigationContainer>
      {token ? (
        <Stack.Navigator>
          <Stack.Screen
            name="MainTabs"
            component={MainTabNavigator}
            options={{ headerShown: false }} // Hide header for tab navigator
          />
          <Stack.Screen name="Preferences" component={PreferencesScreen} />
        </Stack.Navigator>
      ) : (
        <AuthStack />
      )}
    </NavigationContainer>
  );
}
