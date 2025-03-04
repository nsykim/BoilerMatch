import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform, TouchableWithoutFeedback, Keyboard, Alert } from 'react-native'
import React, { useState } from 'react'
import { darkTheme } from '@/styles/theme'
import { apiPost } from '@/api/api'
import { useAuth } from '@/contexts/AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

//navigation things
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '@/navigation/types';  // Define this if you haven't already
import UserInfo from "@/screens/Auth/UserInfo";


const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>_+-])[A-Za-z\d!@#$%^&*(),.?":{}|<>_+-]{8,64}$/

const AuthScreen = () => {
  const [isLogin, setIsLogin] = useState(true)
  const [inputEmail, setInputEmail] = useState('')
  const [password, setPassword] = useState('')
  const [school, setSchool] = useState('')
  const [loading, setLoading] = useState(false)
  const { setEmail, setToken } = useAuth()

  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();



  const handleRegister = async () => {
    if (!emailRegex.test(inputEmail)) {
      Alert.alert("Invalid Email", "Please enter a valid email address.");
      return;
    }
  
    if (!passwordRegex.test(password)) {
      Alert.alert(
        "Weak Password",
        "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character."
      );
      return;
    }
  
    setLoading(true);
    try {
      await apiPost("/create_account", { email: inputEmail, password, school });
  
      // ✅ Log in after successful registration
      const { session_token: token } = await apiPost("/login", { email: inputEmail, password });
  
      setEmail(inputEmail);
      setToken(token);
      await AsyncStorage.setItem("email", inputEmail);
      await AsyncStorage.setItem("session_token", token);
  
      // ✅ Correctly store new user flag
      await AsyncStorage.setItem("is_new_user", "true");
  
      // ✅ Debug log to confirm flag is set
      const checkNewUser = await AsyncStorage.getItem("is_new_user");
      console.log("🟡 [DEBUG] AFTER REGISTERING: is_new_user =", checkNewUser);
  
      navigation.replace("UserInfo", {}); // ✅ Ensure correct transition
    } catch (error: any) {
      Alert.alert("Error", error?.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };
  
  
  
  
  
  
  const handleLogin = async () => {
    if (!emailRegex.test(inputEmail)) {
      Alert.alert('Invalid Email', 'Please enter a valid email address.');
      return;
    }

    setLoading(true);
    try {
      const { session_token: token } = await apiPost('/login', { email: inputEmail, password });

      setEmail(inputEmail);
      setToken(token);
      await AsyncStorage.setItem("email", inputEmail);
      await AsyncStorage.setItem("session_token", token);

      // ✅ Only show success message, NO manual navigation
      Alert.alert("Success", "Logged in!");

      // ✅ Correctly store new user flag
      await AsyncStorage.setItem("is_new_user", "false");
  
      // ✅ Debug log to confirm flag is set
      const checkNewUser = await AsyncStorage.getItem("is_new_user");
      console.log("🟡 [DEBUG] AFTER LOGIN: is_new_user =", checkNewUser);

    } catch (error: any) {
      Alert.alert('Error', error?.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };


  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <ScrollView contentContainerStyle={styles.scrollContainer} bounces={true} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
          <Text style={styles.header}>{isLogin ? 'Login' : 'Register'}</Text>

          <TextInput
            style={styles.input}
            placeholder="Email"
            placeholderTextColor={darkTheme.text}
            value={inputEmail}
            onChangeText={setInputEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <TextInput
            style={styles.input}
            placeholder="Password"
            placeholderTextColor={darkTheme.text}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          {!isLogin && <TextInput
            style={styles.input}
            placeholder="School"
            placeholderTextColor={darkTheme.text}
            value={school}
            onChangeText={setSchool}
          />}

          <TouchableOpacity style={styles.button} onPress={isLogin ? handleLogin : handleRegister} disabled={loading}>
            <Text style={styles.buttonText}>{loading ? 'Loading...' : isLogin ? 'Login' : 'Register'}</Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={() => setIsLogin(!isLogin)}>
            <Text style={styles.switchText}>{isLogin ? "Don't have an account? Register" : "Already have an account? Login"}</Text>
          </TouchableOpacity>
        </ScrollView>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  )
}

export default AuthScreen

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: darkTheme.background,
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: darkTheme.text,
  },
  input: {
    width: '100%',
    height: 50,
    borderWidth: 1,
    borderColor: darkTheme.border,
    borderRadius: 8,
    paddingHorizontal: 10,
    marginBottom: 15,
    fontSize: 16,
    backgroundColor: darkTheme.inputBackground,
    color: darkTheme.inputText,
  },
  button: {
    backgroundColor: darkTheme.primary,
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 8,
    marginTop: 10,
  },
  buttonText: {
    color: darkTheme.text,
    fontSize: 16,
  },
  switchText: {
    color: darkTheme.primary,
    marginTop: 10,
  },
})