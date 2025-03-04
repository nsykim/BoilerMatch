import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AuthScreen from '@/screens/Auth/AuthScreen';
import Preferences from '@/screens/Auth/Preferences';
import UserInfo from '@/screens/Auth/UserInfo';


const Stack = createNativeStackNavigator();

const AuthStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Auth" component={AuthScreen} />
      <Stack.Screen name="UserInfo" component={UserInfo} />
      <Stack.Screen name="Preferences" component={Preferences} />
    </Stack.Navigator>
  );
};

export default AuthStack;
