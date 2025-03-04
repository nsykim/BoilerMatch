import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

type AuthContextType = {
  email: string | null;
  token: string | null;
  isAuthenticated: boolean;
  setEmail: (email: string | null) => void;
  setToken: (token: string | null) => void;
  clearEmail: () => void;
  clearToken: () => void;
};

export const AuthContext = createContext<AuthContextType>({
  email: null,
  token: null,
  isAuthenticated: false,
  setEmail: () => {},
  setToken: () => {},
  clearEmail: () => {},
  clearToken: () => {},
});

type AuthProviderProps = { children: ReactNode };

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [email, setEmail] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const isAuthenticated = !!token;

  useEffect(() => {
    const loadStoredData = async () => {
      try {
        const storedEmail = await AsyncStorage.getItem("email");
        const storedToken = await AsyncStorage.getItem("session_token");
        
        if (storedEmail) {
          setEmail(storedEmail);
        }
        if (storedToken) {
          setToken(storedToken);
        }
      } catch (error) {
        console.error("Failed to load stored data:", error);
      }
    };
    
    loadStoredData();
  }, []);

  const clearEmail = async () => {
    setEmail(null);
    await AsyncStorage.removeItem('email');
  };

  const clearToken = async () => {
    setToken(null);
    await AsyncStorage.removeItem('session_token');
  };

  return (
    <AuthContext.Provider value={{ email, token, isAuthenticated, setEmail, setToken, clearEmail, clearToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
