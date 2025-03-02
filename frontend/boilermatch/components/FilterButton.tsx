import React from "react";
import { TouchableOpacity, StyleSheet } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "@/navigation/types";
import { Ionicons } from "@expo/vector-icons";
import { darkTheme } from "@/styles/theme"; // ✅ Import darkTheme for consistent colors

const FilterButton = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  const goToPreferences = () => {
    console.log("Current Navigation State:", navigation.getState());
    
    try {
      navigation.navigate("Preferences"); // ✅ Directly navigate to Preferences
    } catch (error) {
      console.error("Navigation Error: Could not navigate to Preferences", error);
    }
  };
  

  return (
    <TouchableOpacity style={styles.button} onPress={goToPreferences}>
      <Ionicons name="filter-outline" size={24} color="white" />
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    position: "absolute",
    top: 90, // Distance from top of screen
    right: 15, // Distance from right side
    backgroundColor: darkTheme.primary, // ✅ Same color as "Next" button
    padding: 12,
    borderRadius: 25,
    elevation: 5, // Android shadow
    shadowColor: "#000", // iOS shadow
    shadowOpacity: 0.3,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
  },
});

export default FilterButton;
