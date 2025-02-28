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
import UserInfo from "@/screens/Auth/UserInfo";  // ✅ Ensure correct path



// ✅ Define Root Stack Types
import type { RootStackParamList } from "@/navigation/types";  // ✅ Import from types.ts


const Stack = createNativeStackNavigator<RootStackParamList>();

export default function AppNavigator() {
  const { token, setToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const storedToken = await AsyncStorage.getItem("session_token");
        console.log("Stored Token in AsyncStorage:", storedToken);
  
        if (storedToken && !isTokenExpired(storedToken)) {
          setToken(storedToken);
          const storedUserInfo = await AsyncStorage.getItem("user_info");  // ✅ Fetch user info
          setUserInfo(storedUserInfo ? JSON.parse(storedUserInfo) : null);  // ✅ Parse if exists
        } else {
          await AsyncStorage.removeItem("session_token"); // Remove expired token
          setToken(null);
          setUserInfo(null); // Reset user info
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
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {token ? (
          <>
            {/* ✅ Preferences and MainTabNavigator should always be accessible */}
            <Stack.Screen name="Preferences" component={PreferencesScreen} />
            <Stack.Screen name="MainTabNavigator" component={MainTabNavigator} />
  
            {/* ✅ Show UserInfo only if the user comes from registration */}
            <Stack.Screen name="UserInfo" component={UserInfo} />
          </>
        ) : (
          <>
            <Stack.Screen name="Auth" component={AuthStack} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
  
}
