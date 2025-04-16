//export const API_BASE_URL = "http://10.186.35.227:3020"; //CHANGE THIS EACH TIME YOOU MOVE
//This is an IPV4 address

import Constants from "expo-constants";
import { Platform } from "react-native";

let apiBaseUrl = "http://localhost:3020"; // fallback

if (Platform.OS !== "web") {
  const debuggerHost = Constants.expoConfig?.hostUri ?? "";
  const [host] = debuggerHost.split(":");
  apiBaseUrl = `http://${host}:3020`;
}

export const API_BASE_URL = apiBaseUrl;
