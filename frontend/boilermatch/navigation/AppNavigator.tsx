import React, { useEffect, useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import AuthStack from "./AuthStack";
import MainTabNavigator from "./MainTabNavigator";
import { useAuth } from "@/contexts/AuthContext";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { ActivityIndicator, View } from "react-native";
import { isTokenExpired } from "@/api/api";
import PreferencesScreen from "@/screens/Auth/Preferences";
import UserInfo from "@/screens/Auth/UserInfo";  
import UserInfoRegister from "@/screens/Auth/UserInfoRegister"; // ✅ Import new registration page

import type { RootStackParamList } from "@/navigation/types";

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function AppNavigator() {
  const { token, setToken, isNewUser, setIsNewUser } = useAuth();
  const [loading, setLoading] = useState(true);
  //const [isNewUser, setIsNewUser] = useState(false);

  useEffect(() => {
  const checkLoginStatus = async () => {
    try {
      const storedToken = await AsyncStorage.getItem("session_token");
      console.log("Stored Token in AsyncStorage:", storedToken);

      if (storedToken && !isTokenExpired(storedToken)) {
        setToken(storedToken);

        //const newUserFlag = await AsyncStorage.getItem("is_new_user");
        //console.log("🟢 Debug: Retrieved is_new_user BEFORE setting state:", newUserFlag);

        // ✅ Ensure correct boolean conversion
        //setIsNewUser(newUserFlag === "true");
      } else {
        await AsyncStorage.removeItem("session_token");
        setToken(null);
        setIsNewUser(false);
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
  console.log("Is New User:", isNewUser);

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {token ? (
          isNewUser ? (
            // ✅ New users must go through onboarding
            <>
              <Stack.Screen name="UserInfo" component={UserInfo} />
              <Stack.Screen name="Preferences" component={PreferencesScreen} />
              <Stack.Screen name="MainTabNavigator" component={MainTabNavigator} />
            </>
          ) : (
            // ✅ Logged-in users go directly to main app
            <>
              <Stack.Screen name="MainTabNavigator" component={MainTabNavigator} />
              <Stack.Screen name="Preferences" component={PreferencesScreen} />
            </>
          )
        ) : (
          <Stack.Screen name="Auth" component={AuthStack} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
