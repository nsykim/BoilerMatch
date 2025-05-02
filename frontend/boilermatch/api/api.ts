import { Alert } from 'react-native';
import { API_BASE_URL } from '@/config/config';
import { jwtDecode } from "jwt-decode";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useAuth } from '@/contexts/AuthContext';

//checks if your token expired
export const isTokenExpired = (token: string): boolean => {
  try {
    const decoded: any = jwtDecode(token); // Decode JWT
    const now = Date.now() / 1000; // Convert to seconds
    return decoded.exp < now; // Return true if expired
  } catch (error) {
    console.error("Invalid token:", error);
    return true; // Treat invalid tokens as expired
  }
};

const apiGet = async (endpoint: string, token?: string) => {
  try {
    const headers: Record<string, string> = {
      Accept: "application/json",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "GET",
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        await AsyncStorage.removeItem("session_token");
        await AsyncStorage.removeItem("email");
        useAuth().setToken(null);
        Alert.alert("Session Expired", "Your session has expired. Please log in again.");
        return null;
      }
      const errorText = await response.text();
      throw new Error(errorText || "Error with GET request");
    }

    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error("API GET Error:", error);
    throw error;
  }
};

const apiPost = async (endpoint: string, body: object, token?: string, chat_id?: string) => {
  try {
    console.log(`${API_BASE_URL}${endpoint}`);

    // ✅ 1️⃣ Check if the token is expired **before** making a request
    if (token && isTokenExpired(token)) {
      console.log("JWT expired. Logging out...");
      await AsyncStorage.removeItem("session_token"); // Clear storage
      await AsyncStorage.removeItem("email"); 
      useAuth().setToken(null); // Update state to log out
      Alert.alert("Session Expired", "Your session has expired. Please log in again.");
      return null;
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (chat_id) {
      headers["Chat-Id"] = chat_id
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });

    console.log(response);

    // ✅ 2️⃣ Handle 401 Unauthorized (Expired Token) and log out
    if (!response.ok) {
      if (response.status === 401) { // Token is invalid/expired
        console.log("Unauthorized request. Logging out...");
        await AsyncStorage.removeItem("session_token");
        await AsyncStorage.removeItem("email");
        useAuth().setToken(null);
        Alert.alert("Session Expired", "Your session has expired. Please log in again.");
        return null;
      }
      const errorText = await response.text();
      throw new Error(errorText || "Error with POST request");
    }

    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error("API POST Error:", error);
    Alert.alert("Error", error.message || "Something went wrong");
    throw error;
  }
};

export { apiGet, apiPost };