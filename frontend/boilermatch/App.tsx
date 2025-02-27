import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import AppNavigator from './navigation/AppNavigator';
import AuthScreen from './screens/Auth/AuthScreen';
import Preferences from './screens/Auth/Preferences';

const App = () => {
  return (
    <AuthProvider>
      <UserInfo />
    </AuthProvider>
  );
};

export default App;
