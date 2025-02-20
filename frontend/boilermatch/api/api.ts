import { Alert } from 'react-native';
import { API_BASE_URL } from '@/config/config';

const apiGet = async (endpoint: string) => {
  try {
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

    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('API GET Error:', error);
    Alert.alert('Error', error.message || 'Something went wrong');
    throw error;
  }
};

const apiPost = async (endpoint: string, body: object) => {
  try {
    console.log(`${API_BASE_URL}${endpoint}`)
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(body),
    });
    console.log(response)
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'Error with POST request');
    }

    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('API POST Error:', error);
    Alert.alert('Error', error.message || 'Something went wrong');
    throw error;
  }
};

export { apiGet, apiPost };
