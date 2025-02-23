import { Alert } from 'react-native';
import { getApiBaseUrl } from '@/config/config';

const apiGet = async (endpoint: string) => {
  try {
    const API_BASE_URL = await getApiBaseUrl(); // Fetch the correct API URL dynamically
    console.log(`GET Request to: ${API_BASE_URL}${endpoint}`);

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'Error with GET request');
    }

    return await response.json();
  } catch (error: any) {
    console.error('API GET Error:', error);
    Alert.alert('Error', error.message || 'Something went wrong');
    throw error;
  }
};

const apiPost = async (endpoint: string, body: object) => {
  try {
    const API_BASE_URL = await getApiBaseUrl(); // Fetch the correct API URL dynamically
    console.log(`POST Request to: ${API_BASE_URL}${endpoint}`);

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(body),
    });

    console.log(response);
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'Error with POST request');
    }

    return await response.json();
  } catch (error: any) {
    console.error('API POST Error:', error);
    Alert.alert('Error', error.message || 'Something went wrong');
    throw error;
  }
};

export { apiGet, apiPost };
