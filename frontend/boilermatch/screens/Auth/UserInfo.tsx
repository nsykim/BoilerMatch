import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert, ScrollView } from 'react-native';
import React, { useState } from 'react';
import { darkTheme } from '@/styles/theme';
import { apiPost } from '@/api/api';
import { useAuth } from '@/contexts/AuthContext';

import { useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '@/navigation/types';
import { RouteProp } from '@react-navigation/native';

import AsyncStorage from "@react-native-async-storage/async-storage";

//IMAGE Section
import * as ImagePicker from 'expo-image-picker';
import { Image } from 'react-native'; // Add this for image preview



const UserInfo = () => {
  const [userInfo, setUserInfo] = useState({
    first_name: '',
    last_name: '',
    age: '',
    bio: '',
    hobbies: [] as string[],
  });
  const [hobbyInput, setHobbyInput] = useState('');
  const { email, token, isNewUser, setIsNewUser } = useAuth();

  //for image picking
  const [image, setImage] = useState<string | null>(null);

  // ✅ These lines must be inside the component
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const route = useRoute<RouteProp<RootStackParamList, 'UserInfo'>>();
  //const navigation = { navigate: () => {} } as any;
  //const route = { params: { fromRegister: false } } as any;


  // Check if user came from registration
  const fromRegister = route.params?.is_new_user ?? false;

  const addHobby = () => {
    if (hobbyInput.trim()) {
      setUserInfo(prev => ({ ...prev, hobbies: [...prev.hobbies, hobbyInput.trim()] }));
      setHobbyInput('');
    }
  };

  const handleChange = (field: string, value: string) => {
    setUserInfo(prev => ({ ...prev, [field]: value }));
  };



  const handleSubmit = async () => {
    if (!userInfo.first_name || !userInfo.last_name || !userInfo.age || !userInfo.bio) {
      Alert.alert('Error', 'Please fill out all required fields.');
      return;
    }
  
    try {
      if (!token) {
        throw new Error("Invalid session token");
      }
      await apiPost('/set_user_info', { email, user_info: {userInfo, profile_image: image} }, token);
      console.log("User Info Saved Successfully!");
    } catch (error: any) {
      console.error("API Error:", error);
    } finally {
      // 🟢 If it's a new user, continue onboarding to preferences
      if (isNewUser) {
        setIsNewUser(false);
        await AsyncStorage.setItem("is_new_user", "false");
        navigation.replace("Preferences");
      } else {
        // 🔵 Otherwise, just route to main tabs (e.g., after editing user info)
        navigation.replace("MainTabNavigator");
      }
      console.log("AFTER SAVING: is_new_user =", await AsyncStorage.getItem("is_new_user"));
    }
  };
  
  const handlePickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'Camera roll permissions are required.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
      base64: true,
    });

    if (!result.canceled && result.assets[0].base64) {
      const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
      setImage(base64Image);
    }
  };

  
    

  
  return (
    <View style={styles.container}>
      <Text style={styles.header}>User Information</Text>
      <ScrollView style={styles.scrollContainer}>
        {['first_name', 'last_name', 'age', 'bio'].map((key) => (
          <TextInput
            key={key}
            style={styles.input}
            placeholder={key.charAt(0).toUpperCase() + key.slice(1)}
            placeholderTextColor={darkTheme.text}
            onChangeText={(text) => handleChange(key, text)}
            value={userInfo[key as keyof typeof userInfo] as string}
          />
        ))}

        {image && (
          <Image
            source={{ uri: image }}
            style={{ width: 200, height: 200, borderRadius: 10, marginBottom: 15 }}
          />
        )}

        <TouchableOpacity style={styles.submitButton} onPress={handlePickImage}>
          <Text style={styles.submitButtonText}>Upload Profile Image</Text>
        </TouchableOpacity>


          <TextInput
            style={[styles.input, { flex: 1 }]}
            placeholder="Add a hobby"
            placeholderTextColor={darkTheme.text}
            onChangeText={setHobbyInput}
            value={hobbyInput}
          />
        <TouchableOpacity onPress={addHobby}>
          <Text style={{ color: 'white', fontWeight: 'bold' }}>+</Text>
        </TouchableOpacity>

        {userInfo.hobbies.length > 0 && (
          <View style={{ marginBottom: 15 }}>
            {userInfo.hobbies.map((hobby, index) => (
              <Text key={index} style={{ color: darkTheme.text, marginLeft: 5 }}>• {hobby}</Text>
            ))}
          </View>
        )}

        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
          <Text style={styles.submitButtonText}>Save</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: darkTheme.background,
    paddingTop: 100,
  },
  scrollContainer: {
    flex: 1,
    padding: 20,
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    color: darkTheme.text,
    paddingBottom: 10,
  },
  input: {
    color: darkTheme.text,
    borderRadius: 10,
    padding: 10,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: darkTheme.border,
  },
  submitButton: {
    backgroundColor: darkTheme.primary,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginVertical: 20,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default UserInfo;
