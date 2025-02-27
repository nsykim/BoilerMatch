import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import AppNavigator from './navigation/AppNavigator';
import SwipeScreen from './screens/Home/SwipeScreen';
import AuthScreen from './screens/Auth/AuthScreen';
import Preferences from './screens/Auth/Preferences';
import UserInfo from './screens/Auth/UserInfo';

const App = () => {
  return (
    <AuthProvider>
      <UserInfo />
    </AuthProvider>
  );
};

export default App;
