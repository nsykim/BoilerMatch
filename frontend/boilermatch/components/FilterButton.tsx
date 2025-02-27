import React from "react";
import { TouchableOpacity, StyleSheet } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "@/navigation/types"; // Ensure this exists
import { Ionicons } from "@expo/vector-icons"; // Uses Ionicons for filter icon

const FilterButton = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  return (
    <TouchableOpacity 
      style={styles.button} 
      onPress={() => navigation.navigate("Preferences")} // Navigates to Preferences screen
    >
      <Ionicons name="filter-outline" size={24} color="white" />
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    position: "absolute",
    top: 90, // Distance from top of screen
    right: 15, // Distance from right side
    backgroundColor: "#007AFF", // Blue color like iOS buttons (customizable)
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
