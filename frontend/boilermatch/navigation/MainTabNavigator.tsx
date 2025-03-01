import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import ChatScreen from "../screens/Chat/ChatScreen";
import SwipeScreen from "../screens/Home/SwipeScreen";
import SettingsScreen from "../screens/Settings/SettingsScreen";
import { Ionicons } from "@expo/vector-icons";
import FilterButton from "@/components/FilterButton"; // ✅ Import FilterButton
import LogoutButton from "@/components/LogoutButton"; // ✅ Import FilterButton
import { View } from "react-native";
import UserInfo from "@/screens/Auth/UserInfo";

const Tab = createBottomTabNavigator();

export default function MainTabNavigator() {
  return (
    <>
      {/* ✅ Floating Button is added outside of the Tab.Navigator to overlay all screens */}
      <View style={{ flex: 1 }}>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ color, size }) => {
              let iconName: keyof typeof Ionicons.glyphMap = "home"; // Ensures only valid Ionicons names

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

        {/* ✅ Floating Filter Button (on all authenticated screens) */}
        <FilterButton />
        <LogoutButton />
      </View>
    </>
  );
}
