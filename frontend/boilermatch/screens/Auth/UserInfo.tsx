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


const UserInfo = () => {
  const [userInfo, setUserInfo] = useState({
    first_name: '',
    last_name: '',
    age: '',
    bio: '',
    hobbies: '',
  });
  const { email, token } = useAuth();

  // ✅ These lines must be inside the component
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const route = useRoute<RouteProp<RootStackParamList, 'UserInfo'>>();


  // Check if user came from registration
  const fromRegister = route.params?.fromRegister ?? false;


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
      await apiPost('/set_user_info', { email, user_info: userInfo }, token);
      console.log("User Info Saved Successfully!");
    } catch (error: any) {
      console.error("API Error:", error);
    } finally {
      // ✅ Only store the flag, but DO NOT navigate
      await AsyncStorage.setItem("is_new_user", "false");
      console.log("AFTER SAVING: is_new_user =", await AsyncStorage.getItem("is_new_user"));
    }
  };
  
  
  
    

  
  return (
    <View style={styles.container}>
      <Text style={styles.header}>User Information</Text>
      <ScrollView style={styles.scrollContainer}>
        {Object.keys(userInfo).map((key) => (
          <TextInput
            key={key}
            style={styles.input}
            placeholder={key.charAt(0).toUpperCase() + key.slice(1)}
            placeholderTextColor={darkTheme.text}
            onChangeText={(text) => handleChange(key, text)}
            value={userInfo[key as keyof typeof userInfo]}
          />
        ))}
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
