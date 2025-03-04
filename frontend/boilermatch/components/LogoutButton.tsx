import React from "react";
import { TouchableOpacity, StyleSheet, Alert } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useAuth } from "@/contexts/AuthContext";
import { Ionicons } from "@expo/vector-icons";
import { darkTheme } from "@/styles/theme"; // ✅ Import darkTheme for consistent colors

const LogoutButton = () => {
  const { setToken } = useAuth();

  const handleLogout = async () => {
    Alert.alert("Logout", "Are you sure you want to log out?", [
      { text: "Cancel", style: "cancel" },
      { 
        text: "Logout", 
        onPress: async () => {
          await AsyncStorage.removeItem("session_token");
          setToken(null);
        } 
      },
    ]);
  };

  return (
    <TouchableOpacity style={styles.button} onPress={handleLogout}>
      <Ionicons name="log-out-outline" size={24} color="white" />
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    position: "absolute",
    top: 150, // Positioned below FilterButton
    right: 15,
    backgroundColor: darkTheme.primary, // ✅ Same color as "Next" button
    padding: 12,
    borderRadius: 25,
    elevation: 5,
    shadowColor: "#000",
    shadowOpacity: 0.3,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
  },
});

export default LogoutButton;
