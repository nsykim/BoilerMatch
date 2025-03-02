import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  Image,
  Button,
  StyleSheet,
  Alert,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useAuth } from "@/contexts/AuthContext";

const ProfileScreen = () => {
  const { token } = useAuth();
  const [profileImage, setProfileImage] = useState<string | null>(null);
  const [userPrompts, setUserPrompts] = useState<{ question: string; answer: string }[]>([]);

  // Load user profile from AsyncStorage or API
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const storedImage = await AsyncStorage.getItem("profileImage");
        if (storedImage) setProfileImage(storedImage);

        const response = await fetch("YOUR_BACKEND_URL/user-profile", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await response.json();
        
        if (data.profileImage) setProfileImage(data.profileImage);
        if (data.prompts) setUserPrompts(data.prompts);
      } catch (error) {
        console.error("Error fetching profile:", error);
      }
    };

    fetchProfile();
  }, []);

  // Function to pick and upload image
  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      const imageUri = result.assets[0].uri;
      setProfileImage(imageUri);
      await AsyncStorage.setItem("profileImage", imageUri);

      // Upload image to backend
      uploadImage(imageUri);
    }
  };

  const uploadImage = async (imageUri: string) => {
    let formData = new FormData();
    formData.append("image", {
      uri: imageUri,
      name: "profile.jpg",
      type: "image/jpeg",
    } as any);

    try {
      const response = await fetch("YOUR_BACKEND_URL/upload-profile", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" },
        body: formData,
      });

      const data = await response.json();
      Alert.alert("Success", "Profile picture updated!");
    } catch (error) {
      Alert.alert("Error", "Failed to upload image.");
      console.error("Upload error:", error);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.profileContainer}>
        <TouchableOpacity onPress={pickImage}>
          {profileImage ? (
            <Image source={{ uri: profileImage }} style={styles.profileImage} />
          ) : (
            <View style={styles.defaultImageContainer}>
              <Text style={styles.defaultImageText}>Select Profile Image</Text>
            </View>
          )}
        </TouchableOpacity>
        <Text style={styles.username}>Your Profile</Text>
      </View>

      <View style={styles.promptsContainer}>
        <Text style={styles.sectionTitle}>Prompts</Text>
        {userPrompts.length > 0 ? (
          userPrompts.map((prompt, index) => (
            <View key={index} style={styles.promptItem}>
              <Text style={styles.promptQuestion}>{prompt.question}</Text>
              <Text style={styles.promptAnswer}>{prompt.answer}</Text>
            </View>
          ))
        ) : (
          <Text style={styles.noPrompts}>No prompts available.</Text>
        )}
      </View>

      <Button title="Change Profile Image" onPress={pickImage} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    backgroundColor: "#f8f8f8",
    alignItems: "center",
  },
  profileContainer: {
    alignItems: "center",
    marginBottom: 20,
  },
  profileImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 2,
    borderColor: "#007AFF",
  },
  defaultImageContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: "#ddd",
    justifyContent: "center",
    alignItems: "center",
  },
  defaultImageText: {
    color: "#666",
  },
  username: {
    fontSize: 20,
    fontWeight: "bold",
    marginTop: 10,
  },
  promptsContainer: {
    width: "100%",
    marginTop: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 10,
  },
  promptItem: {
    backgroundColor: "#fff",
    padding: 10,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
  },
  promptQuestion: {
    fontWeight: "bold",
    fontSize: 16,
  },
  promptAnswer: {
    fontSize: 14,
    marginTop: 5,
    color: "#666",
  },
  noPrompts: {
    fontSize: 14,
    color: "#888",
    textAlign: "center",
    marginTop: 10,
  },
});

export default ProfileScreen;
