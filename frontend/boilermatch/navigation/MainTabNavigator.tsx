import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import ChatScreen from "../screens/Chat/ChatScreen";
import SwipeScreen from "../screens/Home/SwipeScreen";
import UserInfo from "@/screens/Auth/UserInfo";
import { Ionicons } from "@expo/vector-icons";
import FilterButton from "@/components/FilterButton";
import LogoutButton from "@/components/LogoutButton";
import { View } from "react-native";

const Tab = createBottomTabNavigator();

export default function MainTabNavigator() {
  return (
    <View style={{ flex: 1 }}>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ color, size }) => {
            let iconName: keyof typeof Ionicons.glyphMap = "home";

            if (route.name === "Home") {
              iconName = "home";
            } else if (route.name === "Chat") {
              iconName = "chatbubble";
            } else if (route.name === "Profile") {
              iconName = "person";
            }

            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: "tomato",
          tabBarInactiveTintColor: "gray",
        })}
      >
        <Tab.Screen name="Home" component={SwipeScreen} />
        <Tab.Screen name="Chat" component={ChatScreen} />
        <Tab.Screen name="Profile" component={UserInfo} />
      </Tab.Navigator>

      {/* ✅ Floating Filter and Logout Buttons */}
      <FilterButton />
      <LogoutButton />
    </View>
  );
}
