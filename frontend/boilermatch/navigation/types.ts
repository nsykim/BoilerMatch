export type RootStackParamList = {
  Auth: undefined;
  Preferences: undefined;
  MainTabNavigator: undefined;
  Chat: undefined;
  Settings: undefined;
  UserInfo: { is_new_user ?: boolean };
  UserInfoRegister: undefined; // ✅ Add this line
};
